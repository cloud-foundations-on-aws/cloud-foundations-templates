#!/usr/bin/env python3
import sys
import os

import Inventory_Modules
from Inventory_Modules import display_results, get_all_credentials
from ArgumentsClass import CommonArguments
# from datetime import datetime
from colorama import init, Fore
from botocore.exceptions import ClientError
from queue import Queue
from threading import Thread
from time import time

import logging

init()

__version__ = '2024.10.24'

##################
# Functions
##################

def parse_args(f_args):
	"""
	Description: Parses the arguments passed into the script
	@param f_args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	script_path, script_name = os.path.split(sys.argv[0])
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--ipaddress", "--ip",
		dest="pipaddresses",
		nargs="*",
		metavar="IP address",
		default=None,
		help="IP address(es) you're looking for within your accounts")
	return parser.my_parser.parse_args(f_args)


def check_accounts_for_enis(fCredentialList, fip=None):
	"""
	Note that this function takes a list of Credentials and checks for ENIs in every account and region it has creds for
	"""

	class FindENIs(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_region, c_fip, c_PlacesToLook, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					account_enis = Inventory_Modules.find_account_enis2(c_account_credentials, c_region, c_fip)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']} in region {c_region}")
					for eni in account_enis:
						eni['MgmtAccount'] = c_account_credentials['MgmtAccount']
					Results.extend(account_enis)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					print(f"{ERASE_LINE}Finished finding ENIs in account {c_account_credentials['AccountId']} in region {c_region} - {c_PlaceCount} / {c_PlacesToLook}", end='\r')
					self.queue.task_done()

	checkqueue = Queue()

	Results = []
	PlaceCount = 0
	PlacesToLook = WorkerThreads = min(len(fCredentialList), 50)

	for x in range(WorkerThreads):
		worker = FindENIs(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in fCredentialList:
		logging.info(f"Connecting to account {credential['AccountId']} in region {credential['Region']}")
		try:
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			checkqueue.put((credential, credential['Region'], fip, PlacesToLook, PlaceCount))
			PlaceCount += 1
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return Results


def present_results(f_ENIsFound: list):
	"""
	Description: Presents results at the end of the script
	@param f_ENIsFound: The list of records to show...
	"""
	display_dict = {'MgmtAccount'     : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'       : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'          : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'PrivateDnsName'  : {'DisplayOrder': 4, 'Heading': 'ENI Name'},
	                'Status'          : {'DisplayOrder': 5, 'Heading': 'Status', 'Condition': ['available', 'attaching', 'detaching']},
	                'PublicIp'        : {'DisplayOrder': 6, 'Heading': 'Public IP Address'},
	                'ENIId'           : {'DisplayOrder': 7, 'Heading': 'ENI Id'},
	                'PrivateIpAddress': {'DisplayOrder': 8, 'Heading': 'Assoc. IP'}}

	sorted_ENIs_Found = sorted(f_ENIsFound, key=lambda d: (d['MgmtAccount'], d['AccountId'], d['Region'], d['VpcId']))
	display_results(sorted_ENIs_Found, display_dict, 'None', pFilename)

	DetachedENIs = [x for x in sorted_ENIs_Found if x['Status'] in ['available', 'attaching', 'detaching']]
	RegionList = list(set([x['Region'] for x in CredentialList]))
	AccountList = list(set([x['AccountId'] for x in CredentialList]))

	print()
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
	print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
	print()
	# print(f"Your output will be saved to {Fore.GREEN}'{pFilename}-{datetime.now().strftime('%y-%m-%d--%H:%M:%S')}'{Fore.RESET}") if pFilename is not None else ""
	print(f"The output has also been written to a file beginning with '{pFilename}' + the date and time") if pFilename is not None else ""
	print(f"Found {len(f_ENIsFound)} ENIs across {len(AccountList)} accounts across {len(RegionList)} regions")
	print(f"{Fore.RED}Found {len(DetachedENIs)} ENIs that are not listed as 'in-use' and may therefore be costing you additional money while they're unused.{Fore.RESET}")
	print()
	if verbose < 40:
		for x in DetachedENIs:
			print(x)


##################
# Main
##################

ERASE_LINE = '\x1b[2K'

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccounts = args.Accounts
	pRootOnly = args.RootOnly
	pIPaddressList = args.pipaddresses
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
	print()
	print(f"Checking for Elastic Network Interfaces... ")
	print()

	logging.info(f"Profiles: {pProfiles}")

	# Get credentials for all relevant children accounts
	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)

	# Find ENIs across all children accounts
	ENIsFound = check_accounts_for_enis(CredentialList, fip=pIPaddressList)
	# Display results
	present_results(ENIsFound)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thank you for using this script")
print()
