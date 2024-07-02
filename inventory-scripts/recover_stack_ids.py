#!/usr/bin/env python3

import logging
import sys
from pprint import pprint
from time import time
from os.path import split

import simplejson as json
from colorama import Fore, init

import Inventory_Modules
from Inventory_Modules import get_credentials_for_accounts_in_org
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access

"""
This script was created to help solve a testing problem for the "move_stack_instances.py" script.e
Originally, that script didn't have built-in recovery, so we needed this script to "recover" those stack-instance ids that might have been lost during the move_stack_instances.py run. However, that script now has built-in recovery, so this script isn't really needed. However, it can still be used to find any stack-instances that have been orphaned from their original stack-set, if that happens. 
"""

init()
__version__ = "2024.05.18"


#########################
# Functions
#########################

def parse_args(args):
	"""
	Description: Parse the arguments sent to the script
	@param args: namespace of the arguments passed in at the command line
	@return: namespace with all parameters parsed out
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()  # Allows for a single profile to be specified
	parser.singleregion()  # Allows for a single region to be specified at the command line
	parser.extendedargs()  # Allows for extended arguments like which accounts to skip, and whether Force is enabled.
	parser.fragment()
	parser.timing()
	parser.rolestouse()
	parser.verbosity()  # Allows for the verbosity to be handled.
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	# local.add_argument(
	# 	"-s", "--status",
	# 	dest="status",
	# 	metavar="CloudFormation status",
	# 	default="active",
	# 	help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too")
	local.add_argument(
		"-R", "--SearchRegions",
		dest="pRegionList",
		metavar="Region name",
		help="Regions where StackSets are applied")
	local.add_argument(
		"--new",
		dest="newStackSetName",
		metavar="New Stackset name",
		help="The NEW Stack Set name")
	local.add_argument(
		"--old",
		dest="oldStackSetName",
		metavar="Old Stackset name",
		help="The OLD Stack Set name")
	return parser.my_parser.parse_args(args)


def setup_auth_and_regions(fProfile: str = None) -> (object, list, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials.
	@return: (aws_acct_access, list)
	"""
	aws_acct = aws_acct_access(fProfile)
	ChildAccounts = aws_acct.ChildAccounts
	RegionList = Inventory_Modules.get_regions3(aws_acct, pRegionList)
	ChildAccounts = Inventory_Modules.RemoveCoreAccounts(ChildAccounts, pAccountsToSkip)
	AccountList = [account['AccountId'] for account in ChildAccounts]

	print(f"You asked to find stacks with this fragment list: {Fore.RED}{pFragments}{Fore.RESET}")
	print(f"\t\tin these accounts: {Fore.RED}{AccountList}{Fore.RESET}")
	print(f"\t\tin these regions: {Fore.RED}{RegionList}{Fore.RESET}")
	return aws_acct, AccountList, RegionList


#########################
# Main
#########################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegion = args.Region
	pRegionList = args.pSearchRegionList
	pAccountsToSkip = args.SkipAccounts
	pAccounts = args.Accounts
	pOldStackSetName = args.oldStackSetName
	pNewStackSetName = args.newStackSetName
	pTiming = args.Time
	pFragments = args.Fragments
	# pstatus = args.status
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	##########################
	ERASE_LINE = '\x1b[2K'
	begin_time = time()

	# Setup credentials and regions (filtered by what they wanted to check)
	aws_acct, AccountList, RegionList = setup_auth_and_regions(pProfile)

	pStackIdFlag = True
	precoveryFlag = True

	print()
	fmt = '%-20s %-15s %-15s %-50s %-50s'
	print(fmt % ("Account", "Region", "Stack Status", "Stack Name", "Stack ID"))
	print(fmt % ("-------", "------", "------------", "----------", "--------"))

	StacksFound = []
	sts_client = aws_acct.session.client('sts')
	item_counter = 0
	AllCredentials = get_credentials_for_accounts_in_org(aws_acct)
	for cred in AllCredentials:
		if not cred['Success']:
			continue
		for region in RegionList:
			item_counter += 1
			Stacks = False
			try:
				Stacks = Inventory_Modules.find_stacks2(cred, region, pFragments)
				logging.warning(f"Account: {cred['AccountId']} | Region: {region} | Found {len(Stacks)} Stacks")
				print(f"{ERASE_LINE}{Fore.RED}Account: {cred['AccountId']} Region: {region} Found {len(Stacks)} Stacks{Fore.RESET} ({item_counter} of {len(AccountList) * len(RegionList)})", end='\r')
			except Exception as my_Error:
				print(f"Error: {my_Error}")
			# TODO: Currently we're using this "Stacks" list as a boolean if it's populated. We should change this.
			if Stacks and len(Stacks) > 0:
				for y in range(len(Stacks)):
					StackName = Stacks[y]['StackName']
					StackStatus = Stacks[y]['StackStatus']
					StackID = Stacks[y]['StackId']
					if pStackIdFlag:
						print(fmt % (cred['AccountId'], region, StackStatus, StackName, StackID))
					else:
						print(fmt % (cred['AccountId'], region, StackStatus, StackName))
					StacksFound.append({
						'Account'    : cred['AccountId'],
						'Region'     : region,
						'StackName'  : StackName,
						'StackStatus': StackStatus,
						'StackArn'   : StackID})
	lAccounts = []
	lRegions = []
	lAccountsAndRegions = []
	for i in range(len(StacksFound)):
		lAccounts.append(StacksFound[i]['Account'])
		lRegions.append(StacksFound[i]['Region'])
		lAccountsAndRegions.append((StacksFound[i]['Account'], StacksFound[i]['Region']))
	print(ERASE_LINE)
	print(f"{Fore.RED}Looked through {len(StacksFound)} Stacks across {len(AccountList)} accounts across {len(RegionList)} regions{Fore.RESET}")
	print()
	if args.loglevel < 21:  # INFO level
		print("The list of accounts and regions:")
		pprint(list(sorted(set(lAccountsAndRegions))))

	if precoveryFlag:
		Stack_Instances = []
		for item in StacksFound:
			Stack_Instances.append({'Account': item['Account'],
			                        'Region' : item['Region'],
			                        'Status' : item['StackStatus'],
			                        'StackId': item['StackArn']})
		stack_ids = {'Stack_instances': Stack_Instances, 'Success': True}
		BigString = {'AccountNumber'    : aws_acct.acct_number,
		             'AccountToMove'    : None,
		             'ManagementAccount': aws_acct.MgmtAccount,
		             'NewStackSetName'  : pNewStackSetName,
		             'OldStackSetName'  : pOldStackSetName,
		             'ProfileUsed'      : pProfile,
		             'Region'           : pRegion,
		             'stack_ids'        : stack_ids}
		file_data = json.dumps(BigString, sort_keys=True, indent=4 * ' ')
		OutputFilename = f"{pOldStackSetName}-{pNewStackSetName}-{aws_acct.acct_number}-{pRegion}"
		with open(OutputFilename, 'w') as out:
			print(file_data, file=out)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

	print()
	print("Thanks for using this script...")
	print()
