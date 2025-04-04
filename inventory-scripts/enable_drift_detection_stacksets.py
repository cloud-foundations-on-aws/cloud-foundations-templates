#!/usr/bin/env python3


import logging
import sys
from os.path import split
from datetime import datetime
from botocore.exceptions import ClientError
from time import time
from colorama import Fore, init

import Inventory_Modules
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results
from account_class import aws_acct_access

init()
__version__ = "2024.03.06"
begin_time = time()
sleep_interval = 5


def parse_args(args):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()
	parser.singleregion()
	parser.extendedargs()
	parser.fragment()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-s", "--status",
		dest="pstatus",
		metavar="CloudFormation status",
		default="active",
		help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too")
	local.add_argument(
		"+enable",
		dest="pEnable",
		action="store_true",
		help="Flag that determines whether we run drift_detection on those stacksets that haven't had it run in <xx> number of days")
	local.add_argument(
		"--days_since", "--ds",
		dest="pDaysSince",
		metavar="Number of days old",
		type=int,
		default=15,
		help="Days since the drift_status was checked, to be acceptable")
	return parser.my_parser.parse_args(args)


def setup_auth(fProfile: str) -> aws_acct_access:
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@return:
		- an object of the type "aws_acct_access"
		- a list of regions valid for this particular profile/ account.
	"""
	try:
		aws_acct = aws_acct_access(fProfile)
	except ConnectionError as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	if not aws_acct.Success:
		print(f"{Fore.RED}Profile {pProfile} failed to access an account. Check credentials and try again{Fore.RESET}")
		sys.exit(99)

	print()
	print(f"You asked me to display drift detection status on stacksets that match the following:")
	print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
	print(f"\t\tIn this Region: {pRegion}")

	if pExact:
		print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET}: {pFragments}")
	else:
		print(f"\t\tFor stacksets that contain th{'is fragment' if len(pFragments) == 1 else 'ese fragments'}: {pFragments}")
	print(f"\t\tand enable drift detection on those stacksets, if they're not current") if pEnableDriftDetection else ''

	print()
	return aws_acct


def find_stack_sets(faws_acct: aws_acct_access, fStackSetFragmentlist: list = None, fExact: bool = False) -> dict:
	if fStackSetFragmentlist is None:
		fStackSetFragmentlist = ['all']
	StackSets = {'Success': False, 'ErrorMessage': '', 'StackSets': {}}
	try:
		StackSets = Inventory_Modules.find_stacksets3(faws_acct, faws_acct.Region, fStackSetFragmentlist, fExact, True)
	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			error_message = f"{aws_acct.acct_number}: Authorization Failure"
			logging.error(error_message)
		else:
			error_message = f"Error: {my_Error}"
			logging.error(error_message)
		StackSets['ErrorMessage'] = error_message
	except Exception as my_Error:
		error_message = f"Error: {my_Error}"
		logging.error(error_message)
		StackSets['ErrorMessage'] = error_message
	return StackSets


def enable_stack_set_drift_detection(faws_acct: aws_acct_access, fStackSets: dict = None):
	from queue import Queue
	from threading import Thread
	from time import sleep

	class UpdateDriftDetection(Thread):
		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				c_aws_acct, c_stackset_name = self.queue.get()
				logging.info(f"De-queued info for account {c_aws_acct.acct_number}")
				try:
					logging.info(f"Attempting to run drift_detection on {c_stackset_name['StackSetName']}")
					client = c_aws_acct.session.client('cloudformation')
					logging.info(f"Enabling Drift Detection for {c_stackset_name['StackSetName']}")
					DD_Operation = Inventory_Modules.enable_drift_on_stackset3(c_aws_acct, c_stackset_name['StackSetName'])
					intervals_waited = 1
					sleep(sleep_interval)
					Status = client.describe_stack_set_operation(StackSetName=c_stackset_name['StackSetName'], OperationId=DD_Operation['OperationId'])
					while Status['StackSetOperation']['Status'] in ['RUNNING']:
						Status = client.describe_stack_set_operation(StackSetName=c_stackset_name['StackSetName'], OperationId=DD_Operation['OperationId'])
						sleep(sleep_interval)
						print(f"{ERASE_LINE}Waiting for {c_stackset_name['StackSetName']} to finish drift detection",
						      f"{sleep_interval * intervals_waited} seconds waited so far", end='\r')
						intervals_waited += 1
						logging.info(f"Sleeping to allow {c_stackset_name['StackSetName']} to continue drift detection")
					if Status['Status'] in ['FAILED']:
						fStackSets['Success'] = False
						fStackSets['ErrorMessage'] = Status['StackSetOperation']['StackSetDriftDetectionDetails']
					else:
						fStackSets['Success'] = True
				except TypeError as my_Error:
					logging.info(f"Error: {my_Error}")
					continue
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"Account {c_aws_acct.acct_number}: Authorization Failure")
					continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_aws_acct.acct_number}")
					logging.info(f"Actual Error: {my_Error}")
					continue
				finally:
					# fStackSets[c_stackset_name]['AccountId'] = c_aws_acct.acct_number
					# fStackSets[c_stackset_name]['Region'] = c_aws_acct.Region
					self.queue.task_done()

	WorkerThreads = min(len(fStackSets), 25)

	checkqueue = Queue()

	for x in range(WorkerThreads):
		worker = UpdateDriftDetection(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for stackset in fStackSets:
		logging.info(f"Connecting to account {faws_acct.acct_number}")
		try:
			print(f"{ERASE_LINE}Queuing stackset {stackset['StackSetName']} in account {faws_acct.acct_number} in region {faws_acct.Region}", end='\r')
			checkqueue.put((faws_acct, stackset))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {faws_acct.acct_number} in {faws_acct.Region} region")
				logging.error(f"It's possible that the region {faws_acct.Region} hasn't been opted-into")
				pass
	checkqueue.join()
	return fStackSets


def days_between_dates(fdate1: datetime, fdays_since: int):
	from dateutil.tz import tzutc

	# Ensure that the input parameter is a datetime object
	if fdate1 is None:
		response = {'Current': False, 'ErrorMessage': 'Drift Status never checked'}
		return response
	elif not isinstance(fdate1, datetime):
		raise ValueError("Date passed in should be datetime object")

	# Calculate the difference between the two dates
	date_difference = abs(datetime.now(tzutc()) - fdate1)

	# Extract the number of days from the timedelta object
	number_of_days = date_difference.days
	if number_of_days <= fdays_since:
		response = {'Current': True, 'NumberOfDays': number_of_days}
	else:
		response = {'Current': False, 'NumberOfDays': number_of_days}

	return response


##################
# Main
##################
if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegion = args.Region
	pFragments = args.Fragments
	pExact = args.Exact
	pDaysSince = args.pDaysSince
	pstatus = args.pstatus
	pFilename = args.Filename
	pEnableDriftDetection = args.pEnable
	pTiming = args.Time
	AccountsToSkip = args.SkipAccounts
	ProfilesToSkip = args.SkipProfiles
	pAccounts = args.Accounts
	pSaveFilename = args.Filename
	verbose = args.loglevel

	# Set Log Level
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)
	"""
	We should eventually create an argument here that would check on the status of the drift-detection using
	"describe_stack_drift_detection_status", but we haven't created that function yet... 
	https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_drift_detection_status
	"""

	##########################
	ERASE_LINE = '\x1b[2K'

	# Setup the aws_acct object, and the list of Regions
	aws_acct = setup_auth(pProfile)

	display_dict_stacksets = {'AccountNumber'            : {'DisplayOrder': 1, 'Heading': 'Acct Number'},
	                          'Region'                   : {'DisplayOrder': 2, 'Heading': 'Region'},
	                          'StackSetName'             : {'DisplayOrder': 3, 'Heading': 'Stack Set Name'},
	                          'Status'                   : {'DisplayOrder': 4, 'Heading': 'Stack Status'},
	                          'Stack_Instances_number'   : {'DisplayOrder': 5, 'Heading': '# of Instances'},
	                          'DriftStatus'              : {'DisplayOrder': 6, 'Heading': 'Drift Status'},
	                          'LastDriftCheckTimestamp'  : {'DisplayOrder': 7, 'Heading': 'Date Drift Checked'},
	                          'NeedsDriftDetectionUpdate': {'DisplayOrder': 8, 'Heading': 'Needs update', 'Condition': [True]}}

	# RegionList = Inventory_Modules.get_service_regions('cloudformation', pRegionList)

	# Find StackSets to operate on and get the last detection status
	StackSets = find_stack_sets(aws_acct, pFragments, pExact)
	StackSetsList = [item for key, item in StackSets['StackSets'].items()]
	for item in StackSetsList:
		item['AccountNumber'] = aws_acct.acct_number
		item['Region'] = aws_acct.Region
	sorted_all_stacksets = sorted(StackSetsList, key=lambda x: (x['StackSetName']))
	for item in sorted_all_stacksets:
		if ('LastDriftCheckTimestamp' not in item.keys() or not days_between_dates(item['LastDriftCheckTimestamp'], pDaysSince)['Current']) and item.get('Stack_Instances_number',0) > 0:
			item['NeedsDriftDetectionUpdate'] = True
		else:
			item['NeedsDriftDetectionUpdate'] = False
	display_results(sorted_all_stacksets, display_dict_stacksets, None, pSaveFilename)
	# Enable drift_detection on those stacksets
	DriftDetectionNeededStacksets = [item for item in StackSetsList if item['NeedsDriftDetectionUpdate']]
	if len(DriftDetectionNeededStacksets) == 0:
		print()
		print(f"The stacksets found all fall within current guidelines. No additional drift detection is necessary.")
		print()
		ReallyDetectDrift = False
	else:
		StackSetNamesThatNeededDriftDetection = [item['StackSetName'] for item in DriftDetectionNeededStacksets]
		if verbose == logging.INFO:
			print(f"The following stacksets haven't been updated in at least {pDaysSince} days, and therefore need to be updated:")
			for stackname in StackSetNamesThatNeededDriftDetection:
				print(f"\t{stackname}")
		ReallyDetectDrift = input(f"Do you want to enable drift detection on th{'is' if len(DriftDetectionNeededStacksets) == 1 else 'ese'} {len(DriftDetectionNeededStacksets)} stackset{' that is not' if len(DriftDetectionNeededStacksets) == 1 else 's that are not'} current? (y/n)") in ['Y', 'y']
	if ReallyDetectDrift:
		Drift_Status = enable_stack_set_drift_detection(aws_acct, DriftDetectionNeededStacksets)
		StackSets = find_stack_sets(aws_acct, StackSetNamesThatNeededDriftDetection, True)
		# Determine whether we want to update this status or not -
		StackSetsList = [item for key, item in StackSets['StackSets'].items()]
		sorted_all_stacksets = sorted(StackSetsList, key=lambda x: (x['StackSetName']))
		# Display results
		display_results(sorted_all_stacksets, display_dict_stacksets, None, pSaveFilename)

	print(ERASE_LINE)
	print(f"{Fore.RED}Looked through {len(sorted_all_stacksets)} StackSets across the {pRegion} region{Fore.RESET}")
	print()

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.3f} seconds{Fore.RESET}")
	print("Thanks for using this script...")
	print()
