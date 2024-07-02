#!/usr/bin/env python3
import logging
import os
import sys
from queue import Queue
from threading import Thread
from time import time

from botocore.exceptions import ClientError
from colorama import Fore, init

import Inventory_Modules
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, get_all_credentials

init()
__version__ = "2024.05.31"


##################
def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = os.path.split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.rolestouse()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--ipaddress", "--ip",
		dest="pipaddresses",
		nargs="*",
		metavar="IP address",
		default=None,
		help="IP address(es) you're looking for within your VPCs")
	return parser.my_parser.parse_args(args)


def check_accounts_for_subnets(CredentialList, fip=None):
	"""
	Note that this function takes a list of Credentials and checks for subnets in every account it has creds for
	"""

	class FindSubnets(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_fip, c_PlacesToLook, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					account_subnets = Inventory_Modules.find_account_subnets2(c_account_credentials, c_fip)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for y in range(len(account_subnets['Subnets'])):
						account_subnets['Subnets'][y]['MgmtAccount'] = c_account_credentials['MgmtAccount']
						account_subnets['Subnets'][y]['AccountId'] = c_account_credentials['AccountId']
						account_subnets['Subnets'][y]['Region'] = c_account_credentials['Region']
						account_subnets['Subnets'][y]['SubnetName'] = "None"
						if 'Tags' in account_subnets['Subnets'][y].keys():
							for tag in account_subnets['Subnets'][y]['Tags']:
								if tag['Key'] == 'Name':
									account_subnets['Subnets'][y]['SubnetName'] = tag['Value']
						account_subnets['Subnets'][y]['VPCId'] = account_subnets['Subnets'][y]['VpcId'] if 'VpcId' in account_subnets['Subnets'][y].keys() else None
					if len(account_subnets['Subnets']) > 0:
						AllSubnets.extend(account_subnets['Subnets'])
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					print(f"{ERASE_LINE}Finished finding subnets in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']} - {c_PlaceCount} / {c_PlacesToLook}", end='\r')
					self.queue.task_done()

	checkqueue = Queue()

	AllSubnets = []
	PlaceCount = 0
	PlacesToLook = len(CredentialList)
	WorkerThreads = min(len(CredentialList), 50)

	for x in range(WorkerThreads):
		worker = FindSubnets(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		# for region in fRegionList:
		try:
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			checkqueue.put((credential, fip, PlacesToLook, PlaceCount))
			PlaceCount += 1
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return AllSubnets


def present_results(fSubnetsFound: list):
	"""
	Description: Shows off results at the end
	@param fSubnetsFound: List of subnets found and their attributes.
	"""
	display_dict = {'MgmtAccount'            : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'              : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'                 : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'VpcId'                  : {'DisplayOrder': 4, 'Heading': 'VPC ID'},
	                'SubnetName'             : {'DisplayOrder': 5, 'Heading': 'Subnet Name'},
	                'CidrBlock'              : {'DisplayOrder': 6, 'Heading': 'CIDR Block'},
	                'AvailableIpAddressCount': {'DisplayOrder': 7, 'Heading': 'Available IPs'},
	                # 'IPUtilization'          : {'DisplayOrder': 8, 'Heading': 'IP Utilization'},
	                # 'NearExhaustion'          : {'DisplayOrder': 8, 'Heading': 'Near Exhaustion', 'Condition': [True]},
	                }
	AccountNum = len(set([acct['AccountId'] for acct in AllCredentials]))
	RegionNum = len(set([acct['Region'] for acct in AllCredentials]))
	sorted_Subnets_Found = sorted(fSubnetsFound, key=lambda x: (x['MgmtAccount'], x['AccountId'], x['Region'], x['SubnetName']))
	display_results(sorted_Subnets_Found, display_dict, 'None', pFilename)
	print()
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
	print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
	print(f"The output has also been written to a file beginning with '{pFilename}' + the date and time") if pFilename is not None else ""
	print()
	print(f"Found {len(SubnetsFound)} subnets across {AccountNum} accounts across {RegionNum} regions")


def analyze_results(fSubnetsFound: list):
	# :fSubnetsFound: a list of the subnets found and their attributes
	account_summary = []
	VPC_summary = []
	subnets_near_exhaustion = []
	for record in fSubnetsFound:
		AvailableIps = record['AvailableIpAddressCount']
		account_number = record['AccountId']
		vpc_id = record['VpcId']
		mask = int(str(record['CidrBlock']).split("/")[1])
		TotalIPs = 2 ** (32 - mask) - 5
		IPUtilization = 100 - (round(AvailableIps / TotalIPs, 2) * 100)
		subnets_near_exhaustion.append(record['SubnetId']) if IPUtilization > 74 else ''
		if account_number not in account_summary:
			account_summary.append(account_number)
		if vpc_id not in VPC_summary:
			VPC_summary.append(vpc_id)
	print()
	print(f"Number of accounts found with subnets: {len(account_summary)}")
	print(f"Number of unique VPCs found: {len(VPC_summary)}")
	print(f"Number of subnets in danger of IP Exhaustion (80%+ IPs utilized): {len(subnets_near_exhaustion)}")
	# print(f"Number of subnets using unroutable space (100.64.*.*): ")
	print()


##################

ERASE_LINE = '\x1b[2K'
begin_time = time()

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pAccounts = args.Accounts
	pRoleList = args.AccessRoles
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
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

	logging.info(f"Profiles: {pProfiles}")

	print()
	print(f"Checking accounts for Subnets... ")
	print()

	# Get credentials from all relevant Children accounts
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoleList)
	# Get relevant subnets
	SubnetsFound = check_accounts_for_subnets(AllCredentials, fip=pIPaddressList)
	# display_results(SubnetsFound, display_dict)
	present_results(SubnetsFound)
	# Print out an analysis of what was found at the end
	if verbose < 50:
		analyze_results(SubnetsFound)
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thank you for using this script")
print()
