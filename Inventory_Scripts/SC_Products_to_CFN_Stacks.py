#!/usr/bin/env python3

import Inventory_Modules
from Inventory_Modules import display_results
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from colorama import init, Fore
from time import time
from threading import Thread
from queue import Queue
from tqdm.auto import tqdm
from botocore.exceptions import ClientError, ProfileNotFound, UnknownRegionError, UnknownCredentialError
import logging
import sys

init()
__version__ = "2023.08.09"

parser = CommonArguments()
parser.singleprofile()
parser.singleregion()
parser.extendedargs()
parser.save_to_file()
parser.verbosity()
parser.timing()
parser.version(__version__)
parser.my_parser.add_argument(
	"+d", "+delete",
	dest="DeletionRun",
	action="store_true",
	help="This will delete the SC Provisioned Products found to be in error, or without active CloudFormation stacks - without any opportunity to confirm. Be careful!!")
parser.my_parser.add_argument(
	"-f", "--fragment",
	dest="Fragment",
	metavar="Fragment of the Product name or the product id",
	default=None,
	help="Unique fragment of the product name or the product id")
parser.my_parser.add_argument(
	"-e", "--exact",
	dest="Exact",
	action="store_true",
	help="Use this flag to make sure that ONLY the string you specified will be identified")
args = parser.my_parser.parse_args()

pProfile = args.Profile
pRegion = args.Region
pTiming = args.Time
pFileName = args.Filename
pFragment = args.Fragment
pExact = args.Exact
verbose = args.loglevel
DeletionRun = args.DeletionRun
# Setup logging levels
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)


##########################


def sort_by_email(elem):
	return elem('AccountEmail')


def find_account_stacksets(faws_acct, f_SCProducts, fRegion=None, fstacksetname=None):
	"""
	Note that this function takes a list of Credentials and checks for stacks in every account it has creds for
	"""

	class CheckProducts(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_sc_product, c_region, c_fstacksetname, c_PlacesToLook, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for SC Product: {c_sc_product['SCPName']}")
				logging.info(f"{Fore.RED}Checking {PlaceCount} of {len(f_SCProducts)} products{Fore.RESET}")
				CFNresponse = Inventory_Modules.find_stacks3(faws_acct, pRegion, c_sc_product['SCPId'])
				logging.info(f"There are {len(CFNresponse)} matches for SC Provisioned Product Name {c_sc_product['SCPName']}")
				try:
					if len(CFNresponse) > 0:
						stack_info = client_cfn.describe_stacks(
							StackName=CFNresponse[0]['StackName']
						)
						# The above command fails if the stack found (by the find_stacks3 function) has been deleted
						# The following section determines the NEW Account's AccountEmail and AccountID
						AccountEmail = AccountID = AccountStatus = None
						if 'Parameters' in stack_info['Stacks'][0].keys() and len(stack_info['Stacks'][0]['Parameters']) > 0:
							for y in range(len(stack_info['Stacks'][0]['Parameters'])):
								if stack_info['Stacks'][0]['Parameters'][y]['ParameterKey'] == 'AccountEmail':
									AccountEmail = stack_info['Stacks'][0]['Parameters'][y]['ParameterValue']
									logging.info(f"Account Email is {AccountEmail}")
						if 'Outputs' in stack_info['Stacks'][0].keys():
							for y in range(len(stack_info['Stacks'][0]['Outputs'])):
								logging.info(f"Output Key {stack_info['Stacks'][0]['Outputs'][y]['OutputKey']} "
								             f"for stack {CFNresponse[0]['StackName']} is {stack_info['Stacks'][0]['Outputs'][y]['OutputValue']}")
								if stack_info['Stacks'][0]['Outputs'][y]['OutputKey'] == 'AccountID':
									AccountID = stack_info['Stacks'][0]['Outputs'][y]['OutputValue']
									if AccountID in AccountHistogram.keys():
										AccountStatus = AccountHistogram[AccountID]
									else:
										AccountStatus = 'Closed'
									logging.info(f"{Fore.RED}Found the Account ID: {AccountID}{Fore.RESET}")
									if AccountID in SuspendedAccounts:
										logging.error(f"{Fore.RED}Account ID {AccountID} has been suspended{Fore.RESET}")
									break
								else:
									logging.error("Outputs key present, but no account ID")
									AccountID = None
									AccountStatus = None
						else:
							logging.error("No Outputs key present")
							AccountID = 'None'
							AccountStatus = 'None'
						CFNStackName = CFNresponse[0]['StackName']
						CFNStackStatus = CFNresponse[0]['StackStatus']
					# AccountEmail should have been assigned in the 'Parameters' if-then above
					# AccountID should have been assigned in the 'Outputs' if-then above
					# AccountStatus should have been assigned in the 'Outputs' if-then above
					else:  # This takes effect when CFNResponse can't find any stacks with the Service Catalog Product ID
						CFNStackName = CFNStackStatus = AccountID = AccountEmail = AccountStatus = None
					logging.error(f"AccountID: {AccountID} | AccountEmail: {AccountEmail} | CFNStackName: {CFNStackName} | CFNStackStatus: {CFNStackStatus} | SC Product: {c_sc_product['SCPName']}")
					SCP2Stacks.append({
						'SCProductName'           : c_sc_product['SCPName'],
						'SCProductId'             : c_sc_product['SCPId'],
						'SCStatus'                : c_sc_product['SCPStatus'],
						'ProvisioningArtifactName': c_sc_product['ProvisioningArtifactName'],
						'CFNStackName'            : CFNStackName,
						'CFNStackStatus'          : CFNStackStatus,
						'AccountEmail'            : AccountEmail,
						'AccountID'               : AccountID,
						'AccountStatus'           : AccountStatus
					})
				except ClientError as my_Error:
					if str(my_Error).find("ValidationError") > 0:
						print("Validation Failure ")
						print(f"Validation Failure in profile {pProfile} looking for stack {CFNresponse[0]['StackName']} with status of {CFNresponse[0]['StackStatus']}")
					elif str(my_Error).find("AccessDenied") > 0:
						print(f"{pProfile}: Access Denied Failure ")
					else:
						print(f"{pProfile}: Other kind of failure ")
						print(my_Error)
				finally:
					logging.info(f"Finished finding product {c_sc_product['SCPName']} - {c_PlaceCount} / {c_PlacesToLook}")
					pbar.update()
					self.queue.task_done()

	if fRegion is None:
		fRegion = ['us-east-1']
	checkqueue = Queue()

	# AllSubnets = []
	PlaceCount = 0
	PlacesToLook = WorkerThreads = min(len(f_SCProducts), 10)

	pbar = tqdm(desc=f'Reconciling SC Products with CloudFormation Stacks in accounts',
	            leave=True,
	            total=len(f_SCProducts), unit=' products')

	# Create and start the worker threads
	for x in range(WorkerThreads):
		worker = CheckProducts(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for SCProduct in SCProducts:
		logging.info(f"Checking service catalog product: {SCProduct['SCPName']}")
		try:
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			checkqueue.put((SCProduct, fRegion, fstacksetname, PlacesToLook, PlaceCount))
			PlaceCount += 1
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {faws_acct.acct_number} in {fRegion} region")
				logging.warning(f"It's possible that the region {fRegion} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return SCP2Stacks


##########################


'''
TODO: 
- Need to add a parameter that allows the user to close / terminate the SC products for only the closed / suspended accounts (very safe)
- Add a parameter that refuses to close/ terminate accounts with active VPCs?
'''

'''
Significant Variable Explanation:
	'AcctList' holds a list of accounts within this Org.
	'SCresponse' holds a native list of Service Catalog Provisioned Products supplied by the native API.  
	'SCProducts' holds a refined list of the Service Catalog Provisioned Products from the 'SCresponse' list, but only the fields we're interested in. 
	** TODO: I duplicated this listing, in case later I decided to add some additional useful fields to the dict. 
	'SCP2Stacks' holds a list of the CloudFormation Stacks in this account that *match* the Provisioned Products.
	** TODO: This list should hold *all* stacks and then we could find stacks for accounts that no longer exist.
	'AccountHistogram' holds the list of accounts (the account numbers are the keys in this dict) and the number of SC products that are created for this account is the value of that key.
'''
begin_time = time()

ERASE_LINE = '\x1b[2K'

print()

SCP2Stacks = []
SCProducts = []
try:
	if pProfile is None:
		aws_acct = aws_acct_access()
	else:
		aws_acct = aws_acct_access(fProfile=pProfile, fRegion=pRegion)
	if aws_acct.ErrorType is not None and aws_acct.ErrorType.lower() == 'invalid region':
		raise UnknownRegionError(region_name=pRegion, error_msg=aws_acct.ErrorType)
	session_aws = aws_acct.session
except UnknownCredentialError as my_Error:
	print(f"Single profile '{pProfile}' doesn't seem to exist, or work. Please check your credentials-1.\n"
	      f"Error Message: {my_Error}")
	print()
	sys.exit(1)
except ProfileNotFound as my_Error:
	print(f"Single profile '{pProfile}' doesn't seem to exist, or work. Please check your credentials-1.\n"
	      f"Error Message: {my_Error}")
	print()
	sys.exit(1)
except AttributeError as my_Error:
	print(f"Single profile '{pProfile}' doesn't seem to exist, or work. Please check your credentials-2.\n"
	      f"Error Message: {my_Error}")
	print()
	sys.exit(1)
except (ConnectionError, UnknownRegionError) as my_Error:
	print(f"There is no single region '{pRegion}'. Please re-run and specify a valid AWS region for this Org account.\n"
	      f"Error Message: {my_Error}")
	print()
	sys.exit(1)
client_org = aws_acct.session.client('organizations')
client_cfn = aws_acct.session.client('cloudformation')

AccountHistogram = {}
SuspendedAccounts = []
ClosedAccts = []
def main():
	client_sc = aws_acct.session.client('servicecatalog')
	ErroredSCProductExists = False
	# Creates AccountHistogram which tracks which accounts have SC Products built for them, and which do not.
	# The Histogram is initialized with ALL accounts and their status.
	# It's then later overwritten with the count of how many SC Products relate to that account.
	# So the accounts which only have a status as their value - are missing the SC Product
	for account in aws_acct.ChildAccounts:
		AccountHistogram[account['AccountId']] = account['AccountStatus']
		if account['AccountStatus'] == 'SUSPENDED':
			SuspendedAccounts.append(account['AccountId'])

	# Find the provisioned product ids
	AVM_prod_id = None
	if pFragment is None:
		result = client_sc.search_products_as_admin()
		prod_ids = result['ProductViewDetails']
		# while 'NextPageToken' in result.keys() and 'NextPageToken' is not None:
		# 	result = client_sc.search_products_as_admin()
		# 	prod_ids.extend(result['ProductViewDetails'])
		# 	if verbose < 50:
		# 		print(f"{ERASE_LINE}Found {len(result['ProductViewDetails'])} products | Total found: {len(prod_ids)}", end='\r')
		# print()
		for product in prod_ids:
			if product['ProductViewSummary']['Name'].find('Account-Vending-Machine') > 0:
				AVM_prod_id = product['ProductViewSummary']['ProductId']
	elif pFragment is not None and not pExact:
		result = client_sc.search_products_as_admin()
		prod_ids = result['ProductViewDetails']
		# while 'NextPageToken' in result.keys() and 'NextPageToken' is not None:
		# 	result = client_sc.search_products_as_admin()
		# 	prod_ids.extend(result['ProductViewDetails'])
		# 	if verbose < 50:
		# 		print(f"{ERASE_LINE}Found {len(result['ProductViewDetails'])} products | Total found: {len(prod_ids)}", end='\r')
		for product in prod_ids:
			if product['ProductViewSummary']['Name'].find(pFragment) > -1 or product['ProductViewSummary']['ProductId'].find(pFragment) > -1:
				AVM_prod_id = product['ProductViewSummary']['ProductId']
	elif pFragment is not None and pExact:
		AVM_prod_id = pFragment

	# Finds Service Catalog Products and reconciles them to the account they belong to
	try:
		# The function below takes the parent account (object),
		# the stack statuses we're trying to find, the number of products to find at once, and possibly the product id (if provided)
		SCresponse = Inventory_Modules.find_sc_products3(aws_acct, "All", 10, AVM_prod_id)
		logging.warning("A list of the SC Products found:")
		for i in range(len(SCresponse)):
			logging.warning(f"SC Product Name {SCresponse[i]['Name']} | SC Product Status {SCresponse[i]['Status']}")
			SCProducts.append({
				'SCPName'                 : SCresponse[i]['Name'],
				'SCPId'                   : SCresponse[i]['Id'],
				'SCPStatus'               : SCresponse[i]['Status'],
				'SCPRecordId'             : SCresponse[i]['LastRecordId'],
				'ProvisioningArtifactName': SCresponse[i]['ProvisioningArtifactName']
			})
			if SCresponse[i]['Status'] == 'ERROR' or SCresponse[i]['Status'] == 'TAINTED':
				ErroredSCProductExists = True

		CFNStacks = Inventory_Modules.find_stacks3(aws_acct, pRegion, f"SC-{aws_acct.acct_number}")

		if pTiming:
			print(f"{Fore.GREEN}Finding stacks in your account has taken {time() - begin_time:.2f} seconds now...{Fore.RESET}")
			milestone1 = time()

		SCresponse = None

		# TODO: Create a queue - place the SCProducts on that queue, one by one, and let this code run in a multi-thread worker
		# def find_account_stacksets(faws_acct, f_SCProducts, fRegion=None, fstacksetname=None):
		CFNresponse = find_account_stacksets(aws_acct, SCProducts, pRegion, pFragment)

		# TODO: We should list out Suspended accounts in the SCP2Stacks readout at the end - in case any accounts have
		#  both a provisioned product, but are also suspended.
		# Do any of the account numbers show up more than once in this list?
		# We initialize the listing from the full list of accounts in the Org.

		if pTiming:
			print(f"{Fore.GREEN}Reconciling products to the CloudFormation stacks took {time() - milestone1:.2f} seconds{Fore.RESET}")

		# TODO: This might not be a good idea, if it misses the stacks which are associated with accounts no longer within the Org.
		# We add a one to each account which is represented within the Stacks listing. This allows us to catch duplicates
		# and also accounts which do not have a stack associated.
		# Note it does *not* help us catch stacks associated with an account that's been removed.
		for i in range(len(CFNresponse)):
			if CFNresponse[i]['AccountID'] == 'None':
				continue
			elif not CFNresponse[i]['AccountID'] in AccountHistogram.keys():
				CFNresponse[i]['AccountStatus'] = 'CLOSED'
				ClosedAccts.append(CFNresponse[i]['AccountID'])
			else:
				# This means that the value is still either "ACTIVE" or "SUSPENDED"
				if isinstance(AccountHistogram[CFNresponse[i]['AccountID']], str):
					AccountHistogram[CFNresponse[i]['AccountID']] = 1
				else:
					AccountHistogram[CFNresponse[i]['AccountID']] += 1

		display_dict = {'AccountID'               : {'DisplayOrder': 1, 'Heading': 'Account Id', 'Condition': ['None']},
		                'SCProductName'           : {'DisplayOrder': 2, 'Heading': 'SC Product Name'},
		                'ProvisioningArtifactName': {'DisplayOrder': 3, 'Heading': 'Version'},
		                'CFNStackName'            : {'DisplayOrder': 4, 'Heading': 'CFN Stack Name'},
		                'SCStatus'                : {'DisplayOrder': 5, 'Heading': 'SC Status', 'Condition': ['ERROR', 'TAINTED']},
		                'CFNStackStatus'          : {'DisplayOrder': 6, 'Heading': 'CFN Stack Status'},
		                'AccountStatus'           : {'DisplayOrder': 7, 'Heading': 'Account Status', 'Condition': ['CLOSED']},
		                'AccountEmail'            : {'DisplayOrder': 8, 'Heading': 'Account Email'}}
		display_results(CFNresponse, display_dict, 'None', pFileName)

	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			print(f"{pProfile}: Authorization Failure ")
		elif str(my_Error).find("AccessDenied") > 0:
			print(f"{pProfile}: Access Denied Failure ")
		else:
			print(f"{pProfile}: Other kind of failure ")
			print(my_Error)

	print()
	for acctnum in AccountHistogram.keys():
		if AccountHistogram[acctnum] == 1:
			pass  # This is the desired state, so no user output is needed.
		elif AccountHistogram[acctnum] == 'SUSPENDED':
			print(f"{Fore.RED}While there is no SC Product associated, account number {acctnum} appears to be a suspended account.{Fore.RESET}")
		elif AccountHistogram[acctnum] == 'ACTIVE':  # This compare needs to be separate from below, since we can't compare a string with a "<" operator
			print(f"Account Number {Fore.RED}{acctnum}{Fore.RESET} appears to have no SC Product associated with it. This can be a problem")
		elif AccountHistogram[acctnum] < 1:
			print(f"Account Number {Fore.RED}{acctnum}{Fore.RESET} appears to have no SC Product associated with it. This can be a problem")
		elif AccountHistogram[acctnum] > 1:
			print(f"Account Number {Fore.RED}{acctnum}{Fore.RESET} appears to have multiple SC Products associated with it. This can be a problem")

	if ErroredSCProductExists:
		print()
		print("You probably want to remove the following SC Products:")
		session_sc = aws_acct.session
		client_sc = session_sc.client('servicecatalog')
		for i in range(len(CFNresponse)):
			if ((CFNresponse[i]['SCStatus'] == 'ERROR') or (CFNresponse[i]['CFNStackName'] == 'None')) and not DeletionRun:
				print(f"aws servicecatalog terminate-provisioned-product --provisioned-product-id {CFNresponse[i]['SCProductId']} --ignore-errors", end='')
				# Finishes the line for display, based on whether they used a profile or not to run this command
				if pProfile is None:
					print()
				elif pProfile is not None:
					print(f" --profile {pProfile}")
			elif ((CFNresponse[i]['SCStatus'] == 'ERROR') or (CFNresponse[i]['CFNStackName'] == 'None')) and DeletionRun:
				print(f"Deleting Service Catalog Provisioned Product {CFNresponse[i]['SCProductName']} from account {aws_acct.acct_number}")
				StackDelete = client_sc.terminate_provisioned_product(
					ProvisionedProductId=CFNresponse[i]['SCProductId'],
					IgnoreErrors=True,
				)
				logging.error("Result of Deletion: %s", StackDelete['RecordDetail']['Status'])
				if len(StackDelete['RecordDetail']['RecordErrors']) > 0:
					logging.error("Error code: %s", StackDelete['RecordDetail']['RecordErrors'][0]['Code'])
					logging.error("Error description: %s", StackDelete['RecordDetail']['RecordErrors'][0]['Description'])

	print()
	for i in AccountHistogram:
		logging.info(f"There are {AccountHistogram[i] if isinstance(AccountHistogram[i], int) else '0'} active SC products for Account ID: {i}")
	end_time = time()
	duration = end_time - begin_time
	if pTiming:
		print(f"{Fore.GREEN}This script took {duration:.2f} seconds{Fore.RESET}")
	print(f"We found {len(aws_acct.ChildAccounts)} accounts within the Org")
	print(f"We found {len(SCProducts)} Service Catalog Products")
	print(f"We found {len(SuspendedAccounts)} Suspended accounts")
	print(f"We found {len(ClosedAccts)} Closed Accounts that still have an SC product")
	# print("We found {} Service Catalog Products with no account attached".format('Some Number'))
	print("Thanks for using this script...")
	print()

if __name__ == '__main__':
	main()
