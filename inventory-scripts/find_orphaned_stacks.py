#!/usr/bin/env python3

import logging

from time import time

# import simplejson as json
from botocore.exceptions import ClientError
from colorama import Fore, init

from Inventory_Modules import get_credentials_for_accounts_in_org, find_stacks2, get_regions3, find_stacksets3, find_stack_instances3, display_results, print_timings
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access

import sys
from os.path import split

"""
This script was created to help solve a testing problem for the "move_stack_instances.py" script.
Originally, that script didn't have built-in recovery, so we needed this script to "recover" those stack-instance ids that might have been lost during the move_stack_instances.py run. However, that script now has built-in recovery, so this script isn't really needed. However, it can still be used to find any stack-instances that have been orphaned from their original stack-set, if that happens. 
"""

init()
__version__ = "2024.05.18"
ERASE_LINE = '\x1b[2K'
begin_time = time()


##################
# Functions
##################

def parse_args(fargs):
	"""
	Description: Parse the arguments sent to the script
	@param fargs: namespace of the arguments passed in at the command line
	@return: namespace with all parameters parsed out
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()
	parser.singleregion()
	parser.fragment()
	parser.extendedargs()
	parser.rolestouse()
	parser.save_to_file()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		'-R', "--SearchRegions",
		help="The region(s) you want to search through to find orphaned stacksets.",
		default=['all'],
		nargs="*",
		metavar="region-name",
		dest="SearchRegionList")

	return parser.my_parser.parse_args(fargs)


def setup_auth_and_regions(fProfile: str, f_AccountList: list, f_Region: str, f_args) -> (aws_acct_access, list, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@param f_AccountList: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@param f_Region: A string representing the region provided by the user. If nothing, then use the default profile or credentials
	@param f_args: The arguments passed in at the command line
	@return:
		- an object of the type "aws_acct_access"
		- a list of regions valid for this particular profile/ account.
	"""
	# Validate inputs
	if isinstance(fProfile, str) or fProfile is None:
		pass
	else:       # If they tried to pass a list, or an integer, which should be caught at the argparse function...
		print(f"{Fore.RED}You specified an invalid profile name. This script only allows for one profile at a time. Please try again.{Fore.RESET}")
		sys.exit(7)

	try:
		aws_acct = aws_acct_access(fProfile)
	except ConnectionError as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	AllRegions = get_regions3(aws_acct)
	RegionList = get_regions3(aws_acct, f_args.SearchRegionList)

	if f_Region.lower() not in AllRegions:
		print(f"{Fore.RED}You specified '{f_Region}' as the region, but this script only works with a single region.\n"
		      f"Please run the command again and specify only a single, valid region{Fore.RESET}")
		sys.exit(9)

	print()
	ChildAccounts = []  # This is a list of dictionaries, each with the following keys: AccountId, AccountEmail, AccountStatus, MgmtAccount.
	if f_AccountList is None:
		ChildAccounts = aws_acct.ChildAccounts
	else:
		for account in aws_acct.ChildAccounts:
			if account['AccountId'] in f_AccountList:
				ChildAccounts.append({'AccountId'    : account['AccountId'],
				                      'AccountEmail' : account['AccountEmail'],
				                      'AccountStatus': account['AccountStatus'],
				                      'MgmtAccount'  : account['MgmtAccount']})
	AccountList = [account['AccountId'] for account in ChildAccounts]
	print(f"You asked me to find orphaned stacksets that match the following:")
	print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
	print(f"\t\tIn this home Region: {f_Region}")
	print(f"\t\tFor stackset instances whose region matches this region fragment: {f_args.SearchRegionList}") if f_args.SearchRegionList is not None else ''
	print(f"While skipping these accounts:\n{Fore.RED}{f_args.SkipAccounts}{Fore.RESET}") if f_args.SkipAccounts is not None else ''

	if f_args.Exact:
		print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET}: {f_args.Fragments}")
	else:
		print(f"\t\tFor stacksets that contain th{'is fragment' if len(f_args.Fragments) == 1 else 'ese fragments'}: {f_args.Fragments}")

	if f_args.Accounts is None:
		print(f"\t\tFor stack instances across all accounts")
	else:
		print(f"\t\tSpecifically to find th{'ese' if len(f_args.Accounts) > 1 else 'is'} account number{'s' if len(f_args.Accounts) > 1 else ''}: {f_args.Accounts}")
	print()
	return aws_acct, AccountList, RegionList


def find_stacks_within_child_accounts(fall_credentials, fFragmentlist: list = None, threads:int=25):
	from queue import Queue
	from threading import Thread

	class FindStacks(Thread):
		def __init__(self, fqueue: Queue):
			Thread.__init__(self)
			self.queue = fqueue

		def run(self):
			while True:
				# Get the next account from the queue
				c_credential, c_fragmentlist = self.queue.get()
				# Find the stacks in this account
				try:
					if c_credential['Success']:
						account_and_region_stacks = find_stacks2(c_credential, c_credential['Region'], c_fragmentlist)
						AllFoundStacks.extend(account_and_region_stacks)
					else:
						logging.info(f"Skipping {c_credential['AccountNumber']} in {c_credential['Region']} as we failed to successfully access")
				except Exception as my_Error:
					# ErrorMessage = my_Error.response['Error']['Message']
					logging.error(f"Error accessing account {c_credential['AccountId']} in region {c_credential['Region']} "
					              f"Skipping this account")
					logging.info(f"Actual Error: {my_Error}")
				finally:
					# Notify the queue that the job is done
					self.queue.task_done()

	# Create a queue to hold the threads
	checkqueue = Queue()
	if fFragmentlist is None:
		fFragmentlist = ['all']
	# This function takes the accounts and "SkipAccounts" that the user provided into account, so we don't have to filter any more than this.

	WorkerThreads = min(len(fall_credentials), threads)

	AllFoundStacks = []
	for x in range(WorkerThreads):
		worker = FindStacks(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in fall_credentials:
		logging.info(f"Queueing account {credential['AccountId']} and {credential['Region']}")
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			checkqueue.put((credential, fFragmentlist))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']}")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return AllFoundStacks


def reconcile_between_parent_stacksets_and_children_stacks(f_parent_stack_instances: list, f_child_stacks: list):
	child_comparisons = 0
	parent_comparisons = 0
	i = 0
	for ParentInstance in f_parent_stack_instances:
		parent_comparisons += 1
		for Childinstance in f_child_stacks:
			child_comparisons += 1
			if 'StackId' in ParentInstance.keys() and Childinstance['StackId'] == ParentInstance['StackId']:
				i += 1
				logging.debug(f"**** Match {i}!! **** - {time() - begin_time:.6f}")
				logging.debug(f"Childinstance: {Childinstance['StackId']}")
				logging.debug(f"ParentInstance:  {ParentInstance['StackId']}")
				Childinstance['Matches'] = ParentInstance['StackId']
				ParentInstance['Matches'] = Childinstance['StackId']
			else:
				continue
	print_timings(pTiming, verbose, begin_time, f"We compared {len(AllChildStackInstances)} child stacks against {len(AllParentStackInstancesInStackSets)} parent stack instances")
	# Filter out any instances that have a 'Match' in the Children
	Parent_Instances_Not_In_Children_Stacks = [x for x in AllParentStackInstancesInStackSets if 'Matches' not in x.keys()]
	# Filter out any instances that have a 'Match' in the Parent, as well as any that are regular account stacks
	Child_Instances_Not_In_Parent_Stacks = [x for x in AllChildStackInstances if 'Matches' not in x.keys() and (x['StackName'].find('StackSet-') > -1)]
	print()
	print(f"We found {len(Parent_Instances_Not_In_Children_Stacks)} parent stack instances that are not in the child stacks")
	print(f"We found {len(Child_Instances_Not_In_Parent_Stacks)} child stacks that are not in the parent stacksets")
	print()
	if verbose < 50:
		parent_display_dict = {'Account'     : {'DisplayOrder': 1, 'Heading': 'Acct Number'},
		                       'Region'      : {'DisplayOrder': 2, 'Heading': 'Region'},
		                       'StackSetId'  : {'DisplayOrder': 3, 'Heading': 'StackSet Id'},
		                       'Status'      : {'DisplayOrder': 4, 'Heading': 'Status'},
		                       'StatusReason': {'DisplayOrder': 5, 'Heading': 'Possible Reason'}}
		print(f"Stack Instances in the Root Account that don't appear in the Children")
		sorted_Parent_Instances_Not_In_Children_Stacks = sorted(Parent_Instances_Not_In_Children_Stacks, key=lambda k: (k['Account'], k['Region'], k['StackSetId']))
		display_results(sorted_Parent_Instances_Not_In_Children_Stacks, parent_display_dict, None, f"{pFilename}-Parent")
		child_display_dict = {'AccountNumber': {'DisplayOrder': 1, 'Heading': 'Acct Number'},
		                      'Region'       : {'DisplayOrder': 2, 'Heading': 'Region'},
		                      'StackName'    : {'DisplayOrder': 3, 'Heading': 'Stack Name'},
		                      'StackStatus'  : {'DisplayOrder': 4, 'Heading': 'Status'}}
		print(f"Stacks in the Children accounts that don't appear in the Root Stacksets")
		sorted_Child_Instances_Not_In_Parent_Stacks = sorted(Child_Instances_Not_In_Parent_Stacks, key=lambda k: (k['AccountNumber'], k['Region'], k['StackName']))
		display_results(sorted_Child_Instances_Not_In_Parent_Stacks, child_display_dict, None, f"{pFilename}-Child")


##################
# Main
##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegion = args.Region
	pSearchRegionList = args.SearchRegionList
	pAccounts = args.Accounts
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pFilename = args.Filename
	pRootOnly = False  # It doesn't make any sense to think that this script would be used for only the root account
	pExact = args.Exact
	pRoles = args.AccessRoles
	verbose = args.loglevel
	pTiming = args.Time
	pFragments = args.Fragments
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	ERASE_LINE = '\x1b[2K'
	begin_time = time()

	# Setup credentials and regions (filtered by what they wanted to check)
	aws_acct, AccountList, RegionList = setup_auth_and_regions(pProfile, pAccounts, pRegion, args)
	# Determine the accounts we're checking
	print_timings(pTiming, verbose, begin_time, "Just setup account and region list")
	AllCredentials = get_credentials_for_accounts_in_org(aws_acct, pSkipAccounts, pRootOnly, AccountList, pProfile, RegionList, pRoles, pTiming)
	print_timings(pTiming, verbose, begin_time, f"Finished getting {len(AllCredentials)} credentials for all accounts and regions in spec...")

	# Connect to every account, and in every region specified, to find all stacks
	print(f"Now finding all stacks across {'all' if pAccounts is None else (len(pAccounts) * len(RegionList))} accounts and regions under the {aws_acct.AccountType} account {aws_acct.acct_number}")
	AllChildStackInstances = find_stacks_within_child_accounts(AllCredentials, pFragments)
	print_timings(pTiming, verbose, begin_time, f"Just finished getting {len(AllChildStackInstances)} children stack instances")
	# and then compare them with the stackset instances managed within the Root account, and find anything that doesn't match

	# This is the list of stacksets in the root account
	AllParentStackSets = find_stacksets3(aws_acct, pRegion, pFragments, pExact)
	print_timings(pTiming, verbose, begin_time, f"Just finished getting {len(AllParentStackSets['StackSets'])} parent stack sets")
	print(f"Now getting all the stack instances for all {len(AllParentStackSets)} stacksets")
	# This will be the listing of the stack_instances in each of the stacksets in the root account
	AllParentStackInstancesInStackSets = []
	for stackset_name, stackset_attributes in AllParentStackSets['StackSets'].items():
		StackInstancesInStackSets = find_stack_instances3(aws_acct, pRegion, stackset_name, faccountlist=AccountList, fregionlist=RegionList)
		# TODO: Filter out skipped / closed accounts within the stacksets
		AllParentStackInstancesInStackSets.extend(StackInstancesInStackSets)
	print_timings(pTiming, verbose, begin_time, f"Just finished getting {len(AllParentStackInstancesInStackSets)} parent stack instances")
	# Then compare the stack_instances in the root account with the stack_instances in the child accounts to see if anything is missing
	print(f"We found {len(AllChildStackInstances)} stack instances in the {len(AccountList)} child accounts")
	print(f"We found {len(AllParentStackInstancesInStackSets)} stack instances in the {len(AllParentStackSets['StackSets'])} stacksets in the root account")
	print(f"Now cross-referencing these to find if there are any orphaned stacks...")
	# Find the stacks that are in the root account but not in the child accounts
	# And find any stack instances in the children accounts that are not in the root account
	# And display them to the screen...
	reconcile_between_parent_stacksets_and_children_stacks(AllParentStackInstancesInStackSets, AllChildStackInstances)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

	print()
	print("Thanks for using this script...")
	print()
