#!/usr/bin/env python3

import logging
import sys
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import sleep, time

from botocore.exceptions import ClientError
from colorama import Fore, Style, init

from Inventory_Modules import random_string, get_ec2_regions3, get_regions3, find_stack_instances3, find_stacksets3, get_child_access3, check_stack_set_status3, delete_stackset3, delete_stack_instances3
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access

'''
	- There are four possible use-cases when trying to modify or remove a stack instance from a stack set:
		- The stack exists as an association within the stackset AND it exists within the child account (typical)
			- We should remove the stackset-association with "--RetainStacks=False" and that will remove the child stack in the child account.
		- The stack exists as an association within the stackset, but has been manually deleted within the child account
			- If we remove the stackset-association with "--RetainStacks=False", it won't error, even when the stack doesn't exist within the child.
			- There is a special use case here where the child account has been deleted or suspended. This is a difficult use-case to test12.
		- The stack doesn't exist within the stackset association, but DOES exist within the child account (because its association was removed from the stackset)
			- The only way to remove this is to remove the stack from the child account. This would have to be done after having found the stack within the child account. This will be a ToDo for later...
		- The stack doesn't exist within the child account, nor within the stack-set
			- Nothing to do here
			
TODO:
	- Pythonize the whole thing
	- More Commenting throughout script
	- Make deleting multiple closed accounts easier - needs a parameter that comprises "+delete +force -A -check" all in one - to remove all closed accounts at one time... 
	- Add a stackset status, instead of just the status for the instances
	- Add a "tail" option, so it runs over and over until the stackset is finished
	- Make sure that the part where it removes stack instances and WAITS till they're done it working... 
'''

init()

__version__ = "2024.05.31"
ERASE_LINE = '\x1b[2K'
begin_time = time()
sleep_interval = 5
# Seems low, but this fits under the API threshold. Make it too high and it will not.
DefaultMaxWorkerThreads = 5


###################
def parse_args(f_arguments: object):
	"""
	Description: Parses the arguments passed into the script
	@param f_arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.singleprofile()
	parser.singleregion()
	# This next parameter includes picking a specific account, ignoring specific accounts or profiles
	parser.extendedargs()
	parser.fragment()
	parser.roletouse()
	# parser.save_to_file()
	parser.confirm()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	operation_group = parser.my_parser.add_mutually_exclusive_group()
	operation_group.add_argument(
		"+refresh",
		help="Use this parameter is you want to re-run the same stackset, over again",
		action="store_true",
		dest="Refresh")
	operation_group.add_argument(
		'+add',
		help="If this parameter is specified, we'll add the specified accounts to the specified stacksets.",
		action="store_true",
		dest="AddNew")
	operation_group.add_argument(
		'+delete', "+remove",
		help="If this parameter is specified, we'll delete stacksets we find, with no additional confirmation.",
		action="store_true",
		dest="DryRun")
	parser.my_parser.add_argument(
		'-R', "--ModifyRegion",
		help="The region(s) you want to either remove from or add to all the specified stacksets.",
		default=None,
		nargs="*",
		metavar="region-name",
		dest="pRegionModifyList")
	parser.my_parser.add_argument(
		'-c', '-check', '--check',
		help="Do a comparison of the accounts found in the stacksets to the accounts found in the Organization and list out any that have been closed or suspended, but never removed from the stacksets.",
		action="store_true",
		dest="AccountCheck")
	parser.my_parser.add_argument(
		'--date',
		help="Provide this flag if you want the date of the last operation included with the detailed stack instance output",
		action="store_true",
		dest="OperationDate")
	parser.my_parser.add_argument(
		'--retain', '--disassociate',
		help="Remove the stack instances from the stackset, but retain the resources. You must also specify '+delete' to use this parameter",
		action="store_true",
		dest="Retain")
	return parser.my_parser.parse_args(f_arguments)


def setup_auth_and_regions(fProfile: str) -> (aws_acct_access, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@return:
		- an object of the type "aws_acct_access"
		- a list of regions valid for this particular profile/ account.
	"""
	try:
		logging.info(f"Running for profile: {fProfile}")
		aws_acct = aws_acct_access(fProfile)
	except Exception as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	AllRegions = get_ec2_regions3(aws_acct)

	if not aws_acct.Success:
		print(f"\n{Fore.RED}Profile '{fProfile}' didn't work properly. Please provide a valid profile{Fore.RESET}\n")
		sys.exit(9)
	elif pRegion.lower() not in AllRegions:
		print()
		print(f"{Fore.RED}You specified '{pRegion}' as the region, but this script only works with a single region.\n"
		      f"Please run the command again and specify only a single, valid region{Fore.RESET}")
		print()
		sys.exit(9)

	print()
	if pdelete:
		action = "and delete"
	elif pAddNew:
		action = "and add to"
	elif pRefresh:
		action = "and refresh"
	else:
		action = "but not modify"
	print(f"You asked me to find ({action}) stacksets that match the following:")
	print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
	print(f"\t\tIn this Region: {pRegion}")

	RegionList = get_regions3(aws_acct, pRegionModifyList)

	if pRegionModifyList is None:
		print(f"\t\tFor stack instances across all enabled Regions")
	else:
		print(f"\t\tLimiting instance targets to Region{'s' if len(RegionList) > 1 else ''}: {RegionList}")

	if pExact:
		print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET}: {pStackfrag}")
	else:
		print(f"\t\tFor stacksets that contain th{'is fragment' if len(pStackfrag) == 1 else 'ese fragments'}: {pStackfrag}")

	if pAccountModifyList is None:
		print(f"\t\tFor stack instances across all accounts")
	else:
		print(f"\t\tSpecifically to find th{'ese' if len(pAccountModifyList) > 1 else 'is'} account number{'s' if len(pAccountModifyList) > 1 else ''}: {pAccountModifyList}")
	# print(f"\t\tSpecifically to find th{'ese' if len(pRegionModifyList) > 1 else 'is'} region{'s' if len(pRegionModifyList) > 1 else ''}: {pRegionModifyList}") if pRegionModifyList is not None else ""
	print(f"\t\tWe'll also display those accounts in the stacksets that are no longer part of the organization") if pCheckAccount else ""
	print(f"\t\tWe'll refresh the stackset with fragments {pStackfrag}") if pRefresh else ""
	print()
	return aws_acct, RegionList


def _find_stack_set_instances(fStackSetNames: dict, fRegion: str) -> list:
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
			"""
			Description: This function simply multi-threads the calls to the Inventory_Scripts function called "find_stack_instances3"
			@return: This returns a list with the stackset instance information...
			"""
			while True:
				# Get the work from the queue and expand the tuple
				c_stacksetname, c_region, c_stackset_info, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for stack set name {c_stacksetname}")
				try:
					# Now go through those stacksets and determine the instances, made up of accounts and regions
					# Most time spent in this loop
					# for i in range(len(fStackSetNames['StackSets'])):
					logging.info(f"{ERASE_LINE}Looking through {c_PlaceCount} of {len(fStackSetNames)} stacksets found with '{pStackfrag}' string in them")
					# TODO: Creating the list to delete this way prohibits this script from including stacksets that are already empty. This should be fixed.
					StackInstances = find_stack_instances3(aws_acct, c_region, c_stacksetname)
					logging.warning(f"Found {len(StackInstances)} Stack Instances within the StackSet {c_stacksetname}, without filtering on the specific accounts we were looking for")
					if len(StackInstances) == 0 and pAccountModifyList is None and pRegionModifyList is None:
						# logging.warning(f"While we didn't find any stack instances within {fStackSetNames['StackSets'][i]['StackSetName']}, we assume you want to delete it, even when it's empty")
						logging.warning(f"While we didn't find any stack instances within {c_stacksetname}, we assume you want to include it, even when it's empty")
						f_combined_stack_set_instances.append({
							'ParentAccountNumber' : aws_acct.acct_number,
							'ChildAccount'        : None,
							'ChildRegion'         : None,
							'StackStatus'         : None,
							'DetailedStatus'      : None,
							'StatusReason'        : None,
							'OrganizationalUnitId': None,
							'PermissionModel'     : c_stackset_info['PermissionModel'] if 'PermissionModel' in c_stackset_info else 'SELF_MANAGED',
							'StackSetName'        : c_stacksetname,
							'LastOperationId'     : None
							})
					for StackInstance in StackInstances:
						if 'StackId' not in StackInstance.keys():
							logging.info(f"The stack instance found {StackInstance} doesn't have a stackid associated. Which means it's never been deployed and probably OUTDATED")
							pass
						if pAccountModifyList is None or StackInstance['Account'] in pAccountModifyList:
							# This stack instance will be reported if it matches the account they provided,
							# or reported on if they didn't provide an account list at all.
							# or - it will be removed if they also provided the "+delete" parameter,
							# or it will be included since they're trying to ADD accounts to this stackset...
							logging.debug(f"This is Instance #: {str(StackInstance)}")
							logging.debug(f"This is instance status: {str(StackInstance['Status'])}")
							logging.debug(f"This is ChildAccount: {StackInstance['Account']}")
							logging.debug(f"This is ChildRegion: {StackInstance['Region']}")
							# logging.debug("This is StackId: %s", str(StackInstance['StackId']))

							if pRegionModifyList is None or (StackInstance['Region'] in RegionList) or ChangesRequested:
								f_combined_stack_set_instances.append({
									'ParentAccountNumber' : aws_acct.acct_number,
									'ChildAccount'        : StackInstance['Account'],
									'ChildRegion'         : StackInstance['Region'],
									'StackStatus'         : StackInstance['Status'],
									'DetailedStatus'      : StackInstance['StackInstanceStatus']['DetailedStatus'] if 'DetailedStatus' in StackInstance['StackInstanceStatus'] else None,
									'StatusReason'        : StackInstance['StatusReason'] if 'StatusReason' in StackInstance else None,
									'OrganizationalUnitId': StackInstance['OrganizationalUnitId'] if 'OrganizationalUnitId' in StackInstance else None,
									'PermissionModel'     : c_stackset_info['PermissionModel'] if 'PermissionModel' in c_stackset_info else 'SELF_MANAGED',
									'StackSetName'        : c_stacksetname,
									'LastOperationId'     : StackInstance['LastOperationId']
									})
						elif not (StackInstance['Account'] in pAccountModifyList):
							# If the user only wants to remove the stack instances associated with specific accounts,
							# then we only want to capture those stack instances where the account number shows up.
							# The following code captures this scenario
							logging.debug(f"Found a stack instance, but the account didn't match {pAccountModifyList}... exiting")
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
					logging.debug(f"Operations name: {my_Error.operation_name} | Response: {my_Error.response} | MSG TEMPLATE: {my_Error.MSG_TEMPLATE}")
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

	pbar = tqdm(desc=f'Finding instances from {len(fStackSetNames)} stacksets',
	            total=len(fStackSetNames), unit=' stacksets'
	            )

	for x in range(WorkerThreads):
		worker = FindStackSets(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for stackset_name, stackset_data in fStackSetNames.items():
		logging.debug(f"Beginning to queue data - starting with {stackset_name}")
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			PlaceCount += 1
			checkqueue.put((stackset_name, fRegion, stackset_data, PlaceCount))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing stack set {stackset_name} in {fRegion} region")
				logging.warning(f"It's possible that the region {fRegion} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return f_combined_stack_set_instances


def display_stack_set_health(StackSet_Dict: dict, Account_Dict: dict):
	"""
	Description: This function shows off the health of the stacksets at the end of the script
	@param StackSet_Dict: Dictionary containing the stacksets that were updated
	@param Account_Dict: Dictionary containing the accounts that were used
	@return: Nothing - just writes to the screen

	TODO: Since it refers to "combined_stack_set_instances",
		there's a edge-case where it skips stacksets that don't appear to have the instance, if it failed to be added.
	"""
	combined_stack_set_instances = StackSet_Dict['combined_stack_set_instances']
	RemovedAccounts = Account_Dict['RemovedAccounts'] if pCheckAccount else None
	InaccessibleAccounts = Account_Dict['InaccessibleAccounts'] if pCheckAccount else None
	StackSetNames = StackSet_Dict['StackSetNames']['StackSets']
	summary = {}
	stack_set_permission_models = dict()
	for record in combined_stack_set_instances:
		stack_set_name = record['StackSetName']
		stack_status = record['StackStatus']
		# stackset_status = StackSetNames[stack_set_name]['Status']
		# stackset_status_reason = StackSetNames[stack_set_name]['Reason']
		detailed_status = record['DetailedStatus']
		status_reason = record['StatusReason']
		stack_region = record['ChildRegion']
		last_operation = record['LastOperationId']
		ou = record['OrganizationalUnitId']
		stack_set_permission_models.update({stack_set_name: record['PermissionModel']})
		if stack_set_name not in summary:
			summary[stack_set_name] = {}
		if stack_status not in summary[stack_set_name]:
			summary[stack_set_name][stack_status] = []
		summary[stack_set_name][stack_status].append({
			'Account'       : record['ChildAccount'],
			'Region'        : stack_region,
			'DetailedStatus': detailed_status,
			'StatusReason'  : status_reason,
			'LastOperation' : last_operation,
			'OrganizationalUnitId': ou
			})
		summary[stack_set_name]['Status'] = StackSetNames[stack_set_name]['Status']

	# Print the summary
	sorted_summary = dict(sorted(summary.items()))
	print()
	for stack_set_name, status_counts in sorted_summary.items():
		print(f"{stack_set_name} ({stack_set_permission_models[stack_set_name]}) | Last Operation {sorted_summary[stack_set_name]['Status']}:")
		for stack_status, instances in status_counts.items():
			if stack_status is None:
				print(f"\t{Fore.RED}--Empty stackset--{Fore.RESET}")
			elif stack_status == 'Status':
				continue
			else:
				print(f"\t{Fore.RED if stack_status not in ['CURRENT'] else ''}{stack_status}: {len(instances)} instances {Fore.RESET}")
			if verbose < 50:
				stack_instances = {}
				for stack_instance in instances:
					if stack_instance['Account'] not in stack_instances.keys():
						stack_instances[stack_instance['Account']] = {'Region': [], 'DetailedStatus': stack_instance['DetailedStatus'], 'StatusReason': stack_instance['StatusReason'], 'OperationId': stack_instance['LastOperation']}
					stack_instances[stack_instance['Account']]['Region'].append(stack_instance['Region'])
				for k, v in stack_instances.items():
					if pCheckAccount and k in RemovedAccounts:
						print(f"{Style.BRIGHT}{Fore.MAGENTA}\t\t{k}: {v['Region']}\t <----- Look here for orphaned accounts!{Style.RESET_ALL}")
					else:
						print(f"\t\t{k}: {v['Region']}")
					if verbose <= 30 and pOperationDate:
						last_stackset_operation = v['OperationId']
						cfn_client = aws_acct.session.client('cloudformation')
						last_operation_date = cfn_client.describe_stack_set_operation(StackSetName=stack_set_name, OperationId=last_stackset_operation)['StackSetOperation']['EndTimestamp']
						logging.info(f"Account: {k} | Region: {v['Region']}\n")
						print(f"\t\t\t{Fore.RED if v['DetailedStatus'] != 'SUCCEEDED' else ''}Detailed Status: {v['DetailedStatus']}{Fore.RESET}\n"
						      f"\t\t\tCompleted: {last_operation_date}\n"
						      f"\t\t\tStatus Reason: {v['StatusReason']}")
					elif verbose <= 30 and stack_status != 'CURRENT':
						logging.info(f"\t\t\tAccount: {k}\n"
						             f"\t\t\tRegion: {v['Region']}\n")
						print(f"\t\t\t{Fore.RED}Detailed Status: {v['DetailedStatus']}{Fore.RESET}\n"
						      f"\t\t\tStatus Reason: {v['StatusReason']}")
						pass
	if verbose < 50:
		print()
		print(f"Found {len(StackSetNames)} matching stackset{'' if len(StackSetNames) == 1 else 's'}")
		print(f"Found a total of {len(combined_stack_set_instances)} matching stack instance{'' if len(combined_stack_set_instances) == 1 else 's'}")
		# print(f"Found {len(summary)} unique stackset names within the Stack Instances")
		print()

	# Print the summary of any accounts that were found in the StackSets, but not in the Org.
	if pCheckAccount:
		print("Displaying accounts within the stacksets that aren't a part of the Organization")
		print()
		# TODO: Adding together these two lists - which are likely full of the same accounts gives an incorrect number
		logging.info(f"Found {len(InaccessibleAccounts) + len(RemovedAccounts)} accounts that don't belong")
		print(f"There were {len(RemovedAccounts)} accounts in the {len(StackSetNames)} Stacksets we looked through, that are not a part of the Organization")
		for item in RemovedAccounts:
			print(f"Account {item} is not in the Organization")
		print()
		print(f"There are {len(InaccessibleAccounts)} accounts that appear inaccessible, using typical role names")
		for item in InaccessibleAccounts:
			print(f"Account {item['AccountId']} is unreachable using these roles:\n"
			      f"\t\t{item['RolesTried']}")
		print()


def get_stack_set_deployment_target_info(faws_acct: aws_acct_access, fRegion: str, fStackSetName: str, fAccountRemovalList: list = None):
	"""
	Required Parameters:
	faws_acct - the object containing the account credentials and such
	fRegion - the region we're looking to make changes in
	fStackSetName - the stackset we're removing stack instances from
	fAccountRemvalList - The list of accounts they may have provided to limit the deletion to
	"""
	return_result = {'Success': False, 'ErrorMessage': None, 'Results': None}
	if fAccountRemovalList is None:
		deployment_results = find_stack_instances3(faws_acct, fRegion, fStackSetName)
		identified_ous = list(set([x['OrganizationalUnitId'] for x in deployment_results]))
		DeploymentTargets = {
			# 'Accounts'             : [
			# 	'string',
			# ],
			# 'AccountsUrl'          : 'string',
			'OrganizationalUnitIds': identified_ous
			# 'AccountFilterType'    : 'NONE' | 'INTERSECTION' | 'DIFFERENCE' | 'UNION'
			}
	else:
		DeploymentTargets = {
			'Accounts': fAccountRemovalList,
			# 'AccountsUrl'          : 'string',
			# 'OrganizationalUnitIds': identified_ous
			# 'AccountFilterType'    : 'NONE' | 'INTERSECTION' | 'DIFFERENCE' | 'UNION'
			}
	return_result.update({'Success': True, 'ErrorMessage': None, 'Results': DeploymentTargets})
	return return_result


def collect_cfnstacksets(faws_acct: aws_acct_access, fRegion: str) -> dict:
	"""
	Description: This function collects the information about existing stacksets
	@param faws_acct: Account Object of type "aws_acct_access"
	@param fRegion: String for the region in which to collect the stacksets
	@return:
		- dict of lists, containing:
		 1) Aggregate list of all stack instances found
		 2) list of stackset names found
		 3) list of stacksets that are in-scope for this script
		 4) list of stackset instances that may be acted upon
		 5) dict of Accounts found within the applicable stacksets
		 6) dict of Regions found within the applicable stacksets
	"""
	# TODO: Wrap in try... except to capture errors here, and when we do - stop using this as a dict!!.
	# Get the StackSet names from the Management Account
	StackSetNames = find_stacksets3(faws_acct, fRegion, pStackfrag, pExact, fGetHealth=True)
	if not StackSetNames['Success']:
		error_message = "Something went wrong with the AWS connection. Please check the parameters supplied and try again."
		sys.exit(error_message)
	logging.info(f"Found {len(StackSetNames['StackSets'])} StackSetNames that matched your fragment")

	# This finds ALL stack_set_instances in *all* stack_sets that matched the NAME...
	combined_stack_set_instances = _find_stack_set_instances(StackSetNames['StackSets'], fRegion)

	print(ERASE_LINE)
	logging.info(f"Found {len(combined_stack_set_instances)} stack instances, filtered on specific accounts.")

	# Assumes that all stacksets found are "Applicable"
	ApplicableStackSetsList = sorted(list(set([stackset_name for stackset_name in StackSetNames['StackSets'].keys()])))
	# The checks for None below are required in case the stackset has no instances.
	FoundAccountList = sorted(list(set([item['ChildAccount'] for item in combined_stack_set_instances if item['ChildAccount'] is not None])))
	FoundRegionList = sorted(list(set([item['ChildRegion'] for item in combined_stack_set_instances if item['ChildRegion'] is not None])))
	# If no accounts specified, but regions were specified
	if pAccountModifyList is None and pRegionModifyList is not None:
		ApplicableStackSetInstancesList = list(filter(lambda n: (n['ChildRegion'] in pRegionModifyList), combined_stack_set_instances))
	# If accounts were specified, but regions were not specified
	elif pAccountModifyList is not None and pRegionModifyList is None:
		ApplicableStackSetInstancesList = list(filter(lambda n: (n['ChildAccount'] in pAccountModifyList), combined_stack_set_instances))
	# If accounts were specified and regions were specified
	elif pAccountModifyList is not None and pRegionModifyList is not None:
		ApplicableStackSetInstancesList = list(filter(lambda n: (n['ChildAccount'] in pAccountModifyList and n['ChildRegion'] in pRegionModifyList), combined_stack_set_instances))
	# If no accounts or regions were provided, then apply to everything...
	else:
		ApplicableStackSetInstancesList = combined_stack_set_instances

	if pAddNew:
		# This exists, in case there are EMPTY stacksets, which the user is adding to, which wouldn't have shown up within the combined_stack_set_instances above
		ApplicableStackSetsList = [stackset_name for stackset_name in StackSetNames['StackSets'].keys()]

	stackset_instance_count = {}
	for _stackset_name in ApplicableStackSetsList:
		stackset_instance_count[_stackset_name] = len([n['StackSetName'] for n in combined_stack_set_instances if n['StackSetName'] == _stackset_name])
	for stackset_name, stackset_data in StackSetNames['StackSets'].items():
		stackset_data['InstanceCount'] = stackset_instance_count[stackset_name]
	"""
	Within StackSet_Dict, there are six lists:
		1. combined_stack_set_instances: which is a list of all stackset instances from all stacksets that matched the name
		2. StackSetNames: which is a list of the stackset names that matched
		3. ApplicableStackSetsList: which is a list of all stacksets (and their attributes) which matched the name
		4. ApplicableStackSetInstances: which is a list of only those stackset instances which matched the name, account, region to be modified
		5. FoundAccountList is a list of accounts found in all the stackset instances that matched
		6. FoundRegionList is a list of regions found in all the stackset instances that matched
	"""
	StackSet_Dict = {'combined_stack_set_instances'   : combined_stack_set_instances,
	                 'StackSetNames'                  : StackSetNames,
	                 'ApplicableStackSetsList'        : ApplicableStackSetsList,
	                 'ApplicableStackSetInstancesList': ApplicableStackSetInstancesList,
	                 'FoundAccountList'               : FoundAccountList,
	                 'FoundRegionList'                : FoundRegionList}
	return StackSet_Dict


def check_accounts(faws_acct: aws_acct_access, AccountList: list):
	Account_Dict = {}
	InaccessibleAccounts = []
	OrgAccountList = [i['AccountId'] for i in faws_acct.ChildAccounts]
	logging.info(f"There are {len(OrgAccountList)} accounts in the Org, and {len(AccountList)} unique accounts in all stacksets found")
	RemovedAccounts = list(set(AccountList) - set(OrgAccountList))
	# TODO: Wrap in Try...Except
	for accountnum in AccountList:
		logging.info(f"{ERASE_LINE}Trying to gain access to account number {accountnum}")
		my_creds = get_child_access3(faws_acct, accountnum)
		if my_creds['AccessError']:
			InaccessibleAccounts.append({'AccountId' : accountnum,
			                             'Success'   : my_creds['Success'],
			                             'RolesTried': my_creds['RolesTried']})
	Account_Dict.update({'InaccessibleAccounts': InaccessibleAccounts,
	                     'RemovedAccounts'     : RemovedAccounts,
	                     'AccountList'         : AccountList})
	return Account_Dict


def check_on_stackset_operations(OpsList: list, f_cfn_client):
	"""
	Description: Showing the health and status of the stacksets operated on within this script.
	@param OpsList: Ths list of stacksets that were modified
	@param f_cfn_client: The boto client used within the operation, just we don't need to open another
	@return: Nothing. Just writes to the screen.
	"""
	print(f"If this status checking is annoying, you can Ctrl-C to quit out, since the stackset operations are working in the background.")
	StillRunning = True
	stackset_results = {}
	while StillRunning:
		Success = True
		StillRunning = False
		for operation in OpsList:
			print(f"Checking on operations... ")
			StackSetStatus = f_cfn_client.describe_stack_set_operation(StackSetName=operation['StackSetName'], OperationId=operation['OperationId'])
			print(f"StackSet: {operation['StackSetName']} | Status: {StackSetStatus['StackSetOperation']['Status']}")
			# Allows this to run until *all* stacksets are complete - whether successfully or not
			StillRunning = StillRunning or StackSetStatus['StackSetOperation']['Status'] == 'RUNNING'
			Success = Success and StackSetStatus['StackSetOperation']['Status'] == 'SUCCEEDED'
			stackset_results.update({operation['StackSetName']: StackSetStatus['StackSetOperation']['Status']})
			stackset_results.update({operation['StackSetName']: StackSetStatus['StackSetOperation']['Status']})
		if StillRunning:
			print(f"Waiting {sleep_interval} seconds before checking all stacksets again... ")
			print()
			sleep(sleep_interval)
	return stackset_results


def _modify_stacksets(StackSet_Dict: dict) -> dict:
	applicable_stack_set_instances = StackSet_Dict['ApplicableStackSetInstancesList']
	StackSets: dict = StackSet_Dict['StackSetNames']['StackSets']
	ApplicableStackSetsList = StackSet_Dict['ApplicableStackSetsList']
	AccountList = StackSet_Dict['FoundAccountList']
	FoundRegionList = StackSet_Dict['FoundRegionList']
	# RemovedAccounts = Account_Dict['RemovedAccounts']

	# If we *are* deleting stack instances, and there's anything to delete...
	if pdelete and len(applicable_stack_set_instances) > 0:
		ReallyDelete = False
		print()
		print(f"Removing {len(applicable_stack_set_instances)} stack instances from the {len(StackSets)} StackSets found")
		StackInstanceItem = 0
		results = dict()
		# We need to use the StackSet Data dictionary, since only that dictionary tells us whether this is a SELF_MANAGED or SERVICE_MANAGED stackset
		for StackSetName, StackSetData in StackSets.items():
			StackSetResult = {'StackSetName': StackSetName, 'Success': False, 'ErrorMessage': "Haven't started yet..."}
			StackInstanceItem += 1
			print(f"About to start deleting stackset instances in {StackSetName}. Beginning {StackInstanceItem} of {len(ApplicableStackSetsList)}")
			# TODO: This needs to be wrapped in a try...except
			# Determine what kind of stackset this is - Self-Managed, or Service-Managed.
			# We need to check to see if the 'PermissionModel' key in in the dictionary, since it's only in the dictionary if the permission is 'service_managed',
			# but I'm not willing to be it stats that way...
			if 'PermissionModel' in StackSetData.keys() and StackSetData['PermissionModel'] == 'SERVICE_MANAGED':
				"""
				If the StackSet is SERVICE-MANAGED, we need to find more information about the stackset than is returned in the "list-stack-set" call from above
				"""
				if pAccountModifyList is None:
					DeploymentTargets = get_stack_set_deployment_target_info(aws_acct, pRegion, StackSetName)
				else:
					DeploymentTargets = get_stack_set_deployment_target_info(aws_acct, pRegion, StackSetName, pAccountModifyList)
				if FoundRegionList is None:
					print(f"There appear to be no stack instances for this stack-set")
					continue
				# TODO:
				#  Have to rethink this part - since we have to be careful how we remove specific accounts or OUs in Service-Managed Stacks
				if pAccountModifyList is None:  # Remove all instances from the stackset
					if pRegionModifyList is not None:
						print(f"About to update stackset {StackSetName} to remove all accounts within {str(FoundRegionList)}")
						RemoveStackSet = False
					else:
						print(f"About to update stackset {StackSetName} to remove ALL accounts from all regions")
						RemoveStackSet = True
				# RemoveStackInstanceResult = _delete_stack_instances(aws_acct, pRegion, AccountList, FoundRegionList, StackSetName, pForce)
				else:
					print(f"About to remove account {pAccountModifyList} from stackset {StackSetName} in regions {str(FoundRegionList)}")
					RemoveStackSet = False
				RemoveStackInstanceResult = _delete_stack_instances(aws_acct,
				                                                    pRegion,
				                                                    StackSetName,
				                                                    pRetain,
				                                                    AccountList,
				                                                    FoundRegionList,
				                                                    StackSetData['PermissionModel'],
				                                                    DeploymentTargets['Results'])
			# Section that handles the deletion for the "SELF_MANAGED" type of stackset
			else:
				# There were no regions found in the stackset, which means there are no instances, which means there's nothing to delete
				if StackSetData['Status'] == 'Never Run':
					print(f"There appear to be no stack instances for this stack-set")
					StackSetResult = {'Success': True}
					continue
				# If the user didn't supply any accounts to be deleted (which means *all* accounts)
				if pAccountModifyList is None:
					# If they supplied specific regions to be deleted
					if pRegionModifyList is not None:
						print(f"About to update stackset {StackSetName} to remove all instances with {str(pRegionModifyList)} "
						      f"region{'' if len(pRegionModifyList) == 1 else 's'}")
						RegionsToDelete = pRegionModifyList
						RemoveStackSet = False
					# If they *didn't* supply specific regions to be deleted - which means all regions.
					elif pRegionModifyList is None:
						print(f"About to update stackset {StackSetName} to remove ALL accounts from all regions")
						RegionsToDelete = FoundRegionList
						# Only delete the stackset, if they didn't specify "retain"
						RemoveStackSet = True and not pRetain
				# If the user *did* supply a list of accounts to be deleted
				elif pAccountModifyList is not None:
					# If the user specified the regions to be deleted
					if pRegionModifyList is not None:
						print(f"About to update stackset {StackSetName} to remove all instances with {str(pRegionModifyList)} "
						      f"region{'' if len(pRegionModifyList) == 1 else 's'}")
						RegionsToDelete = pRegionModifyList
						RemoveStackSet = False
					# If the user *didn't* specify a list of regions (which means *all* regions)
					else:
						print(f"About to remove ALL instances from stackset {StackSetName}")
						RegionsToDelete = FoundRegionList
						# Only delete the stackset, if they didn't specify "retain"
						RemoveStackSet = True and not pRetain
					logging.info(f"About to remove account {pAccountModifyList} from stackset {StackSetName} in regions {str(RegionsToDelete)}")
				ReallyDelete = False
				# If they didn't specify any accounts
				if pAccountModifyList is None:
					# AND they didn't specify any regions
					if pRegionModifyList is None:
						# Assume they meant ALL instances
						instances_to_modify = list(filter(lambda n: n['StackSetName'] == StackSetName, applicable_stack_set_instances))
					elif len(pRegionModifyList) > 0:  # They *did* specify some regions
						# Assume they meant, all instances with those regions
						instances_to_modify = list(filter(lambda n: (n['ChildRegion'] in pRegionModifyList and n['StackSetName'] == StackSetName), applicable_stack_set_instances))
				# They *did* specify some accounts,
				elif pRegionModifyList is None:  # But they didn't specify a region
					instances_to_modify = list(filter(lambda n: (n['ChildAccount'] in pAccountModifyList and n['StackSetName'] == StackSetName), applicable_stack_set_instances))
				elif len(pRegionModifyList) > 0:  # And they specified regions
					instances_to_modify = list(filter(lambda n: (n['ChildAccount'] in pAccountModifyList and n['ChildRegion'] in pRegionModifyList and n['StackSetName'] == StackSetName), applicable_stack_set_instances))
				else:  # Empty list
					instances_to_modify = []

				if not pConfirm:
					ReallyDelete = (input(f"{Fore.RED}Removing {len(instances_to_modify)} instances within {StackSetName}...{Fore.RESET}\n"
					                      f"Are you still sure? (y/n): ") in ['y', 'Y'])
				if pConfirm or ReallyDelete:
					RemoveStackInstanceResult = _delete_stack_instances(aws_acct, pRegion, StackSetName, pRetain, AccountList, RegionsToDelete)
				else:
					RemoveStackInstanceResult = {'Success': False, 'ErrorMessage': 'Customer decided not to delete stack instances'}

			if RemoveStackInstanceResult['Success']:
				Instances = [item for item in applicable_stack_set_instances if item['StackSetName'] == StackSetName]
				print(f"{ERASE_LINE}Successfully initiated removal of {len(Instances)} instance{'' if len(Instances) == 1 else 's'} from StackSet {StackSetName}")
			elif RemoveStackInstanceResult['ErrorMessage'] == 'Failed-ForceIt' and pRetain:
				print("We tried to force the deletion, but some other problem happened.")
			elif RemoveStackInstanceResult['ErrorMessage'] == 'Failed-ForceIt' and not pRetain:
				Decision = (input("Deletion of Stack Instances failed, but might work if we force it. Shall we force it? (y/n): ") in ['y', 'Y'])
				if Decision:
					RemoveStackInstanceResult = _delete_stack_instances(aws_acct, pRegion, StackSetName, True, AccountList, RegionsToDelete)  # Try it again, forcing it this time
					if RemoveStackInstanceResult['Success']:
						print(f"{ERASE_LINE}Successfully retried StackSet {StackSetName}")
					elif pRetain is True and RemoveStackInstanceResult['ErrorMessage'] == 'Failed-ForceIt':
						print(f"{ERASE_LINE}Some other problem happened on the retry.")
					elif RemoveStackInstanceResult['ErrorMessage'] == 'Failed-Other':
						print(f"{ERASE_LINE}Something else failed on the retry... Please report the error received.")
			elif str(RemoveStackInstanceResult['ErrorMessage']).find('OperationInProgressException') > 0:
				print(f"{Fore.RED}Another operation is running on this StackSet... Please wait for that operation to end and re-run this script{Fore.RESET}")
				sys.exit(RemoveStackInstanceResult['ErrorMessage'])
			elif not ReallyDelete and not pConfirm:
				sys.exit(RemoveStackInstanceResult['ErrorMessage'])
			else:
				print(f"{Fore.RED}Something else failed... Please report the error below{Fore.RESET}")
				logging.critical(f"{RemoveStackInstanceResult['ErrorMessage']}")
				sys.exit(RemoveStackInstanceResult['ErrorMessage'])
			if RemoveStackSet:
				logging.info(f"Instances have received the deletion command, continuing to remove the stackset too")
				# If there were no Instances to be deleted
				if Instances[0]['ChildAccount'] is None:
					# skip the check to see if stack instances are gone
					RemoveStackInstanceResult['OperationId'] = None
					StackInstancesAreGone = dict()
					StackInstancesAreGone['Success'] = True
					StackInstancesAreGone['OperationId'] = None
					StackInstancesAreGone['StackSetStatus'] = "Not yet assigned"
				# else if there WERE child stacks that were deleted
				else:
					StackInstancesAreGone = check_stack_set_status3(aws_acct, StackSetName, RemoveStackInstanceResult['OperationId'])
					logging.debug(f"The operation id {RemoveStackInstanceResult['OperationId']} is {StackInstancesAreGone['StackSetStatus']}")
				if not StackInstancesAreGone['Success']:
					logging.critical(f"There was a problem with removing the stack instances from stackset {StackSetName}."
					                 f"Moving to the next stackset in the list")
					break
				intervals_waited = 1
				while StackInstancesAreGone['StackSetStatus'] in ['RUNNING']:
					print(f"Waiting for operation {RemoveStackInstanceResult['OperationId']} to finish",
					      f"{sleep_interval * intervals_waited} seconds waited so far", end='\r')
					sleep(sleep_interval)
					intervals_waited += 1
					StackInstancesAreGone = check_stack_set_status3(aws_acct, StackSetName, RemoveStackInstanceResult['OperationId'])
					if not StackInstancesAreGone['Success']:
						logging.critical(f"There was a problem with removing the stack instances from stackset {StackSetName}.")
				StackSetResult = delete_stackset3(aws_acct, pRegion, StackSetName)
				if StackSetResult['Success']:
					print(f"{ERASE_LINE}Removal of stackset {StackSetName} took {sleep_interval * intervals_waited} seconds")
				else:
					print(f"{ERASE_LINE}{Fore.RED}Removal of stackset {StackSetName} {Style.BRIGHT}failed{Style.NORMAL} due to:\n\t{StackSetResult['ErrorMessage']}.{Fore.RESET}")
			results.update({StackSetName: StackSetResult})
		results['ChangesMade'] = True
		return results
	# If we're supposed to be adding more instances to the existing stacksets
	elif pAddNew:
		print()
		print(f"Adding instances into the specified stacksets")
		# Sometimes the user will provide the accounts they want to add, with no additional regions...
		if pAccountModifyList is not None and pRegionModifyList is None:
			operation_result = _add_instances_to_stacksets(StackSet_Dict, pAccountModifyList)
		# Sometimes they want to add a region, but not change the existing accounts...
		elif pAccountModifyList is None and pRegionModifyList is not None:
			operation_result = _add_instances_to_stacksets(StackSet_Dict, AccountList, pRegionModifyList)
		# They want to change both the accounts AND the regions
		elif pAccountModifyList is not None and pRegionModifyList is not None:
			operation_result = _add_instances_to_stacksets(StackSet_Dict, pAccountModifyList, pRegionModifyList)
		# They provided the "+add" parameter, but didn't specify any accounts or regions to add
		else:
			logging.error(f"You specified to '+add', but didn't specify any new accounts or regions to add... exiting... ")
			sys.exit(95)
		operation_result['ChangesMade'] = True
		return operation_result
	# If we are just refreshing the specific stacksets (within the "ApplicableStackSetsList")
	elif pRefresh and len(applicable_stack_set_instances) > 0:
		operation_result = _refresh_stacksets(StackSet_Dict)
		operation_result['ChangesMade'] = True
		return operation_result
	# No matching stacksets, or no matching stackset instances
	else:
		print(f"{Fore.RED}You asked us to make a change, but there are no matching stacksets or stackset instances to modify...{Fore.RESET}")
		operation_result = dict()
		operation_result['ChangesMade'] = False
		for stackset_name, stackset_data in StackSets.items():
			operation_result[stackset_name] = stackset_data['Status']
		return operation_result


def _delete_stack_instances(faws_acct: aws_acct_access, fRegion: str, fStackSetName: str, fRetain: bool, fAccountList: list = None, fRegionList: list = None, fPermissionModel='SELF_MANAGED', fDeploymentTargets=None) -> dict:
	"""
	Required Parameters:
	faws_acct - the object containing the account credentials and such
	fRegion - the region we're looking to make changes in
	fAccountList - this is the listing of accounts that were FOUND to be within stack instances
	fRegionList - The list of regions within the stackset to remove as well
	fStackSetName - the stackset we're removing stack instances from
	fRetain - By passing a "True" here, the API will pass on "RetainStacks" to the child stack - which will allow the stackset to be deleted more easily,
	 	but also leaves a remnant in the child account to clean up later..
	fPermissionModel - Whether the StackSet is using SELF_MANAGED or SERVICE_MANAGED permission model (associating the stack with individual accounts, or with an OU itself)
	fDeploymentTargets - When fPermissionModel is 'SELF_MANAGED', this should be None.
						When fPermissionModel is 'SERVICE_MANAGED', this is a dictionary specifying which OUs, or accounts should be impacted"
	"""
	logging.info(f"Removing instances from {fStackSetName} StackSet")
	StackSetOpId = f"DeleteInstances-{random_string(5)}"
	if ((fAccountList is None or fAccountList == []) and fPermissionModel.upper() == 'SELF_MANAGED') or (fRegionList is None or fRegionList == []):
		logging.error(f"AccountList and RegionList cannot be null")
		logging.warning(f"AccountList: {fAccountList}")
		logging.warning(f"RegionList: {fRegionList}")
		# Note: The "Success" is True below to show that the calling function can move forward, even though the Account / Regions are null
		return_response = {'Success': True, 'ErrorMessage': "Failed - Account List or Region List was null"}
		return return_response
	elif fPermissionModel == 'SERVICE_MANAGED' and fDeploymentTargets is None:
		logging.error(f"You can't provide a stackset that is self-managed, and not supply the deployment targets it's supposed to delete")
		# Note: The "Success" is True below to show that the calling function can move forward, even though the Account / Regions are null
		return_response = {'Success': False, 'ErrorMessage': "Failed - StackSet is 'Service_Managed' but no deployment target was provided"}
		return return_response
	try:
		delete_stack_instance_response = delete_stack_instances3(faws_acct, fRegion, fRegionList, fStackSetName, fRetain, StackSetOpId,
		                                                                           fAccountList, fPermissionModel, fDeploymentTargets)
		if delete_stack_instance_response['Success']:
			return_response = {'Success': True, 'OperationId': delete_stack_instance_response['OperationId']}
		else:
			return_response = {'Success': False, 'ErrorMessage': delete_stack_instance_response['ErrorMessage']}
		return return_response
	except Exception as my_Error:
		logging.error(f"Error: {my_Error}")
		if my_Error.response['Error']['Code'] == 'StackSetNotFoundException':
			logging.info("Caught exception 'StackSetNotFoundException', ignoring the exception...")
			return_response = {'Success': False, 'ErrorMessage': "Failed - StackSet not found"}
			return return_response
		else:
			print("Failure to run: ", my_Error)
			return_response = {'Success': False, 'ErrorMessage': "Failed-Other"}
			return return_response


def _refresh_stacksets(StackSet_Dict: dict) -> dict:
	ApplicableStackSetsList = StackSet_Dict['ApplicableStackSetsList']
	RefreshOpsList = []
	cfn_client = aws_acct.session.client('cloudformation')
	print(f"Found {len(ApplicableStackSetsList)} stacksets that matched {pStackfrag}")
	print()
	for stackset in ApplicableStackSetsList:
		print(f"Beginning to refresh stackset {Fore.RED}{stackset}{Fore.RESET} as you requested...")
		# Get current attributes for the stacksets we've found...
		stacksetAttributes = cfn_client.describe_stack_set(StackSetName=stackset)
		# Then re-run those same stacksets, supplying the same information back to them -
		ReallyRefresh = (input(f"Refresh of {Fore.RED}{stackset}{Fore.RESET} has been requested.\n"
		                       f"Drift Status of the stackset is: {stacksetAttributes['StackSet']['StackSetDriftDetectionDetails']['DriftStatus']}\n"
		                       f"Are you still sure? (y/n): ") in ['y', 'Y']) if not pRetain else False
		if ReallyRefresh or pRetain:
			# WE have to separate the use-cases here, since the "Service Managed" update operation won't accept a "AdministrationRoleArn",
			# but the "Self Managed" *requires* it.
			if 'PermissionModel' in stacksetAttributes['StackSet'].keys() and stacksetAttributes['StackSet']['PermissionModel'] == 'SERVICE_MANAGED':
				refresh_stack_set = cfn_client.update_stack_set(StackSetName=stacksetAttributes['StackSet']['StackSetName'],
				                                                UsePreviousTemplate=True,
				                                                Capabilities=stacksetAttributes['StackSet']['Capabilities'],
				                                                OperationPreferences={
					                                                'RegionConcurrencyType'  : 'PARALLEL',
					                                                'FailureToleranceCount'  : 0,
					                                                'MaxConcurrentPercentage': 100
					                                                })
			else:
				refresh_stack_set = cfn_client.update_stack_set(StackSetName=stacksetAttributes['StackSet']['StackSetName'],
				                                                UsePreviousTemplate=True,
				                                                Capabilities=stacksetAttributes['StackSet']['Capabilities'],
				                                                OperationPreferences={
					                                                'RegionConcurrencyType'  : 'PARALLEL',
					                                                'FailureToleranceCount'  : 0,
					                                                'MaxConcurrentPercentage': 100
					                                                },
				                                                AdministrationRoleARN=stacksetAttributes['StackSet']['AdministrationRoleARN'],
				                                                )
			RefreshOpsList.append({'StackSetName': stackset,
			                       'OperationId' : refresh_stack_set['OperationId']})
	OperationResult = check_on_stackset_operations(RefreshOpsList, cfn_client)
	return OperationResult


def _add_instances_to_stacksets(StackSet_Dict: dict, accounts_to_add: list, regions_to_add: list = None) -> dict:
	ApplicableStackSetsList = StackSet_Dict['ApplicableStackSetsList']
	AddStacksList = []
	cfn_client = aws_acct.session.client('cloudformation')
	print(f"Found {len(ApplicableStackSetsList)} stacksets that matched {pStackfrag}")
	print()
	instances_to_add = (len(accounts_to_add) if accounts_to_add is not None else 1) * (len(regions_to_add) if regions_to_add is not None else 1)
	for stackset in ApplicableStackSetsList:
		ReallyAdd = False
		if not pConfirm:
			ReallyAdd = (input(f"{Fore.RED}Adding {instances_to_add} instances to {stackset}...{Fore.RESET}\n"
			                   f"Are you still sure? (y/n): ") in ['y', 'Y'])
		if pConfirm or ReallyAdd:
			OperationId = 'Add-Instances--' + random_string(6)
			# This is not wrapped in a try/except, because the "create_stack_instances" operation doesn't actually return anything useful.
			stackset_add = cfn_client.create_stack_instances(StackSetName=stackset,
			                                                 Accounts=accounts_to_add,
			                                                 Regions=RegionList,
			                                                 OperationPreferences={'RegionConcurrencyType'  : 'PARALLEL',
			                                                                       'MaxConcurrentPercentage': 100,
			                                                                       'FailureToleranceCount'  : 0},
			                                                 OperationId=OperationId,
			                                                 CallAs='SELF')
			AddStacksList.append({'StackSetName': stackset,
			                      'OperationId' : OperationId})
		else:
			print(f"{Fore.RED}Skipping {stackset}...{Fore.RESET}")
	OperationResult = check_on_stackset_operations(AddStacksList, cfn_client)
	return OperationResult


##########################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegion = args.Region
	pStackfrag = args.Fragments
	pExact = args.Exact
	pTiming = args.Time
	pAccountModifyList = args.Accounts
	verbose = args.loglevel
	pCheckAccount = args.AccountCheck
	pRole = args.AccessRole
	pdelete = args.DryRun
	pAddNew = args.AddNew
	pRetain = args.Retain
	pOperationDate = args.OperationDate
	pRegionModifyList = args.pRegionModifyList
	pRefresh = args.Refresh
	pConfirm = args.Confirm
	ChangesRequested = pdelete or pAddNew or pRefresh
	# pSaveFilename = args.Filename
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	# Setup the aws_acct object
	aws_acct, RegionList = setup_auth_and_regions(pProfile)
	# Collect the stacksets, AccountList and RegionList involved
	# StackSets, Accounts, Regions = collect_cfnstacksets(aws_acct, pRegion)
	StackSet_Info = collect_cfnstacksets(aws_acct, pRegion)
	# Once we have all the stacksets found, determine what to do with them...
	if ChangesRequested:
		operation_result = _modify_stacksets(StackSet_Info)
		ChangesMade = operation_result['ChangesMade']
	else:
		ChangesMade = False
	# Handle the checking of accounts to see if there any that don't belong in the Org.
	Account_Dict = {}
	if pCheckAccount:
		Account_Dict = check_accounts(aws_acct, StackSet_Info['FoundAccountList'])
	# If we changed anything, get a refreshed view before we display health of stacksets
	if ChangesRequested and ChangesMade:
		print()
		print(f"{Fore.RED}Since changes were requested, we're getting the updated view of the environment (post-changes){Fore.RESET}")
		print()
		StackSet_Info = collect_cfnstacksets(aws_acct, pRegion)
	# Display results
	# If the stacksets were found, but the account number they provided isn't in any of the stacksets found
	if len(StackSet_Info['ApplicableStackSetInstancesList']) == 0 and len(StackSet_Info['StackSetNames']['StackSets']) > 0:
		# print()
		print(f"While we found {len(StackSet_Info['ApplicableStackSetsList'])} stackset{'' if len(StackSet_Info['StackSetNames']['StackSets']) == 1 else 's'} that matched your request, "
		      f"we found no instances matching your criteria - {pRegionModifyList} - in them")
		ChangesMade = False
	# If the stacksets were not found...
	elif len(StackSet_Info['ApplicableStackSetsList']) == 0:
		print()
		print(f"We found no stacksets that matched your request... ")
		ChangesMade = False
	# If there is is nothing to display, the function below will print nothing, so it's safe to run it anyway...
	display_stack_set_health(StackSet_Info, Account_Dict)

	if ChangesRequested:
		if pAddNew:
			operation = 'add'
		elif pdelete:
			operation = 'delete'
		elif pRefresh:
			operation = 'refresh'
		if ChangesMade:
			print(f"Results of {operation} operation on {len(operation_result) - 1} stackset{'' if len(operation_result) == 1 else 's'} found with {pStackfrag} fragment:")
			for k, v in operation_result.items():
				if k == 'ChangesMade':
					continue
				else:
					print(f"\t{Fore.RED if v == 'FAILED' else ''}{k}: {v} {Fore.RESET}")
		else:
			print(f"While a {Fore.RED}{operation}{Fore.RESET} was requested, no stacksets were found matching your naming criteria {Fore.RED}{pStackfrag}{Fore.RESET}, "
			      f"the accounts you wanted {Fore.RED}{'[all]' if pAccountModifyList is None else pAccountModifyList}{Fore.RESET} and the regions you specified "
			      f"{Fore.RED}{'[all]' if pRegionModifyList is None else pRegionModifyList}{Fore.RESET}, so no changes were made.")
		print()

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thanks for using this script...")
print()
