#!/usr/bin/env python3


from Inventory_Modules import display_results, get_all_credentials, find_load_balancers2
from time import time
from os.path import split
import sys
from colorama import init, Fore
from botocore.exceptions import ClientError
from ArgumentsClass import CommonArguments
from threading import Thread
from queue import Queue
from tqdm.auto import tqdm

import logging

init()
__version__ = "2024.05.06"
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
	parser.my_parser.description = "We're going to find all elastic load balancers within any of the accounts we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.rolestouse()
	parser.fragment()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-s", "--status",
		dest="pstatus",
		metavar="CloudFormation status",
		default="active",
		help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too")
	return parser.my_parser.parse_args(arguments)


def find_all_elbs(fAllCredentials: list, ffragment: list, fstatus: str):
	"""
	Description: Finds all the load balancers in the Profile(s)
	@param fAllCredentials: List of credentials to some number of accounts
	@param ffragment: Fragment of the load balancer to look for
	@param fstatus: Looking for a specific status
	@return:
	"""
	class FindLoadBalancers(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_fragment, c_status = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					LoadBalancers = find_load_balancers2(c_account_credentials, c_fragment, c_status)
					logging.info(f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(LoadBalancers)} load balancers")
					for lb in LoadBalancers:
						All_Load_Balancers.append({
							# 'ParentProfile': aws_acct.Profile,
							'MgmtAccount': c_account_credentials['MgmtAccount'],
							'AccountId'  : c_account_credentials['AccountId'],
							'Region'     : c_account_credentials['Region'],
							'Name'       : lb['LoadBalancerName'],
							'Status'     : lb['State']['Code'],
							'DNSName'    : lb['DNSName']})
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong")
					logging.warning(my_Error)
					continue
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into")
						continue
					else:
						logging.error(f"Error: Likely throttling errors from too much activity")
						logging.warning(my_Error)
						continue
				finally:
					self.queue.task_done()

	###########

	checkqueue = Queue()
	All_Load_Balancers = []
	WorkerThreads = min(len(fAllCredentials), 10)

	for x in range(WorkerThreads):
		worker = FindLoadBalancers(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in tqdm(fAllCredentials):
		logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			checkqueue.put((credential, ffragment, fstatus))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return All_Load_Balancers


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
	pFragment = args.Fragments
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

	display_dict = {
		# 'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'},
	                'MgmtAccount'  : {'DisplayOrder': 2, 'Heading': 'Mgmt Acct'},
	                'AccountId'    : {'DisplayOrder': 3, 'Heading': 'Acct Number'},
	                'Region'       : {'DisplayOrder': 4, 'Heading': 'Region'},
	                'Name'         : {'DisplayOrder': 5, 'Heading': 'Name'},
	                'Status'       : {'DisplayOrder': 6, 'Heading': 'Status'},
	                'DNSName'      : {'DisplayOrder': 7, 'Heading': 'Public Name'},
	                # 'State'        : {'DisplayOrder': 9, 'Heading': 'State', 'Condition': ['running']}
	                }

	# Get credentials to the necessary accounts
	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles)
	AccountNum = len(set([acct['AccountId'] for acct in CredentialList]))
	RegionNum = len(set([acct['Region'] for acct in CredentialList]))
	WorkerThreads = min(AccountNum, 10)
	print()
	print(f"Looking through {RegionNum} regions and {AccountNum} accounts")
	print()
	# Find all Load Balancers
	All_Load_Balancers = find_all_elbs(CredentialList, pFragment, pStatus)
	# Display what we've found
	display_results(All_Load_Balancers, display_dict)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print(ERASE_LINE)
	print(f"{Fore.RED}Found {len(All_Load_Balancers)} Load Balancers across {AccountNum} profiles across {RegionNum} regions{Fore.RESET}")
	print()
	print("Thank you for using this script")
	print()
