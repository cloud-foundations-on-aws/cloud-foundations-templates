#!/usr/bin/env python3
import sys
from os.path import split
import Inventory_Modules
from time import time
from Inventory_Modules import display_results, get_all_credentials
from pprint import pprint
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
from colorama import init, Fore
from botocore.exceptions import ClientError
import logging

init()

__version__ = '2024.05.31'

###########################


def parse_args(f_arguments):
	"""
	Description: Parses the arguments passed into the script
	@param f_arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()  # Allows for a single profile to be specified
	parser.multiregion()  # Allows for multiple regions to be specified at the command line
	parser.extendedargs()  # Allows for extended arguments like which accounts to skip, and whether Force is enabled.
	parser.rootOnly()
	# TODO: Add parameter for access_roles
	#  parser.rolestouse()  # Allows for the roles to be specified at the command line.
	parser.fragment()
	parser.timing()
	parser.verbosity()  # Allows for the verbosity to be handled.
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-s", "--status",
		dest="status",
		nargs='*',
		choices=['CREATE_IN_PROGRESS', 'CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS',
		         'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_IN_PROGRESS', 'DELETE_FAILED', 'DELETE_COMPLETE',
		         'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_COMPLETE', 'UPDATE_FAILED',
		         'UPDATE_ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
		         'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS', 'IMPORT_IN_PROGRESS', 'IMPORT_COMPLETE',
		         'IMPORT_ROLLBACK_IN_PROGRESS', 'IMPORT_ROLLBACK_FAILED', 'IMPORT_ROLLBACK_COMPLETE', 'all', 'All', 'ALL'],
		metavar="CloudFormation status",
		default=None,
		help="List of statuses that determines which statuses we see. Default is all ACTIVE statuses. 'All' will capture all statuses")
	local.add_argument(
		"--stackid",
		dest="stackid",
		action="store_true",
		help="Flag that determines whether we display the Stack IDs as well")
	local.add_argument(
		"+delete", "+forreal",
		dest="DeletionRun",
		action="store_true",
		help="This will delete the stacks found - without any opportunity to confirm. Be careful!!")
	return parser.my_parser.parse_args(f_arguments)


def setup_auth_accounts_and_regions(fProfile: str, fRegionList:list=None, fAccountList:list=None, fSkipAccounts:list=None, fStackFrag:list=None, fExact:bool=False, fDeletionRun:bool=False) -> (aws_acct_access, list, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@return:
		- an object of the type "aws_acct_access"
		- a list of accounts found for this particular profile.
		- a list of regions valid for this particular profile/ account.
	"""
	try:
		aws_acct = aws_acct_access(fProfile)
	except ConnectionError as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	ChildAccounts = aws_acct.ChildAccounts
	RegionList = Inventory_Modules.get_regions3(aws_acct, fRegionList)

	ChildAccounts = Inventory_Modules.RemoveCoreAccounts(ChildAccounts, fSkipAccounts)
	if fAccountList is None:
		AccountList = [account['AccountId'] for account in ChildAccounts]
	else:
		AccountList = [account['AccountId'] for account in ChildAccounts if account['AccountId'] in fAccountList]

	print(f"You asked to find stacks with this fragment {Fore.RED}'{fStackFrag}'{Fore.RESET}")
	print(f"in these accounts:\n{Fore.RED}{AccountList}{Fore.RESET}")
	print(f"in these regions:\n{Fore.RED}{RegionList}{Fore.RESET}")
	print(f"While skipping these accounts:\n{Fore.RED}{fSkipAccounts}{Fore.RESET}") if fSkipAccounts is not None else ''
	if fDeletionRun:
		print()
		print("And delete the stacks that are found...")

	if fExact:
		print(f"\t\tFor stacks that {Fore.RED}exactly match{Fore.RESET} these fragments: {fStackFrag}")
	else:
		print(f"\t\tFor stacks that contains these fragments: {fStackFrag}")

	return aws_acct, AccountList, RegionList


def collect_cfnstacks(fCredentialList: list) -> list:
	"""
	Description: This function will collect all the CloudFormation stacks for the accounts and regions specified.
	@param fCredentialList: A list of objects of the type "aws_acct_access"
	@return: A list of all the CloudFormation stacks found.
	"""
	from queue import Queue
	from threading import Thread
	StacksFound = []

	def worker(q, pStackfrag, pstatus):
		while True:
			credential = q.get()
			if credential is None:
				break

			Stacks = False
			if credential['Success']:
				try:
					Stacks = Inventory_Modules.find_stacks2(credential, credential['Region'], pStackfrag, pstatus)
					logging.warning(f"Account: {credential['AccountId']} | Region: {credential['Region']} | Found {len(Stacks)} Stacks")
					print(f"{ERASE_LINE}{Fore.RED}Account: {credential['AccountId']} Region: {credential['Region']} Found {len(Stacks)} Stacks{Fore.RESET}", end='\r')
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						print(f"{credential['AccountId']}: Authorization Failure")
			else:
				continue

			if Stacks and len(Stacks) > 0:
				for y in range(len(Stacks)):
					StackName = Stacks[y]['StackName']
					StackStatus = Stacks[y]['StackStatus']
					StackID = Stacks[y]['StackId']
					StackCreate = Stacks[y]['CreationTime']
					StacksFound.append({
						'Account'        : credential['AccountId'],
						'Region'         : credential['Region'],
						'AccessKeyId'    : credential['AccessKeyId'],
						'SecretAccessKey': credential['SecretAccessKey'],
						'SessionToken'   : credential['SessionToken'],
						'AccountNumber'  : credential['AccountNumber'],
						'StackName'      : StackName,
						'StackCreate'    : StackCreate.strftime("%Y-%m-%d"),
						'StackStatus'    : StackStatus,
						'StackArn'       : StackID if pStackIdFlag else 'None'})

			q.task_done()

	stacks_queue = Queue()
	for credential in fCredentialList:
		stacks_queue.put(credential)

	num_threads = 4  # Number of worker threads
	for i in range(num_threads):
		t = Thread(target=worker, args=(stacks_queue, pStackfrag, pstatus))
		t.start()

	stacks_queue.join()

	for i in range(num_threads):
		stacks_queue.put(None)

	sortedStacksFound = sorted(StacksFound, key=lambda x: (x['Account'], x['Region'], x['StackName']))
	return sortedStacksFound


def display_stacks(fAllStacks: list):
	display_dict = {'Account'    : {'DisplayOrder': 1, 'Heading': 'Account'},
	                'Region'     : {'DisplayOrder': 2, 'Heading': 'Region'},
	                'StackStatus': {'DisplayOrder': 3, 'Heading': 'Stack Status'},
	                'StackCreate': {'DisplayOrder': 4, 'Heading': 'Create Date'},
	                'StackName'  : {'DisplayOrder': 5, 'Heading': 'Stack Name'},
	                'StackArn'   : {'DisplayOrder': 6, 'Heading': 'Stack ID'}}

	display_results(fAllStacks, display_dict, None, )
	print(ERASE_LINE)
	print(f"{Fore.RED}Found {len(fAllStacks)} stacks across {len(AccountList)} accounts across {len(RegionList)} regions{Fore.RESET}")
	print()
	if args.loglevel < 21:  # INFO level
		lAccounts = lRegions = lAccountsAndRegions = []
		for i in range(len(fAllStacks)):
			lAccounts.append(fAllStacks[i]['Account'])
			lRegions.append(fAllStacks[i]['Region'])
			lAccountsAndRegions.append((fAllStacks[i]['Account'], fAllStacks[i]['Region']))
		print("The list of accounts and regions:")
		pprint(list(sorted(set(lAccountsAndRegions))))


def modify_stacks(fStacksFound: list):
	"""
	Description: If "DeletionRun" was chosen, this function will delete the requested stacks
	@param fStacksFound: A list of dicts, containing the stack-names, credentials, and meta data
	@return: The response will be the response from the deletion runs... as little as that may be.
	"""
	ReallyDelete = (input(f"Deletion of stacks has been requested, are you still sure? (y/n): ") in ['y', 'Y']) if DeletionRun else False
	response2 = []
	if DeletionRun and ReallyDelete and ('GuardDuty' in pStackfrag or 'guardduty' in pStackfrag):
		logging.warning(f"Deleting {len(fStacksFound)} stacks")
		for stack_found in fStacksFound:
			print(f"Deleting stack {stack_found['StackName']} from Account {stack_found['Account']} in region {stack_found['Region']}")
			if stack_found['StackStatus'] == 'DELETE_FAILED':
				# This deletion generally fails because the Master Detector doesn't properly delete (and it's usually already deleted due to some other script) - so we just need to delete the stack anyway - and ignore the actual resource.
				response = Inventory_Modules.delete_stack2(stack_found, stack_found['Region'], stack_found['StackName'], RetainResources=True, ResourcesToRetain=["MasterDetector"])
			else:
				response = Inventory_Modules.delete_stack2(stack_found, stack_found['Region'], stack_found['StackName'])
			response2.append(response)
	elif DeletionRun and ReallyDelete:
		logging.warning(f"Deleting {len(fStacksFound)} stacks")
		for stack_found in fStacksFound:
			print(f"Deleting stack {stack_found['StackName']} from account {stack_found['Account']} in region {stack_found['Region']} with status: {stack_found['StackStatus']}")
			# print(f"Finished {y + 1} of {len(fStacksFound)}")
			response = Inventory_Modules.delete_stack2(stack_found, stack_found['Region'], stack_found['StackName'])
			response2.append(response)
	# pprint(response)
	return response2


###########################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfile = args.Profile
	pRegionList = args.Regions
	pStackfrag = args.Fragments
	pExact = args.Exact
	pTiming = args.Time
	verbose = args.loglevel
	pSkipProfiles = args.SkipProfiles
	pSkipAccounts = args.SkipAccounts
	pRootOnly = args.RootOnly
	pAccountList = args.Accounts
	pstatus = args.status
	pStackIdFlag = args.stackid
	DeletionRun = args.DeletionRun
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)

	begin_time = time()

	##########################
	ERASE_LINE = '\x1b[2K'

	print()
	# Setup the aws_acct object
	aws_acct, AccountList, RegionList = setup_auth_accounts_and_regions(pProfile,  pRegionList, pAccountList, pSkipAccounts, pStackfrag, pExact, DeletionRun)
	# Get credentials for all Child Accounts
	CredentialList = get_all_credentials(pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, AccountList, RegionList)
	# Collect the stacksets, AccountList and RegionList involved
	AllStacks = collect_cfnstacks(CredentialList)
	# Display the information we've found this far
	display_stacks(AllStacks)
	# Modify stacks, if requested
	if DeletionRun:
		modify_result = modify_stacks(AllStacks)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

	print()
	print("Thanks for using this script...")
	print()
