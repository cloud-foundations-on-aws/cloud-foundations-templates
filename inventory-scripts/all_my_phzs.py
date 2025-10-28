#!/usr/bin/env python3

import logging
import sys

from queue import Queue
from threading import Thread
from time import time
from botocore.exceptions import ClientError
from colorama import Fore, init
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, find_private_hosted_zones2, get_all_credentials

init()
__version__ = "2025.03.09"
ERASE_LINE = '\x1b[2K'


########################
# Functions
########################

def parse_args(f_args):
	parser = CommonArguments()
	parser.multiprofile()
	parser.extendedargs()
	parser.rootOnly()
	parser.save_to_file()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	return parser.my_parser.parse_args(f_args)


def find_all_hosted_zones(fAllCredentials):
	class FindZones(Thread):
		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					HostedZones = find_private_hosted_zones2(c_account_credentials, c_account_credentials['Region'])
					logging.info(f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(HostedZones['HostedZones'])} zones")

					if len(HostedZones['HostedZones']) > 0:
						for zone in HostedZones['HostedZones']:
							ThreadedHostedZones.append({
								'ParentProfile': c_account_credentials['ParentProfile'],
								'MgmtAccount'  : c_account_credentials['MgmtAccount'],
								'AccountId'    : c_account_credentials['AccountId'],
								'Region'       : 'Global',
								'PHZName'      : zone['Name'],
								'Records'      : zone['ResourceRecordSetCount'],
								'PHZId'        : zone['Id']
								})
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error("Error: Likely that one of the supplied profiles was wrong")
					logging.warning(my_Error)
					continue
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into")
						logging.warning(my_Error)
						continue
					else:
						logging.error("Error: Likely throttling errors from too much activity")
						logging.warning(my_Error)
						continue
				finally:
					self.queue.task_done()

	checkqueue = Queue()
	ThreadedHostedZones = []
	WorkerThreads = min(len(fAllCredentials), 25)

	for x in range(WorkerThreads):
		worker = FindZones(checkqueue)
		worker.daemon = True
		worker.start()

	for credential in fAllCredentials:
		logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
		try:
			checkqueue.put((credential))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} region")
				# logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return ThreadedHostedZones


########################
# Main
########################

if __name__ == "__main__":
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pSkipProfiles = args.SkipProfiles
	pSkipAccounts = args.SkipAccounts
	pRootOnly = args.RootOnly
	pAccounts = args.Accounts
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	begin_time = time()
	# Get Credentials
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts)
	AllAccountList = list(set([x['AccountId'] for x in AllCredentials]))
	# Find the hosted zones
	AllHostedZones = find_all_hosted_zones(AllCredentials)
	# Display results
	print()

	display_dict = {
		# 'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'},
		'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
		'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
		'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
		'PHZName'    : {'DisplayOrder': 4, 'Heading': 'Zone Name'},
		'Records'    : {'DisplayOrder': 5, 'Heading': '# of Records'},
		'PHZId'      : {'DisplayOrder': 6, 'Heading': 'Zone ID'}
		}
	sorted_results = sorted(AllHostedZones, key=lambda x: (x['ParentProfile'], x['MgmtAccount'], x['AccountId'], x['PHZName'], x['Region']))
	display_results(sorted_results, display_dict, None, pFilename)

	print(f"{Fore.RED}Found {len(AllHostedZones)} Hosted Zones across {len(AllAccountList)} accounts globally{Fore.RESET}")
	print()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
		print(ERASE_LINE)
	print("Thanks for using this script...")
	print()
