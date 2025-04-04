#!/usr/bin/env python3

# import boto3
import sys
from Inventory_Modules import display_results, get_all_credentials, find_account_policies2, find_policy_action2
from ArgumentsClass import CommonArguments
from colorama import init, Fore
from botocore.exceptions import ClientError
from queue import Queue
from threading import Thread
from time import time

import logging

init()
__version__ = "2023.12.12"
ERASE_LINE = '\x1b[2K'
begin_time = time()


##################
def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all policies (and maybe the actions) within any of the accounts we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.fragment()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	parser.my_parser.add_argument(
		"--action",
		dest="paction",
		nargs="*",
		metavar="AWS Action",
		default=None,
		help="An action you're looking for within the policies")
	parser.my_parser.add_argument(
		"--cmp", "--customer_managed_policies",
		dest="pcmp",
		action="store_true",
		help="A flag to specify you're only looking for customer managed policies")
	return parser.my_parser.parse_args(args)


def check_accounts_for_policies(CredentialList, fRegionList=None, fActions=None, fFragments=None):
	"""
	Note that this function takes a list of Credentials and checks for policies in every account it has creds for
	"""

	class FindActions(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_policy, c_action, c_PlacesToLook, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					policy_actions = find_policy_action2(c_account_credentials, c_policy, c_action)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']} for policy {c_policy['PolicyName']}")
					if len(policy_actions) > 0:
						AllPolicies.extend(policy_actions)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					print(f"{ERASE_LINE}Finished finding policy actions in account {c_account_credentials['AccountId']} - {c_PlaceCount} / {c_PlacesToLook}", end='\r')
					self.queue.task_done()

	if fRegionList is None:
		fRegionList = ['us-east-1']
	if fFragments is None:
		fFragments = []
	checkqueue = Queue()

	AllPolicies = []
	AccountCount = 0
	Policies = []
	PolicyCount = 0

	print()
	for credential in CredentialList:
		try:
			logging.info(f"Connecting to account {credential['AccountId']}")
			Policies = find_account_policies2(credential, fRegionList[0], fFragments, pExact, pCMP)
			AccountCount += 1
			if fActions is None:
				PlacesToLook = len(Policies)
			else:
				PlacesToLook = len(Policies) * len(fActions)
			print(f"{ERASE_LINE}Found {PlacesToLook} matching policies in account {credential['AccountId']} ({AccountCount}/{len(CredentialList)})", end='\r')
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			if fActions is None:
				AllPolicies.extend(Policies)
			else:
				for policy in Policies:
					PolicyCount += 1
					for action in fActions:
						checkqueue.put((credential, policy, action, PlacesToLook, PolicyCount))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']}")
				pass

	# WorkerThreads = min(len(Policies) * len(fAction), 250)
	WorkerThreads = min(round(len(AllPolicies)/len(CredentialList)), 200)

	for x in range(WorkerThreads):
		worker = FindActions(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	checkqueue.join()
	return AllPolicies


##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfiles = args.Profiles
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccounts = args.Accounts
	pFragments = args.Fragments
	pRootOnly = args.RootOnly
	pActions = args.paction
	pCMP = args.pcmp
	pExact = args.Exact
	pTiming = args.Time
	pFilename = args.Filename
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	logging.info(f"Profiles: {pProfiles}")

	print()
	print(f"Checking for matching Policies... ")
	print()

	PoliciesFound = []
	AllChildAccounts = []
	# TODO: Will have to be changed to support single region-only accounts, but that's a ways off yet.
	pRegionList = RegionList = ['us-east-1']

	# Get credentials for all Child Accounts
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)
	# Find all the policies
	PoliciesFound.extend(check_accounts_for_policies(AllCredentials, RegionList, pActions, pFragments))
	# Display the information we've found this far
	sorted_policies = sorted(PoliciesFound, key=lambda x: (x['MgmtAccount'], x['AccountNumber'], x['Region'], x['PolicyName']))

	display_dict = {'MgmtAccount'  : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
					'AccountNumber': {'DisplayOrder': 2, 'Heading': 'Acct Number'},
					'Region'       : {'DisplayOrder': 3, 'Heading': 'Region'},
					'PolicyName'   : {'DisplayOrder': 4, 'Heading': 'Policy Name'},
					'Action'       : {'DisplayOrder': 5, 'Heading': 'Action'}}

	display_results(sorted_policies, display_dict, pActions, pFilename)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else print()
	print()
	print(f"Found {len(PoliciesFound)} policies across {len(AllCredentials)} accounts across {len(RegionList)} regions\n"
		  f"	that matched the fragment{'s' if len(pFragments) > 1 else ''} that you specified: {pFragments}")
	print()
	print("Thank you for using this script")
	print()
