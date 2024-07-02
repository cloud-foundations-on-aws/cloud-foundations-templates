#!/usr/bin/env python3

import sys
import boto3
import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
import simplejson as json

import logging
__version__ = "2023.05.04"

parser = CommonArguments()
parser.singleprofile()
parser.singleregion()
parser.verbosity()
parser.version(__version__)
parser.my_parser.add_argument(
		"-R", "--access_rolename",
		dest="pAccessRole",
		default='AWSCloudFormationStackSetExecutionRole',
		metavar="role to use for access to child accounts",
		help="This parameter specifies the role that will allow this script to have access to the children accounts.")
parser.my_parser.add_argument(
		"-t", "--target_rolename",
		dest="pTargetRole",
		default='AWSCloudFormationStackSetExecutionRole',
		metavar="role to change",
		help="This parameter specifies the role to have its Trust Policy changed.")
parser.my_parser.add_argument(
		"+f", "--fix", "+fix",
		dest="pFix",
		action="store_const",
		const=True,
		default=False,
		help="This parameter determines whether to make any changes in child accounts.")
parser.my_parser.add_argument(
		"+l", "--lock", "+lock",
		dest="pLock",
		action="store_const",
		const=True,
		default=False,
		help="This parameter determines whether to lock the Trust Policy.")
parser.my_parser.add_argument(
		"-s", "--safety",
		dest="pSafety",
		action="store_const",
		const=False,
		default=True,
		help="Adding this parameter will 'remove the safety' - by not including the principle running this script, which might mean you get locked out of making further changes.")
args = parser.my_parser.parse_args()

pProfile = args.Profile
pTargetRole = args.pTargetRole
pAccessRole = args.pAccessRole
pLock = args.pLock
pSafety = args.pSafety
pFix = args.pFix
verbose = args.loglevel
logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

aws_acct = aws_acct_access(pProfile)

if not aws_acct.AccountType.lower() == 'root':
	print()
	print(f"The profile {pProfile} does not represent an Org")
	print("This script only works with org accounts.")
	print()
	sys.exit(1)
##########################
ERASE_LINE = '\x1b[2K'
##########################

print(f"We're using the {pAccessRole} role to gain access to the child accounts")
print(f"We're targeting the {pTargetRole} role to change its Trust Policy")

'''
1. Collect SSM parameters with the ARNs that should be in the permission
2. Create the TrustPolicy in JSON
3. Get a listing of all accounts that need to be updated
4. Connect to each account, and update the existing trust policy with the new policy
'''
# 1. Collect parameters with the ARNs that should be in the permission
# lock_down_arns_list=[]
allowed_arns = []
ssm_client = aws_acct.session.client('ssm')
param_list = ssm_client.describe_parameters(
	ParameterFilters=[{'Key': 'Name', 'Option': 'Contains', 'Values': ['lock_down_role_arns_list']}])['Parameters']
if len(param_list) == 0:
	print("You need to set the region (-r|--region) to the default region where the SSM parameters are stored.")
	print("Otherwise, with no *allowed* arns, we would lock everything out from this role.")
	print("Exiting...")
	sys.exit(2)
for i in param_list:
	response = param = ssm_client.get_parameter(Name=i['Name'])
	logging.info(f"Adding {response['Parameter']['Value']} to the list for i: {i['Name']}")
	allowed_arns.append(response['Parameter']['Value'])

# 1.5 Find who is running the script and add their credential as a safety
Creds = Inventory_Modules.find_calling_identity(pProfile)
if pSafety:
	allowed_arns.append(Creds['Arn'])
# 2. Create the Trust Policy in JSON

if pLock:
	if pSafety and pFix:
		logging.error("Locking down the Trust Policy to *only* the Lambda functions.")
	elif pFix:
		logging.error(f"Locking down the Trust Policy to the Lambda functions and {Creds['Arn']}.")
	else:
		logging.critical(
			"While you asked us to lock things down, You didn't use the '+f' parameter, so we're not changing a thing.")
	Trust_Policy = {
		"Version"  : "2012-10-17",
		"Statement": [
			{
				"Sid"      : "LambdaAccess",
				"Effect"   : "Allow",
				"Principal": {
					"AWS": allowed_arns
					},
				"Action"   : "sts:AssumeRole"
				}
			]}
else:
	Trust_Policy = {
		"Version"  : "2012-10-17",
		"Statement": [
			{
				"Sid"      : "LambdaAccess",
				"Effect"   : "Allow",
				"Principal": {
					"AWS": allowed_arns
					},
				"Action"   : "sts:AssumeRole"
				},
			{
				"Sid"      : "DevAccess",
				"Effect"   : "Allow",
				"Principal": {
					"AWS": [f"arn:aws:iam::{aws_acct.MgmtAccount}:root"]
					},
				"Action"   : "sts:AssumeRole"
				}
			]}
Trust_Policy_json = json.dumps(Trust_Policy)
# 3. Get a listing of all accounts that need to be updated and then ...


# 4. Connect to each account, and detach the existing policy, and apply the new policy
sts_client = aws_acct.session.client('sts')
TrustPoliciesChanged = 0
ErroredAccounts = []
for acct in aws_acct.ChildAccounts:
	ConnectionSuccess = False
	try:
		role_arn = f"arn:aws:iam::{acct['AccountId']}:role/{pAccessRole}"
		account_credentials = sts_client.assume_role(
				RoleArn=role_arn,
				RoleSessionName="RegistrationScript")['Credentials']
		account_credentials['Account'] = acct['AccountId']
		logging.warning(f"Accessed Account {acct['AccountId']} using rolename {pAccessRole}")
		ConnectionSuccess = True
	except ClientError as my_Error:
		logging.error(
			f"Account {acct['AccountId']}, role {pTargetRole} was unavailable to change, so we couldn't access the role's Trust Policy")
		logging.warning(my_Error)
		ErroredAccounts.append(acct['AccountId'])
		pass
	if ConnectionSuccess:
		try:
			# detach policy from the role and attach the new policy
			iam_session = boto3.Session(
					aws_access_key_id=account_credentials['AccessKeyId'],
					aws_secret_access_key=account_credentials['SecretAccessKey'],
					aws_session_token=account_credentials['SessionToken']
					)
			iam_client = iam_session.client('iam')
			trustpolicyexisting = iam_client.get_role(RoleName=pTargetRole)
			logging.info("Found Trust Policy %s in account %s for role %s" % (
				json.dumps(trustpolicyexisting['Role']['AssumeRolePolicyDocument']),
				acct['AccountId'],
				pTargetRole))
			if pFix:
				trustpolicyupdate = iam_client.update_assume_role_policy(RoleName=pTargetRole,
				                                                         PolicyDocument=Trust_Policy_json)
				TrustPoliciesChanged += 1
				logging.error(f"Updated Trust Policy in Account {acct['AccountId']} for role {pTargetRole}")
				trustpolicyexisting = iam_client.get_role(RoleName=pTargetRole)
				logging.info("Updated Trust Policy %s in account %s for role %s" % (
					json.dumps(trustpolicyexisting['Role']['AssumeRolePolicyDocument']),
					acct['AccountId'],
					pTargetRole))
			else:
				logging.error(f"Account {acct['AccountId']} - no changes made")
		except ClientError as my_Error:
			logging.warning(my_Error)
			pass

print(ERASE_LINE)
print(f"We found {len(aws_acct.ChildAccounts)} accounts under your organization")
if pLock and pFix:
	print(f"We locked {TrustPoliciesChanged} Trust Policies")
elif not pLock and pFix:
	print(f"We unlocked {TrustPoliciesChanged} Trust Policies")
else:
	print(f"We didn't change {TrustPoliciesChanged} Trust Policies")
if len(ErroredAccounts) > 0:
	print(f"We weren't able to access {len(ErroredAccounts)} accounts.")
if verbose < 50:
	print("Here are the accounts that were not updated")
	for i in ErroredAccounts:
		print(i)
print()
print("Thanks for using the tool.")
print()
