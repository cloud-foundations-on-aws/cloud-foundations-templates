#!/usr/bin/env python3


from time import time
from os.path import split
import sys
from colorama import init, Fore
from botocore.exceptions import ClientError

from Inventory_Modules import display_results, get_all_credentials, find_global_accelerators2
from ArgumentsClass import CommonArguments
from threading import Thread
from queue import Queue
from tqdm.auto import tqdm

import logging

init()
__version__ = "2025.03.27"
ERASE_LINE = '\x1b[2K'
begin_time = time()


##################
# Functions
##################

def parse_args(arguments):
	"""
	Description: Parses the arguments passed into the script
	@param arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.my_parser.description = (f"We're going to find all global accelerators within any of the accounts we have access to, given the profile(s) provided.\n"
	                                f"Please note that since this is a global service, there's no way to provide the region to look in.")
	parser.multiprofile()
	parser.extendedargs()
	parser.rootOnly()
	parser.rolestouse()
	parser.save_to_file()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-s", "--status",
		dest="pstatus",
		metavar="Global Accelerator Status",
		choices=['DEPLOYED', 'IN_PROGRESS', 'all'],
		default="all",
		help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too")
	return parser.my_parser.parse_args(arguments)


def find_all_global_accelerators(fAllCredentials: list):
	"""
	Description: Finds all the load balancers in the Profile(s)
	@param fAllCredentials: List of credentials to some number of accounts
	@return: List of global accelerators
	"""

	class FindGlobalAccelerators(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			from itertools import chain

			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					GlobalAccelerators = find_global_accelerators2(c_account_credentials)
					logging.info(f"Account: {c_account_credentials['AccountId']} | Found {len(GlobalAccelerators)} global accelerators")
					for ga in GlobalAccelerators:
						All_Global_Accelerators.append({
							'MgmtAccount': c_account_credentials['MgmtAccount'],
							'AccountId'  : c_account_credentials['AccountId'],
							'Region'     : 'Global',
							'Enabled'    : ga['Enabled'],
							'IpSets'     : ga['IpSets'],
							'IpAddresses': list(chain(*[_['IpAddresses'] for _ in ga['IpSets']])),
							'Name'       : ga['Name'],
							'Status'     : ga['Status'],
							'DNSName'    : ga['DnsName'],
							'Listeners'  : []})
						for listener in ga['Listeners']:
							All_Global_Accelerators[-1]['Listeners'].append(listener)
				except KeyError as my_Error:
					logging.error(f"KeyError failure - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong")
					logging.warning(f"Actual Error: {my_Error}")
					continue
				except ClientError as my_Error:
					if my_Error.response['Error']['Code'] == 'AccessDeniedException':
						logging.error(f"Access Denied Error: {my_Error}")
						continue
					if "AuthFailure" in str(my_Error):
						logging.error(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into")
						continue
					else:
						logging.error(f"Error: Likely throttling errors from too much activity")
						logging.warning(f"Actual Error: {my_Error}")
						continue
				finally:
					logging.info(f"Finished finding gas in account {c_account_credentials['AccountId']}")
					pbar.update()
					self.queue.task_done()

	###########

	checkqueue = Queue()
	All_Global_Accelerators = []
	WorkerThreads = min(len(fAllCredentials), 4)

	pbar = tqdm(desc=f"Finding global accelerators from {len(fAllCredentials)} account{'' if len(fAllCredentials) == 1 else 's'}",
	            total=len(fAllCredentials), unit=' ga'
	            )

	for x in range(WorkerThreads):
		worker = FindGlobalAccelerators(checkqueue)
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
	return All_Global_Accelerators


##################
# Main
##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = ['us-west-2']
	pAccounts = args.Accounts
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccessRoles = args.AccessRoles
	pFilename = args.Filename
	pStatus = args.pstatus
	pRootOnly = args.RootOnly
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	display_dict = {'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                # 'Region'       : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'Name'       : {'DisplayOrder': 4, 'Heading': 'Name'},
	                'Status'     : {'DisplayOrder': 5, 'Heading': 'Status'},
	                'DNSName'    : {'DisplayOrder': 6, 'Heading': 'Public Name'},
	                # 'IpAddresses'  : {'DisplayOrder': 7, 'Heading': 'IP Addresses'},
	                'Listeners'  : {'DisplayOrder': 8, 'Heading': 'Listeners'},
	                # 'Targets'    : {'DisplayOrder': 9, 'Heading': 'Target'},
	                # 'Enabled'      : {'DisplayOrder': 10, 'Heading': 'Enabled'}
	                }

	# Get credentials to the necessary accounts
	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles)
	AccountNum = len(set([acct['AccountId'] for acct in CredentialList]))
	print()
	print(f"Looking through {AccountNum} account{'' if AccountNum == 1 else 's'}")
	print()
	# Find all Load Balancers
	All_Global_Accelerators = find_all_global_accelerators(CredentialList)
	# Display what we've found
	display_results(All_Global_Accelerators, display_dict, None, pFilename)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print(ERASE_LINE)
	print(f"{Fore.RED}Found {len(All_Global_Accelerators)} Load Balancer{'' if len(All_Global_Accelerators) == 1 else 's'} across {AccountNum} account{'' if AccountNum == 1 else 's'}{Fore.RESET}")
	print()
	print("Thank you for using this script")
	print()
