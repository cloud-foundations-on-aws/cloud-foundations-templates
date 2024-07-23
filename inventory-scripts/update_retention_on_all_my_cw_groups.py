#!/usr/bin/env python3

import sys
from os.path import split
from Inventory_Modules import display_results, find_cw_groups_retention2, get_all_credentials
from ArgumentsClass import CommonArguments
from colorama import init, Fore
from time import time
from threading import Thread
from queue import Queue
from tqdm.auto import tqdm
from botocore.exceptions import ClientError

import logging

init()
__version__ = "2024.05.10"
ERASE_LINE = '\x1b[2K'
begin_time = time()


##################
# Functions
##################
def parse_args(f_arguments):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.rolestouse()
	parser.save_to_file()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')

	local.add_argument(
		'+R', "--ReplaceRetention",
		help="The retention you want to update to on all groups that match.",
		default=None,
		metavar="retention days",
		type=int,
		choices=[0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 2192, 2557, 2922, 3288, 3653],
		dest="pRetentionDays")
	local.add_argument(
		'-o', "--OldRetention",
		help="The retention you want to change on all groups that match. Use '0' for 'Never'",
		default=None,
		metavar="retention days",
		type=int,
		choices=[0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 2192, 2557, 2922, 3288, 3653],
		dest="pOldRetentionDays")
	return parser.my_parser.parse_args(f_arguments)


def check_cw_groups_retention(f_all_credential_list: list) -> list:
	"""
	This function will check the retention on all CW Groups in all accounts.
	@param f_all_credential_list: Listing of all credentials for accounts we'll look into
	@return: Returns a list of all CW Groups in all accounts provided by the credentials submitted.
	"""

	class FindCWGroups(Thread):
		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				pbar.update()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					CW_Groups = find_cw_groups_retention2(c_account_credentials)
					if len(CW_Groups) > 0:
						for logGroup in CW_Groups:
							if 'retentionInDays' in logGroup.keys():
								logGroup['Retention'] = logGroup['retentionInDays']
							else:
								logGroup['Retention'] = "Never"
							logGroup['Name'] = logGroup['logGroupName']
							logGroup['Size'] = logGroup['storedBytes']
							logGroup['AccessKeyId'] = c_account_credentials['AccessKeyId']
							logGroup['SecretAccessKey'] = c_account_credentials['SecretAccessKey']
							logGroup['SessionToken'] = c_account_credentials['SessionToken']
							logGroup['ParentProfile'] = c_account_credentials['Profile'] if c_account_credentials['Profile'] is not None else 'default'
							logGroup['MgmtAccount'] = c_account_credentials['MgmtAccount']
							logGroup['AccountId'] = c_account_credentials['AccountId']
							logGroup['Region'] = c_account_credentials['Region']
						AllCWLogGroups.extend(CW_Groups)

				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong")
					logging.warning(my_Error)
					continue
				except ClientError as my_Error:
					if 'AuthFailure' in str(my_Error):
						logging.error(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into")
						continue
					else:
						logging.error(f"Error: Likely throttling errors from too much activity")
						logging.warning(my_Error)
						continue
				finally:
					self.queue.task_done()

	checkqueue = Queue()

	AllCWLogGroups = []
	WorkerThreads = min(len(f_all_credential_list), 25)
	WorkerThreads = min(len(f_all_credential_list), 1)

	pbar = tqdm(desc=f'Finding CloudWatch log groups from {len(f_all_credential_list)} accounts / regions',
	            total=len(f_all_credential_list), unit=' locations'
	            )

	for x in range(WorkerThreads):
		worker = FindCWGroups(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in f_all_credential_list:
		logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
		try:
			# While double parens are necessary below, if you're queuing multiple values, we're only queuing one right now.
			# But if/ when we add fragment finding, I'm leaving this comment here to remind myself of that.
			# checkqueue.put((credential))
			checkqueue.put(credential)
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllCWLogGroups


def update_cw_groups_retention(fCWGroups: list, fOldRetentionDays: int = None, fRetentionDays: int = None):
	import boto3

	if fOldRetentionDays is None:
		fOldRetentionDays = 0
	Success = True
	for item in fCWGroups:
		cw_session = boto3.Session(aws_access_key_id=item['AccessKeyId'],
		                           aws_secret_access_key=item['SecretAccessKey'],
		                           aws_session_token=item['SessionToken'],
		                           region_name=item['Region'])
		cw_client = cw_session.client('logs')
		logging.info(f"Connecting to account {item['AccountId']}")
		try:
			print(f"{ERASE_LINE}Updating log group {item['logGroupName']} account {item['AccountId']} in region {item['Region']}", end='\r')
			if 'retentionInDays' not in item.keys():
				retentionPeriod = 'Never'
			else:
				retentionPeriod = item['retentionInDays']
			if (fOldRetentionDays == 0 and 'retentionInDays' not in item.keys()) or retentionPeriod == fOldRetentionDays:
				result = cw_client.put_retention_policy(
					logGroupName=item['logGroupName'],
					retentionInDays=fRetentionDays
					)
				print(f"Account: {item['AccountId']} in Region: {item['Region']} updated {item['logGroupName']} from {retentionPeriod} to {fRetentionDays} days")
				Updated = True
			else:
				Updated = False
				logging.info(f"Skipped {item['logGroupName']} in account: {item['AccountId']} in Region: {item['Region']} as it didn't match criteria")
			Success = True
		except ClientError as my_Error:
			logging.error(my_Error)
			Success = False
			return Success
	return Success


##################
# Main
##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfiles = args.Profiles
	pRegionList = args.Regions
	pAccounts = args.Accounts
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccessRoles = args.AccessRoles
	pRetentionDays = args.pRetentionDays
	pOldRetentionDays = args.pOldRetentionDays
	pRootOnly = args.RootOnly
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	print()
	print(f"Checking for CW Log Groups... ")
	print()

	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles)
	SuccessfulAccountAccesses = [x for x in CredentialList if x['Success']]
	AllChildAccounts = list(set([(x['MgmtAccount'], x['AccountId']) for x in SuccessfulAccountAccesses]))
	RegionList = list(set([x['Region'] for x in SuccessfulAccountAccesses]))

	display_dict = {
		# 'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'},
	                'MgmtAccount'  : {'DisplayOrder': 2, 'Heading': 'Mgmt Acct'},
	                'AccountId'    : {'DisplayOrder': 3, 'Heading': 'Acct Number'},
	                'Region'       : {'DisplayOrder': 4, 'Heading': 'Region'},
	                'Retention'    : {'DisplayOrder': 5, 'Heading': 'Days Retention', 'Condition': ['Never']},
	                'Name'         : {'DisplayOrder': 7, 'Heading': 'CW Log Name'},
	                'Size'         : {'DisplayOrder': 6, 'Heading': 'Size (Bytes)'}}

	CWGroups = check_cw_groups_retention(CredentialList)
	sorted_CWGroups = sorted(CWGroups, key=lambda k: (k['MgmtAccount'], k['AccountId'], k['Region'], k['Name']))

	display_results(sorted_CWGroups, display_dict, None, pFilename)

	print(ERASE_LINE)
	totalspace = 0
	for i in CWGroups:
		totalspace += i['storedBytes']
	print(f"Found {len(CWGroups)} log groups across {len(AllChildAccounts)} accounts across {len(RegionList)} regions, representing {totalspace / 1024 / 1024 / 1024:,.3f} GB")
	print(f"To give you a small idea - in us-east-1 - it costs $0.03 per GB per month to store (after 5GB).")
	if totalspace / 1024 / 1024 / 1024 <= 5.0:
		print("Which means this is essentially free for you...")
	else:
		print(f"This means you're paying about ${((totalspace / 1024 / 1024 / 1024) - 5) * 0.03:,.2f} per month in CW storage charges")

	if pRetentionDays is not None:
		print(f"As per your request - updating ALL retention periods to {pRetentionDays} days")
		print(f"")
		UpdateAllRetention = input(f"This is definitely an intrusive command, so please confirm you want to do this (y/n): ") in ['Y', 'y']
		if UpdateAllRetention:
			print(f"Updating all log groups to have a {pRetentionDays} retention period")
			update_cw_groups_retention(CWGroups, pOldRetentionDays, pRetentionDays)
		else:
			print(f"No changes made")
	print()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print()
	print("Thank you for using this script")
	print()
