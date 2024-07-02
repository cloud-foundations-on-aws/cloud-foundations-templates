#!/usr/bin/env python3

import logging
import sys
import os
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import time

from botocore.exceptions import ClientError
from colorama import Fore, init

import Inventory_Modules
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, find_stacksets3, get_regions3
from account_class import aws_acct_access

init()

__version__ = '2024.05.18'
ERASE_LINE = '\x1b[2K'
begin_time = time()
DefaultMaxWorkerThreads = 5


##################
# Functions
##################
def parse_args(args: object):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = os.path.split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()  # Allows for a single profile to be specified
	parser.singleregion()  # Allows for single region to be specified at the command line
	parser.fragment()
	parser.extendedargs()
	parser.save_to_file()
	parser.rootOnly()
	parser.timing()
	parser.verbosity()  # Allows for the verbosity to be handled.
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-i", "--instances",
		dest="pinstancecount",
		action="store_true",
		default=False,
		help="Flag to determine whether you want to see the instance totals for each stackset")
	local.add_argument(
		"-s", "--status",
		dest="pstatus",
		metavar="CloudFormation status",
		default="Active",
		choices=['active', 'ACTIVE', 'Active', 'deleted', 'DELETED', 'Deleted'],
		help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too. Valid values are 'ACTIVE' or 'DELETED'")
	return parser.my_parser.parse_args(args)


def setup_auth_and_regions(fProfile: str, fRegion: str = None, fStackFrag: list = None, fExact: bool = False) -> (aws_acct_access, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@return:
		- an object of the type "aws_acct_access"
		- a list of regions valid for this particular profile/ account.
	"""

	if fStackFrag is None:
		fStackfrag = ['all']
	if fRegion is None:
		fRegion = "us-east-1"
	try:
		aws_acct = aws_acct_access(fProfile)
	except ConnectionError as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	RegionList = get_regions3(aws_acct, [fRegion])

	if fRegion.lower() not in RegionList:
		print()
		print(f"{Fore.RED}You specified '{fRegion}' as the region, but this script only works with a single region.\n"
		      f"Please run the command again and specify only a single, valid region{Fore.RESET}")
		print()
		raise ValueError(f"You specified '{fRegion}' as the region, but this script only works with a single region.")

	print()
	action = "but not modify"
	print(f"You asked me to find ({action}) stacksets that match the following:")
	print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
	print(f"\t\tIn this Region: {fRegion}")

	if fExact:
		print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET} these fragments: {fStackfrag}")
	else:
		print(f"\t\tFor stacksets that contains these fragments: {fStackfrag}")

	print()
	return aws_acct, RegionList


def collect_cfnstacksets(faws_acct: aws_acct_access, fRegion: str) -> (dict, dict, dict):
	"""
	Description: This function collects the information about existing stacksets
	@param faws_acct: Account Object of type "aws_acct_access"
	@param fRegion: String for the region in which to collect the stacksets
	@return:
		- dict of lists, containing 1/ Aggregate list of stack instances found, 2/ list of stackset names found, 3/ list of stacksets that are in-scope for this script
		- dict of Accounts found within those stacksets
		- dict of Regions found within the stacksets
	"""
	# Get the StackSet names from the Management Account
	StackSets = find_stacksets3(faws_acct, fRegion, pStackfrag, pExact)
	if not StackSets['Success']:
		error_message = "Something went wrong with the AWS connection. Please check the parameters supplied and try again."
		sys.exit(error_message)
	logging.info(f"Found {len(StackSets['StackSets'])} StackSetNames that matched your fragment")

	combined_stack_set_instances = find_stack_set_instances(StackSets['StackSets'], fRegion)

	print(ERASE_LINE)
	logging.info(f"Found {len(combined_stack_set_instances)} stack instances.")

	AccountList = []
	StackSetsList = []
	FoundRegionList = []

	for _ in range(len(combined_stack_set_instances)):
		if pAccountList is None:  # Means we want to not remove anything
			StackSetsList.append(combined_stack_set_instances[_]['StackSetName'])
			AccountList.append(combined_stack_set_instances[_]['ChildAccount'])
			FoundRegionList.append(combined_stack_set_instances[_]['ChildRegion'])
		elif pAccountList is not None:
			if combined_stack_set_instances[_]['ChildAccount'] in pAccountList:
				StackSetsList.append(combined_stack_set_instances[_]['StackSetName'])
				AccountList.append(combined_stack_set_instances[_]['ChildAccount'])
				FoundRegionList.append(combined_stack_set_instances[_]['ChildRegion'])
	# I had to add this list comprehension to filter out the "None" types that happen when there are no stack-instances within a stack-set
	AccountList = sorted(list(set([item for item in AccountList if item is not None])))
	# RegionList isn't specific per account, as the deletion API doesn't need it to be, and it's easier to keep a single list of all regions, instead of per StackSet
	# TODO: Since we allow this now, should we revisit this?
	# If we update this script to allow the removal of individual regions as well as individual accounts, then we'll do that.
	FoundRegionList = sorted(list(set([item for item in FoundRegionList if item is not None])))
	StackSetsList = sorted(list(set(StackSetsList)))
	StackSet_Dict = {'combined_stack_set_instances': combined_stack_set_instances,
	                 'StackSets'                   : StackSets,
	                 'StackSetsList'               : StackSetsList}
	Account_Dict = {'AccountList': AccountList}
	Region_Dict = {'FoundRegionList': FoundRegionList}
	return StackSet_Dict, Account_Dict, Region_Dict


def find_stack_set_instances(fStackSetNames: list, fRegion: str) -> list:
	"""
	Note that this function takes a list of stack set names and finds the stack instances within them
	fStackSetNames - This is a list of stackset names to look for. The reserved word "all" will return everything
	fRegion - This is a string containing the region in which to look for stacksets.

	"""

	class FindStackSets(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_stacksetname, c_region, c_stackset_info, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for stack set name {c_stacksetname}")
				try:
					# Now go through those stacksets and determine the instances, made up of accounts and regions
					# Most time spent in this loop
					# for i in range(len(fStackSetNames['StackSets'])):
					logging.info(f"{ERASE_LINE}Looking through {c_PlaceCount} of {len(fStackSetNames)} stacksets found with {pStackfrag} string in them")
					# TODO: Creating the list to delete this way prohibits this script from including stacksets that are already empty. This should be fixed.
					StackInstances = Inventory_Modules.find_stack_instances3(aws_acct, c_region, c_stacksetname)
					logging.warning(f"Found {len(StackInstances)} Stack Instances within the StackSet {c_stacksetname}")
					for StackInstance in StackInstances:
						if 'StackId' not in StackInstance.keys():
							logging.info(f"The stack instance found {StackInstance} doesn't have a stackid associated. Which means it's never been deployed and probably OUTDATED")
							pass
						if pAccountList is None or StackInstance['Account'] in pAccountList:
							# This stack instance will be reported if it matches the account they provided,
							# or reported on if they didn't provide an account list at all.
							# or - it will be removed if they also provided the "+delete" parameter,
							# or it will be included since they're trying to ADD accounts to this stackset...
							logging.debug(f"This is Instance #: {str(StackInstance)}")
							logging.debug(f"This is instance status: {str(StackInstance['Status'])}")
							logging.debug(f"This is ChildAccount: {StackInstance['Account']}")
							logging.debug(f"This is ChildRegion: {StackInstance['Region']}")
							# logging.debug("This is StackId: %s", str(StackInstance['StackId']))

							if StackInstance['Region'] in RegionList:
								f_combined_stack_set_instances.append({
									'ParentAccountNumber' : aws_acct.acct_number,
									'ChildAccount'        : StackInstance['Account'],
									'ChildRegion'         : StackInstance['Region'],
									'StackStatus'         : StackInstance['Status'],
									'DetailedStatus'      : StackInstance['StackInstanceStatus']['DetailedStatus'] if 'DetailedStatus' in StackInstance['StackInstanceStatus'] else None,
									'StatusReason'        : StackInstance['StatusReason'] if 'StatusReason' in StackInstance else None,
									'OrganizationalUnitId': StackInstance['OrganizationalUnitId'] if 'OrganizationalUnitId' in StackInstance else None,
									'PermissionModel'     : c_stackset_info['PermissionModel'] if 'PermissionModel' in c_stackset_info else 'SELF_MANAGED',
									'StackSetName'        : c_stacksetname
									})
						elif not (StackInstance['Account'] in pAccountList):
							# If the user only wants to remove the stack instances associated with specific accounts,
							# then we only want to capture those stack instances where the account number shows up.
							# The following code captures this scenario
							logging.debug(f"Found a stack instance, but the account didn't match {pAccountList}... exiting")
							continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_stacksetname}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong")
					logging.info(f"Actual Error: {my_Error}")
					continue
				except ClientError as my_Error:
					logging.error(f"Error: Likely throttling errors from too much activity")
					logging.info(f"Actual Error: {my_Error}")
					continue
				finally:
					logging.info(f"{ERASE_LINE}Finished finding stack instances in stackset {c_stacksetname} in region {c_region} - {c_PlaceCount} / {len(fStackSetNames)}")
					pbar.update()
					self.queue.task_done()

	###########

	if fRegion is None:
		fRegion = 'us-east-1'
	checkqueue = Queue()

	f_combined_stack_set_instances = []
	PlaceCount = 0
	WorkerThreads = min(len(fStackSetNames), DefaultMaxWorkerThreads)

	pbar = tqdm(desc=f'Finding Stackset instances from {len(fStackSetNames)} stacksets',
	            total=len(fStackSetNames), unit=' stacksets'
	            )

	# Create and start the worker threads
	for x in range(WorkerThreads):
		worker = FindStackSets(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for stacksetname in fStackSetNames:
		logging.debug(f"Beginning to queue data - starting with {stacksetname}")
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			PlaceCount += 1
			checkqueue.put((stacksetname, fRegion, stacksetname, PlaceCount))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing stack set {stacksetname['StackSetName']} in {fRegion} region")
				logging.warning(f"It's possible that the region {fRegion} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return f_combined_stack_set_instances


def find_last_operations(faws_acct: aws_acct_access, fStackSetNames: list):
	"""
	@param: fStackSetName: The name of the stackset to find the operations of
	"""
	StackSetOps_client = faws_acct.session.client('cloudformation')
	AllStackSetOps = []
	for stacksetname in tqdm(fStackSetNames, desc="Checking stackset operations"):
		StackSetOps = StackSetOps_client.list_stack_set_operations(StackSetName=stacksetname, MaxResults=1, CallAs='SELF')['Summaries']
		AllStackSetOps.append({'StackSetName': stacksetname,
		                       'Operation'   : StackSetOps[0]['Action'],
		                       'LatestStatus': StackSetOps[0]['Status'],
		                       'LatestDate'  : StackSetOps[0]['EndTimestamp'],
		                       'Details'     : StackSetOps[0]['StatusDetails']['FailedStackInstancesCount']})
	return AllStackSetOps


##################
# Main
##################
if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfile = args.Profile
	pRegion = args.Region
	pInstanceCount = args.pinstancecount
	pRootOnly = args.RootOnly
	verbose = args.loglevel
	pTiming = args.Time
	pStackfrag: list = args.Fragments
	pExact: bool = args.Exact
	pAccountList = args.Accounts
	pstatus = args.pstatus
	pFilename = args.Filename
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	display_dict = {'StackSetName': {'DisplayOrder': 1, 'Heading': 'Stackset Name'},
	                'Operation'   : {'DisplayOrder': 2, 'Heading': 'Action'},
	                'LatestStatus': {'DisplayOrder': 3, 'Heading': 'Last status', 'Condition': ['FAILED', 'STOPPED']},
	                'LatestDate'  : {'DisplayOrder': 4, 'Heading': 'Last completed'},
	                'Details'     : {'DisplayOrder': 5, 'Heading': 'Failures'}}

	# Setup the aws_acct object
	aws_acct, RegionList = setup_auth_and_regions(pProfile)
	# Collect the stacksets, AccountList and RegionList involved
	StackSets, Accounts, Regions = collect_cfnstacksets(aws_acct, pRegion)
	# Get the last operations from the Stacksets we've found
	StackSets_and_Operations = find_last_operations(aws_acct, StackSets['StackSetsList'])
	# Display what we've found
	sorted_StackSets_and_Operations = sorted(StackSets_and_Operations, key=lambda x: x['LatestDate'], reverse=True)
	display_results(sorted_StackSets_and_Operations, display_dict, None, pFilename)

	print()
	print(ERASE_LINE)
	print(
		f"{Fore.RED}Found {len(StackSets['StackSetsList'])} Stacksets across {len(Accounts)} accounts across {len(Regions)} regions{Fore.RESET}")
	print()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print("Thanks for using this script...")
	print()
