#!/usr/bin/env python3


import Inventory_Modules
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
from colorama import init, Fore
from botocore.exceptions import ClientError

import logging

init()
__version__ = "2023.05.04"

parser = CommonArguments()
parser.singleprofile()
parser.multiregion()
parser.verbosity()
parser.version(__version__)

# UsageMsg="You can provide a level to determine whether this script considers only the 'credentials' file, the 'config' file, or both."
parser.my_parser.add_argument(
		"-f", "--fragment",
		dest="pstackfrag",
		metavar="CloudFormation stack fragment",
		default="all",
		help="String fragment of the cloudformation stack or stackset(s) you want to check for.")
parser.my_parser.add_argument(
		"-s", "--status",
		dest="pstatus",
		metavar="CloudFormation status",
		default="active",
		help="String that determines whether we only see 'CREATE_COMPLETE' or 'DELETE_COMPLETE' too")
parser.my_parser.add_argument(
		"-k", "--skip",
		dest="pSkipAccounts",
		nargs="*",
		metavar="Accounts to leave alone",
		default=[],
		help="These are the account numbers you don't want to screw with. Likely the core accounts.")
args = parser.my_parser.parse_args()

pProfile = args.Profile
pRegionList = args.Regions
pstackfrag = args.pFragments
pstatus = args.pstatus
AccountsToSkip = args.pSkipAccounts
verbose = args.loglevel
# Setup logging levels
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

"""
We should eventually create an argument here that would check on the status of the drift-detection using
"describe_stack_drift_detection_status", but we haven't created that function yet...  
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_drift_detection_status
"""

##########################
ERASE_LINE = '\x1b[2K'

aws_acct = aws_acct_access(pProfile)
sts_client = aws_acct.session.client('sts')

if aws_acct.AccountType == 'Root':
	print()
	answer = input(f"You've specified a root account to check. \n"
	               f"Do you want to check the entire Org or only the root account? (Enter 'root' for whole Org):")
	if answer == 'root':
		ChildAccounts = aws_acct.ChildAccounts
	else:
		ChildAccounts = {'MgmtAccount' : aws_acct.acct_number,
		                 'AccountId'    : aws_acct.acct_number,
		                 'AccountEmail' : aws_acct.MgmtEmail,
		                 'AccountStatus': aws_acct.AccountStatus}

NumStacksFound = 0
print()
RegionList = Inventory_Modules.get_service_regions('cloudformation', pRegionList)
# ChildAccounts = Inventory_Modules.find_child_accounts2(pProfile)
# ChildAccounts = Inventory_Modules.RemoveCoreAccounts(ChildAccounts, AccountsToSkip)

fmt = '%-20s %-15s %-15s %-50s'
print(fmt % ("Account", "Region", "Stack Status", "Stack Name"))
print(fmt % ("-------", "------", "------------", "----------"))

StacksFound = []
for account in ChildAccounts:
	# role_arn = f"arn:aws:iam::{account['AccountId']}:role/AWSCloudFormationStackSetExecutionRole"
	# logging.info(f"Role ARN: {role_arn}")
	try:
		account_credentials = Inventory_Modules.get_child_access3(aws_acct, account['AccountId'], )
		if account_credentials['AccessError']:
			logging.error(f"Accessing account {account['AccountId']} didn't work, so we're skipping it")
			continue
	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			print(f"{pProfile}: Authorization Failure for account {account['AccountId']}")
		elif str(my_Error).find("AccessDenied") > 0:
			print(f"{pProfile}: Access Denied Failure for account {account['AccountId']}")
		else:
			print(f"{pProfile}: Other kind of failure for account {account['AccountId']}")
			print(my_Error)
		break
	for region in RegionList:
		Stacks = []
		try:
			StackNum = 0
			Stacks = Inventory_Modules.find_stacks2(account_credentials, region, pstackfrag, pstatus)
			logging.warning(f"Account: {account['AccountId']} | Region: {region} | Found {StackNum} Stacks")
			logging.info(
				f"{ERASE_LINE}{Fore.RED}Account: {account['AccountId']} Region: {region} Found {StackNum} Stacks{Fore.RESET}")
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				print(f"{account['AccountId']}: Authorization Failure")
		# if len(Stacks) > 0:
		for Stack in Stacks:
			StackName = Stack['StackName']
			StackStatus = Stack['StackStatus']
			StackID = Stack['StackId']
			DriftStatus = Inventory_Modules.enable_drift_on_stacks2(account_credentials, region, StackName)
			logging.error(
				f"Enabled drift detection on {StackName} in account {account_credentials['AccountNumber']} in region {region}")
			NumStacksFound += 1

print(ERASE_LINE)
print(f"{Fore.RED}Looked through {NumStacksFound} Stacks across {len(ChildAccounts)} accounts across "
      f"{len(RegionList)} regions{Fore.RESET}")
print()

print("Thanks for using this script...")
print()
