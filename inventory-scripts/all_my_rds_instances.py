#!/usr/bin/env python3

# import boto3
import sys
import Inventory_Modules
from Inventory_Modules import display_results, get_all_credentials, find_account_rds_instances2
from ArgumentsClass import CommonArguments
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import time
from colorama import init, Fore
from botocore.exceptions import ClientError

import logging

init()

__version__ = '2025.04.09'


##################
# Functions
##################

def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all rds instances within any of the accounts we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rolestouse()
	parser.rootOnly()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	return parser.my_parser.parse_args(args)


def uniquify_list(non_unique_list: list) -> list:
	"""
	Description: This function takes a list of results and returns a list of unique results
	@param non_unique_list: source list
	@return: list of unique results
	"""
	unique_ids = []
	unique_items = []
	for item in non_unique_list:
		if item['DBId'] not in unique_ids:
			unique_ids.append(item['DBId'])
			unique_items.append(item)
	return unique_items

def check_accounts_for_instances(fAllCredentials: list) -> list:
	"""
	Description: Note that this function checks the account AND any children accounts in the Org.
	@param faws_acct: the well-known account class object
	@param fRegionList: listing of regions to look in
	@return: The list of RDS instances found
	"""

	class FindRDSInstances(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					# Now go through those stacksets and determine the instances, made up of accounts and regions
					# Most time spent in this loop
					DBInstances = find_account_rds_instances2(c_account_credentials)
					logging.info(f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(DBInstances['DBInstances'])} RDS instances")
					if 'DBInstances' in DBInstances.keys():
						for RDSinstance in DBInstances['DBInstances']:
							Name = RDSinstance['DBName'] if 'DBName' in RDSinstance.keys() else 'No Name'
							LastBackup = RDSinstance['LatestRestorableTime'] if 'LatestRestorableTime' in RDSinstance.keys() else 'No Backups'
							AllRDSInstances.append({
								'MgmtAccount'  : c_account_credentials['MgmtAccount'],
								'AccountNumber': c_account_credentials['AccountId'],
								'Region'       : c_account_credentials['Region'],
								'InstanceType' : RDSinstance['DBInstanceClass'],
								'State'        : RDSinstance['DBInstanceStatus'],
								'DBId'         : RDSinstance['DBInstanceIdentifier'],
								'Name'         : Name,
								'Size'         : RDSinstance['AllocatedStorage'],
								'LastBackup'   : LastBackup,
								'Engine'       : RDSinstance['Engine']
								})
					else:
						continue
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
					if my_Error.response['Error']['Code'] == 'AccessDenied':
						logging.warning(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's likely there's an SCP blocking access to this {c_account_credentials['AccountId']} account")
						continue
					else:
						logging.error(f"Error: Likely throttling errors from too much activity")
						logging.warning(my_Error)
						continue
				finally:
					pbar.update()
					self.queue.task_done()

	checkqueue = Queue()

	AllRDSInstances = []
	WorkerThreads = min(len(fAllCredentials), 25)

	pbar = tqdm(desc=f'Finding RDS instances from {len(fAllCredentials)} locations with {WorkerThreads} threads',
	            total=len(fAllCredentials), unit=' location'
	            )

	for x in range(WorkerThreads):
		worker = FindRDSInstances(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in fAllCredentials:
		logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			checkqueue.put((credential))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllRDSInstances


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
	pRootOnly = args.RootOnly
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel

	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	ERASE_LINE = '\x1b[2K'
	begin_time = time()
	logging.info(f"Profiles: {pProfiles}")

	print()
	print(f"Checking for rds instances... ")
	print()

	AllChildAccounts = []

	# Display RDS Instances found
	display_dict = {'MgmtAccount'  : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountNumber': {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'       : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'InstanceType' : {'DisplayOrder': 4, 'Heading': 'Instance Type'},
	                'Name'         : {'DisplayOrder': 5, 'Heading': 'DB Name'},
	                'DBId'         : {'DisplayOrder': 6, 'Heading': 'Database ID'},
	                'Engine'       : {'DisplayOrder': 7, 'Heading': 'DB Engine'},
	                'Size'         : {'DisplayOrder': 8, 'Heading': 'Size (GB)'},
	                'LastBackup'   : {'DisplayOrder': 9, 'Heading': 'Latest Backup'},
	                'State'        : {'DisplayOrder': 10, 'Heading': 'State', 'Condition': ['Failed', 'Deleting', 'Maintenance', 'Rebooting', 'Upgrading']}}

	# Get credentials
	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles)
	AccountNum = len(set([acct['AccountId'] for acct in CredentialList]))
	RegionNum = len(set([acct['Region'] for acct in CredentialList]))

	# Get RDS Instances
	InstancesFound = check_accounts_for_instances(CredentialList)
	sorted_results = sorted(InstancesFound, key=lambda d: (d['MgmtAccount'], d['AccountNumber'], d['Region'], d['DBId']))
	unique_results = uniquify_list(sorted_results)
	# Display results
	display_results(unique_results, display_dict, None, pFilename)

	print(ERASE_LINE)
	print(f"Found {len(unique_results)} instances across {AccountNum} account{'' if AccountNum == 1 else 's'} across {RegionNum} region{'' if RegionNum == 1 else 's'}")
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print()
	print("Thank you for using this script")
	print()
