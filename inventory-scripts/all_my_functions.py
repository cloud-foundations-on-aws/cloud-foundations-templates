#!/usr/bin/env python3
import boto3

import Inventory_Modules
from Inventory_Modules import get_all_credentials, display_results
from colorama import init, Fore
from botocore.exceptions import ClientError
from ArgumentsClass import CommonArguments
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import time
import sys
from os.path import split

import logging

init()
__version__ = "2024.06.05"

ERASE_LINE = '\x1b[2K'
begin_time = time()


# TODO: Need a table at the bottom that creates a summary of the runtimes used, so that action can be taken if older runtimes are in use.


##################
# Functions
##################
def parse_args(args):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()  # Allows for a single profile to be specified
	parser.multiregion()  # Allows for multiple regions to be specified at the command line
	parser.fragment()  # Allows for specifying a string fragment to be looked for
	parser.extendedargs()
	parser.rootOnly()
	parser.save_to_file()
	parser.timing()
	parser.rolestouse()
	parser.fix()
	parser.deletion()
	parser.verbosity()  # Allows for the verbosity to be handled.
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--runtime", "--run", "--rt",
		dest="Runtime",
		nargs="*",
		metavar="language and version",
		default=None,
		help="Language runtime(s) you're looking for within your accounts")
	local.add_argument(
		"--new_runtime", "--new", "--new-runtime",
		dest="NewRuntime",
		metavar="language and version",
		default=None,
		help="Language runtime(s) you will replace what you've found with... ")
	return parser.my_parser.parse_args(args)


def left(s, amount):
	return s[:amount]


def right(s, amount):
	return s[-amount:]


def mid(s, offset, amount):
	return s[offset - 1:offset + amount - 1]


def fix_runtime(CredentialList, new_runtime):
	from time import sleep

	class UpdateRuntime(Thread):
		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				c_account_credentials, c_function_name, c_new_runtime = self.queue.get()
				Updated_Function = {}
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				Success = False
				try:
					logging.info(f"Attempting to update {c_function_name} to {c_new_runtime}")
					session = boto3.Session(aws_access_key_id=c_account_credentials['AccessKeyId'],
					                        aws_secret_access_key=c_account_credentials['SecretAccessKey'],
					                        aws_session_token=c_account_credentials['SessionToken'],
					                        region_name=c_account_credentials['Region'])
					client = session.client('lambda')
					logging.info(f"Updating function {c_function_name} to runtime {c_new_runtime}")
					Updated_Function = client.update_function_configuration(FunctionName=c_function_name,
					                                                        Runtime=c_new_runtime)
					sleep(3)
					Success = client.get_function_configuration(FunctionName=c_function_name)['LastUpdateStatus'] == 'Successful'
					while not Success:
						Status = client.get_function_configuration(FunctionName=c_function_name)['LastUpdateStatus']
						Success = True if Status == 'Successful' else 'False'
						if Status == 'InProgress':
							sleep(3)
							logging.info(f"Sleeping to allow {c_function_name} to update to runtime {c_new_runtime}")
						elif Status == 'Failed':
							raise RuntimeError(f'Runtime update for {c_function_name} to {c_new_runtime} failed')
				except TypeError as my_Error:
					logging.info(f"Error: {my_Error}")
					continue
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"Account {c_account_credentials['AccountId']}: Authorization Failure")
					continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					continue
				finally:
					if Success:
						Updated_Function['MgmtAccount'] = c_account_credentials['MgmtAccount']
						Updated_Function['AccountId'] = c_account_credentials['AccountId']
						Updated_Function['Region'] = c_account_credentials['Region']
						Rolet = Updated_Function['Role']
						Updated_Function['Role'] = mid(Rolet, Rolet.find("/") + 2, len(Rolet))
						FixedFuncs.extend(Updated_Function)
					self.queue.task_done()

	FixedFuncs = []
	PlaceCount = 0
	PlacesToLook = len(CredentialList)
	WorkerThreads = min(len(CredentialList), 25)

	checkqueue = Queue()

	for x in range(WorkerThreads):
		worker = UpdateRuntime(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			print(f"{ERASE_LINE}Queuing function {credential['FunctionName']} in account {credential['AccountId']} in region {credential['Region']}", end='\r')
			checkqueue.put((credential, credential['FunctionName'], new_runtime))
			PlaceCount += 1
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.error(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return FixedFuncs


def check_accounts_for_functions(CredentialList, fFragments=None):
	"""
	Note that this function takes a list of Credentials and checks for functions in every account it has creds for
	"""

	class FindFunctions(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_fragment_list = self.queue.get()
				pbar.update()
				Functions = []
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					Functions = Inventory_Modules.find_lambda_functions2(c_account_credentials, c_account_credentials['Region'], c_fragment_list)
				except TypeError as my_Error:
					logging.info(f"Error: {my_Error}")
					continue
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"Account {c_account_credentials['AccountId']}: Authorization Failure")
					continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					continue
				finally:
					if len(Functions) > 0:
						for _ in range(len(Functions)):
							Functions[_]['MgmtAccount'] = c_account_credentials['MgmtAccount']
							Functions[_]['AccountId'] = c_account_credentials['AccountId']
							Functions[_]['Region'] = c_account_credentials['Region']
							Functions[_]['AccessKeyId'] = c_account_credentials['AccessKeyId']
							Functions[_]['SecretAccessKey'] = c_account_credentials['SecretAccessKey']
							Functions[_]['SessionToken'] = c_account_credentials['SessionToken']
							Rolet = Functions[_]['Role']
							Functions[_]['Role'] = mid(Rolet, Rolet.find("/") + 2, len(Rolet))
						AllFuncs.extend(Functions)
					self.queue.task_done()

	AllFuncs = []
	WorkerThreads = min(len(CredentialList), 25)

	checkqueue = Queue()

	pbar = tqdm(desc=f'Finding instances from {len(CredentialList)} accounts / regions',
	            total=len(CredentialList), unit=' locations'
	            )

	for x in range(WorkerThreads):
		worker = FindFunctions(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			logging.info(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {credential['Region']}", end='\r')
			checkqueue.put((credential, fFragments))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.error(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return AllFuncs


def collect_all_my_functions(AllCredentials, fFragments, fverbose=50):
	# Generate parameter descriptions
	"""
	@AllCredentials - This is a list of all the credentials we have to check
	@fFragments - This is a list of fragments we want to search for
	@fverbose - This is a level of verbosity
	"""
	AllFunctions = check_accounts_for_functions(AllCredentials, fFragments)
	sorted_AllFunctions = sorted(AllFunctions, key=lambda k: (k['MgmtAccount'], k['AccountId'], k['Region'], k['FunctionName']))
	if fverbose < 50:
		print(f"We found {len(AllFunctions)} functions in {len(AllCredentials)} places")
	return sorted_AllFunctions


def fix_my_functions(fAllFunctions, fRuntime, fNewRuntime, fForceDelete, fTiming):
	begin_fix_time = time()

	if fNewRuntime is None:
		print(f"You provided the parameter at the command line to *fix* errors found, but didn't supply a new runtime to use, so exiting now... ")
		sys.exit(8)
	elif not fForceDelete:
		print(f"You provided the parameter at the command line to *fix* errors found")
		ReallyDelete = (input("Having seen what will change, are you still sure? (y/n): ") in ['y', 'Y', 'Yes', 'yes'])
	elif fForceDelete:
		print(f"You provided the parameter at the command line to *fix* errors found, as well as FORCING this change to happen... ")
		ReallyDelete = True
	else:
		ReallyDelete = False

	if ReallyDelete:
		print(f"Updating Runtime for all functions found from {fRuntime} to {fNewRuntime}")
		return_response = fix_runtime(fAllFunctions, fNewRuntime)
	else:
		return_response = "No functions were remediated."

		if fTiming:
			print(ERASE_LINE)
			print(f"{Fore.GREEN}Fixing {len(return_response)} functions took {time() - begin_fix_time:.3f} seconds{Fore.RESET}")

	return return_response


##################
# Main
##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfiles = args.Profiles
	pRegionList = args.Regions
	pFragments = args.Fragments
	pAccounts = args.Accounts
	pFix = args.Fix
	pForceDelete = args.Force
	pSaveFilename = args.Filename
	pRuntime = args.Runtime
	pNewRuntime = args.NewRuntime
	if pFragments == ['all'] and pRuntime is not None:
		pFragments = []
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pRootOnly = args.RootOnly
	pRoleList = args.AccessRoles
	pTiming = args.Time
	pverbose = args.loglevel
	logging.basicConfig(level=pverbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

	display_dict = {'MgmtAccount' : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'   : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'      : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'FunctionName': {'DisplayOrder': 4, 'Heading': 'Function Name'},
	                'Role'        : {'DisplayOrder': 6, 'Heading': 'Role'}}
	if pRuntime is None and pFragments is None:
		display_dict.update({'Runtime': {'DisplayOrder': 5, 'Heading': 'Runtime'}})
	elif pRuntime is not None and pFragments is None:
		display_dict.update({'Runtime': {'DisplayOrder': 5, 'Heading': 'Runtime', 'Condition': pRuntime}})
	elif pRuntime is None and pFragments is not None:
		display_dict.update({'Runtime': {'DisplayOrder': 5, 'Heading': 'Runtime', 'Condition': pFragments}})
	elif pRuntime is not None and pFragments is not None:
		display_dict.update({'Runtime': {'DisplayOrder': 5, 'Heading': 'Runtime', 'Condition': pRuntime + pFragments}})

	print(f"Collecting credentials... ")

	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoleList)
	AccountNum = len(set([acct['AccountId'] for acct in CredentialList]))
	RegionNum = len(set([acct['Region'] for acct in CredentialList]))
	print()
	print(f"Looking through {AccountNum} accounts and {RegionNum} regions ")
	print()

	# Note that 'pFragments' is by default ['all'], so even if pRuntime is provided, we still look for everything
	full_list_to_look_for = pFragments + pRuntime if pRuntime is not None else pFragments
	AllFunctions = collect_all_my_functions(CredentialList, full_list_to_look_for, pverbose)
	AccountNum = len(set([x['AccountId'] for x in AllFunctions]))
	RegionNum = len(set([x['Region'] for x in AllFunctions]))
	display_results(AllFunctions, display_dict, None, pSaveFilename)

	if pFix:
		if pRuntime is None or pNewRuntime is None:
			print(f"You neglected to provide the runtime you want to change from and to. Exiting here... ")
			sys.exit(7)
		FixedFunctions = fix_my_functions(AllFunctions, pRuntime, pNewRuntime, pForceDelete, pTiming)
		print()
		print("And since we remediated the functions - here's the updated list... ")
		print()
		display_results(FixedFunctions, display_dict, None, pSaveFilename)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.3f} seconds{Fore.RESET}")
	print(ERASE_LINE)
	print(f"Found {len(AllFunctions)} functions across {AccountNum} accounts, across {RegionNum} regions")
	print()
	print("Thank you for using this script")
	print()
