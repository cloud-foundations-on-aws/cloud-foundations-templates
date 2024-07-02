#!/usr/bin/env python3

import logging
from time import time
import sys
from os.path import split

from colorama import Fore, init

from Inventory_Modules import display_results, get_regions3, RemoveCoreAccounts, find_stacksets2, find_stack_instances2, get_credentials_for_accounts_in_org
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access

init()

__version__ = '2024.06.20'
begin_time = time()
ERASE_LINE = '\x1b[2K'

#####################
# Functions
#####################


def parse_args(args):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()  # Allows for a single profile to be specified
	parser.multiregion()  # Allows for multiple regions to be specified at the command line
	parser.fragment()
	parser.extendedargs()
	parser.rolestouse()
	parser.rootOnly()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()  # Allows for the verbosity to be handled.
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-i", "--instances",
		dest="pinstancecount",
		action="store_true",
		default=False,
		help="Flag to determine whether you want to see the instance totals for each stackset")
	local.add_argument(
		"-s", "--status",
		dest="pstatus",
		metavar="CloudFormation status",
		default="Active",
		choices=['active', 'ACTIVE', 'Active', 'deleted', 'DELETED', 'Deleted'],
		help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too. Valid values are 'ACTIVE' or 'DELETED'")
	return parser.my_parser.parse_args(args)


def setup_auth_accounts_and_regions(fProfile: str) -> (aws_acct_access, list, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@return:
		- an object of the type "aws_acct_access"
		- a list of accounts  the user has access to, based on the provided profile
		- a list of regions valid for this particular profile/ account.
	"""
	try:
		aws_acct = aws_acct_access(fProfile)
	except ConnectionError as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	ChildAccounts = aws_acct.ChildAccounts
	RegionList = get_regions3(aws_acct, pRegionList)

	ChildAccounts = RemoveCoreAccounts(ChildAccounts, pSkipAccounts)
	if pAccountList is None:
		AccountList = [account['AccountId'] for account in ChildAccounts]
	elif pAccessRoles is not None:
		AccountList = pAccountList
	else:
		AccountList = [account['AccountId'] for account in ChildAccounts if account['AccountId'] in pAccountList]

	print(f"You asked to find CloudFormation stacksets")
	if pRootOnly:
		print(f"\tIn only the root account: {aws_acct.acct_number}")
	else:
		print(f"\tin these accounts: {Fore.RED}{AccountList}{Fore.RESET}")
	print(f"\tin these regions: {Fore.RED}{RegionList}{Fore.RESET}")
	print(f"\tContaining {'this '+ Fore.RED +'exact fragment'+Fore.RESET if pExact else 'one of these fragments'}: {pFragments}")
	if pSkipAccounts is not None:
		print(f"\tWhile skipping these accounts: {Fore.RED}{pSkipAccounts}{Fore.RESET}")

	return aws_acct, AccountList, RegionList


def find_all_cfnstacksets(f_All_Credentials:list, f_Fragments:list, f_Status)->list:
	"""
	Description: This function will find all the stacksets in the specific account.
	@param f_All_Credentials: a list of all the credentials for accounts we're going to look into
	@return:
	"""
	All_Results = []
	for credential in f_All_Credentials:
		if not credential['Success']:
			logging.error(f"Failure for account {credential['AccountId']} in region {credential['Region']}\n"
			              f"With message: {credential['AccessError']}")
			continue
		# logging.info(f"Account Creds: {account_credentials}")
		print(f"{ERASE_LINE}{Fore.RED}Checking Account: {credential['AccountId']} Region: {credential['Region']} for stacksets matching {f_Fragments} with status: {f_Status}{Fore.RESET}", end="\r")
		StackSets = find_stacksets2(credential, pFragments, pstatus)
		logging.warning(f"Account: {credential['AccountId']} | Region: {credential['Region']} | Found {len(StackSets)} Stacksets")
		if not StackSets:
			print(f"{ERASE_LINE}We connected to account {credential['AccountId']} in region {credential['Region']}, but found no stacksets", end='\r') if verbose < 50 else ''
		else:
			print(f"{ERASE_LINE}{Fore.RED}Account: {credential['AccountId']} Region: {credential['Region']} Found {len(StackSets)} Stacksets{Fore.RESET}", end="\r")  if verbose < 50 else ''
		for stack in StackSets:
			ListOfStackInstances = []  # Resets the list every time
			if pInstanceCount:
				milestone = time()
				ListOfStackInstances = find_stack_instances2(credential, credential['Region'], stack['StackSetName'])
				if pTiming:
					print(f"{ERASE_LINE}Found {len(ListOfStackInstances)} instances for {stack['StackSetName']} in {credential['Region']}, which took {time() - milestone:.2f} seconds", end='\r')
			All_Results.append({'AccountId':credential['AccountId'],
			                    'StackName':stack['StackSetName'],
			                    'Status':stack['Status'],
			                    'Region':credential['Region'],
			                    'InstanceNum':len(ListOfStackInstances) if pInstanceCount else 'N/A'})
	return All_Results


#####################
# Main
#####################

if __name__ == "__main__":
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegionList = args.Regions
	pInstanceCount = args.pinstancecount
	pRootOnly = args.RootOnly
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccountList = args.Accounts
	pAccessRoles = args.AccessRoles
	verbose = args.loglevel
	pTiming = args.Time
	pFragments = args.Fragments
	pExact = args.Exact
	pstatus = args.pstatus
	pFilename = args.Filename
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	# Setup auth object, get account list and region list setup
	aws_acct, AccountList, RegionList = setup_auth_accounts_and_regions(pProfile)
	# Get all credentials needed
	CredentialList = get_credentials_for_accounts_in_org(aws_acct, pSkipAccounts, pRootOnly, AccountList, pProfile, RegionList, pAccessRoles, pTiming)
	# Find all the stacksets
	All_Results = find_all_cfnstacksets(CredentialList, AccountList, RegionList)
	print()
	display_dict = {'AccountId': {'DisplayOrder': 1, 'Heading': 'Acct Number'},
	                'Region'   : {'DisplayOrder': 2, 'Heading': 'Region'},
	                'Status'   : {'DisplayOrder': 3, 'Heading': 'Status'},
	                'StackName': {'DisplayOrder': 4, 'Heading': 'Stackset Name'}}
	if pInstanceCount:
		display_dict.update({'Instances'  : {'DisplayOrder': 5, 'Heading': '# of Instances'}})

	# Display results
	display_results(All_Results, display_dict, None, pFilename)

	print(ERASE_LINE)
	print(f"{Fore.RED}Found {len(All_Results)} Stacksets across {len(AccountList)} accounts across {len(RegionList)} regions{Fore.RESET}")
	print()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print("Thanks for using this script...")
	print()
