#!/usr/bin/env python3


import logging
import sys
from queue import Queue
# from tqdm.auto import tqdm
from threading import Thread
from time import time

from botocore.exceptions import ClientError
from colorama import Fore, init

import Inventory_Modules
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, get_all_credentials

init()
__version__ = "2024.01.26"


##########################
def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all vpcs within any of the accounts and regions we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rolestouse()
	parser.rootOnly()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	parser.my_parser.add_argument(
		"--default",
		dest="pDefault",
		metavar="Looking for default VPCs only",
		action="store_const",
		default=False,
		const=True,
		help="Flag to determine whether we're looking for default VPCs only.")
	return parser.my_parser.parse_args(args)


def find_all_vpcs(fAllCredentials, fDefaultOnly=False):
	"""
	Note that this function takes a list of stack set names and finds the stack instances within them
	"""

	# This function is called
	class FindVPCs(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_default, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					# Now go through those stacksets and determine the instances, made up of accounts and regions
					Vpcs = Inventory_Modules.find_account_vpcs2(c_account_credentials, c_default)
					logging.info(f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(Vpcs['Vpcs'])} VPCs")
					if 'Vpcs' in Vpcs.keys() and len(Vpcs['Vpcs']) > 0:
						for y in range(len(Vpcs['Vpcs'])):
							VpcName = "No name defined"
							VpcId = Vpcs['Vpcs'][y]['VpcId']
							IsDefault = Vpcs['Vpcs'][y]['IsDefault']
							CIDRBlockAssociationSet = Vpcs['Vpcs'][y]['CidrBlockAssociationSet']
							if 'Tags' in Vpcs['Vpcs'][y]:
								for z in range(len(Vpcs['Vpcs'][y]['Tags'])):
									if Vpcs['Vpcs'][y]['Tags'][z]['Key'] == "Name":
										VpcName = Vpcs['Vpcs'][y]['Tags'][z]['Value']
							# This is needed to accommodate the possibility that there are multiple CIDRs associated with a given VPC.
							for _ in range(len(CIDRBlockAssociationSet)):
								AllVPCs.append({'MgmtAccount': c_account_credentials['MgmtAccount'],
								                'AccountId'  : c_account_credentials['AccountId'],
								                'Region'     : c_account_credentials['Region'],
								                'CIDR'       : CIDRBlockAssociationSet[_]['CidrBlock'],
								                'VpcId'      : VpcId,
								                'IsDefault'  : IsDefault,
								                'VpcName'    : VpcName})
					else:
						continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
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
					print(".", end='')
					self.queue.task_done()

	###########

	checkqueue = Queue()

	AllVPCs = []
	PlaceCount = 0
	WorkerThreads = min(len(fAllCredentials), 25)

	for x in range(WorkerThreads):
		worker = FindVPCs(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in fAllCredentials:
		logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
		print(f"{ERASE_LINE}Checking {credential['AccountId']} in region {credential['Region']} - {PlaceCount + 1} / {len(fAllCredentials)}", end='\r')
		# for region in fRegionList:
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			checkqueue.put((credential, fDefaultOnly, PlaceCount))
			logging.info(f"Put credential: {credential}, Default: {fDefaultOnly}")
			PlaceCount += 1
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return AllVPCs


##########################
if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pAccounts = args.Accounts
	pRoles = args.AccessRoles
	pSkipProfiles = args.SkipProfiles
	pSkipAccounts = args.SkipAccounts
	pRootOnly = args.RootOnly
	pTiming = args.Time
	pFilename = args.Filename
	pDefault = args.pDefault
	verbose = args.loglevel
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")

	ERASE_LINE = '\x1b[2K'

	begin_time = time()

	NumVpcsFound = 0
	NumRegions = 0
	if pProfiles is not None:
		print(f"Checking for VPCs in profile{'s' if len(pProfiles) > 1 else ''} {pProfiles}")
	else:
		print(f"Checking for VPCs in default profile")

	# NumOfRootProfiles = 0
	# Get credentials
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoles)
	AllRegionsList = list(set([x['Region'] for x in AllCredentials]))
	AllAccountList = list(set([x['AccountId'] for x in AllCredentials]))
	# Find the VPCs
	All_VPCs_Found = find_all_vpcs(AllCredentials, pDefault)
	# Display results
	display_dict = {'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'VpcName'    : {'DisplayOrder': 4, 'Heading': 'VPC Name'},
	                'CIDR'       : {'DisplayOrder': 5, 'Heading': 'CIDR Block'},
	                'IsDefault'  : {'DisplayOrder': 6, 'Heading': 'Default VPC', 'Condition': [True, 1, '1']},
	                'VpcId'      : {'DisplayOrder': 7, 'Heading': 'VPC Id'}}

	logging.info(f"# of Regions: {len(AllRegionsList)}")
	# logging.info(f"# of Management Accounts: {NumOfRootProfiles}")
	logging.info(f"# of Child Accounts: {len(AllAccountList)}")

	sorted_AllVPCs = sorted(All_VPCs_Found, key=lambda d: (d['MgmtAccount'], d['AccountId'], d['Region'], d['VpcName'], d['CIDR']))
	print()
	display_results(sorted_AllVPCs, display_dict, None, pFilename)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print(ERASE_LINE)
	# Had to do this, because some of the VPCs that show up in the "sorted_AllVPCs" list are actually the same VPC, with a different CIDR range.
	Num_of_unique_VPCs = len(set([x['VpcId'] for x in sorted_AllVPCs]))
	print(f"Found {Num_of_unique_VPCs}{' default' if pDefault else ''} Vpcs across {len(AllAccountList)} accounts across {len(AllRegionsList)} regions")
	print()
	print("Thank you for using this script.")
	print()
