#!/usr/bin/env python3


import Inventory_Modules
from Inventory_Modules import get_credentials_for_accounts_in_org
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
from time import time
from colorama import init, Fore
from botocore.exceptions import ClientError

import logging

init()
__version__ = "2023.05.10"

parser = CommonArguments()
parser.multiprofile()
parser.multiregion()
parser.roletouse()
parser.extendedargs()
parser.rootOnly()
parser.timing()
parser.verbosity()
parser.version(__version__)

group = parser.my_parser.add_mutually_exclusive_group(required=True)
group.add_argument(
	"+r", "--RoleToAdd",
	dest="pRoleNameToAdd",
	metavar="role to create",
	default=None,
	help="Rolename to be added to a number of accounts")
group.add_argument(
	"-c", "--rolecheck",
	dest="pRoleNameToCheck",
	metavar="role to check to see if it exists",
	default=None,
	help="Rolename to be checked for existence")
group.add_argument(
	"--RoleToRemove",
	dest="pRoleNameToRemove",
	metavar="role to remove",
	default=None,
	help="Rolename to be removed from a number of accounts")
args = parser.my_parser.parse_args()

pProfiles = args.Profiles
pTiming = args.Time
pSkipAccounts = args.SkipAccounts
pSkipProfiles = args.SkipProfiles
pRootOnly = args.RootOnly
pAccounts = args.Accounts
pRoleToUse = args.AccessRole
pRoleNameToAdd = args.pRoleNameToAdd
pRoleNameToRemove = args.pRoleNameToRemove
pRoleNameToCheck = args.pRoleNameToCheck
verbose = args.loglevel
logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")


##########################


def createrole(ocredentials, frole):
	import simplejson as json
	import boto3
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountId'] holds the account number you're connecting to
	"""
	Trust_Policy = {"Version"  : "2012-10-17",
					"Statement": [
						{
							"Effect"   : "Allow",
							"Principal": {
								"AWS": [
									f"arn:aws:iam::{ocredentials['MgmtAccount']}:root"
								]
							},
							"Action"   : "sts:AssumeRole"
						}
					]
					}

	AdminPolicy = 'arn:aws:iam::aws:policy/AdministratorAccess'

	Trust_Policy_json = json.dumps(Trust_Policy)

	session_iam = boto3.Session(
		aws_access_key_id=ocredentials['AccessKeyId'],
		aws_secret_access_key=ocredentials['SecretAccessKey'],
		aws_session_token=ocredentials['SessionToken'],
		region_name=ocredentials['Region']
	)

	client_iam = session_iam.client('iam')
	try:
		response = client_iam.create_role(RoleName=frole, AssumeRolePolicyDocument=Trust_Policy_json)
		logging.info("Successfully created the blank role %s in account %s", frole, ocredentials['AccountId'])
	except client_iam.exceptions.LimitExceededException as my_Error:
		ErrorMessage = f"Limit Exceeded: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.InvalidInputException as my_Error:
		ErrorMessage = f"Invalid Input: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.EntityAlreadyExistsException as my_Error:
		ErrorMessage = f"Role already exists: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.MalformedPolicyDocumentException as my_Error:
		ErrorMessage = f"Malformed role policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.ConcurrentModificationException as my_Error:
		ErrorMessage = f"Concurrent operations: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.ServiceFailureException as my_Error:
		ErrorMessage = f"Service Failure: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}

	try:
		response1 = client_iam.attach_role_policy(RoleName=frole, PolicyArn=AdminPolicy)
		print(f"{ERASE_LINE}We've successfully added the role{Fore.GREEN} {frole} {Fore.RESET}to account"
			  f"{Fore.GREEN} {ocredentials['AccountId']} {Fore.RESET}with admin rights, "
			  f"trusting the Management Account {Fore.GREEN}{ocredentials['MgmtAccount']}{Fore.RESET} "
			  f"in profile {Fore.GREEN}{ocredentials['ParentProfile']}{Fore.RESET}.")
	except client_iam.exceptions.NoSuchEntityException as my_Error:
		ErrorMessage = f"No such policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.LimitExceededException as my_Error:
		ErrorMessage = f"No such policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.InvalidInputException as my_Error:
		ErrorMessage = f"No such policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.UnmodifiableEntityException as my_Error:
		ErrorMessage = f"No such policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.PolicyNotAttachableException as my_Error:
		ErrorMessage = f"No such policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except client_iam.exceptions.ServiceFailureException as my_Error:
		ErrorMessage = f"No such policy: {my_Error}"
		logging.error(ErrorMessage)
		return_response = {'Success': False, 'ErrorMessage': ErrorMessage}
	except ClientError as my_Error:
		if my_Error.response['Error']['Code'] == 'EntityAlreadyExists':
			print(f"Role {frole} already exists in account {ocredentials['AccountId']}. Skipping.")
		print(my_Error)
		pass


def removerole(ocredentials, frole):
	import boto3
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountId'] holds the account number you're connecting to
	"""
	return_response = {'Success': False, 'ErrorMessage': ''}
	session_iam = boto3.Session(
		aws_access_key_id=ocredentials['AccessKeyId'],
		aws_secret_access_key=ocredentials['SecretAccessKey'],
		aws_session_token=ocredentials['SessionToken']
	)

	client_iam = session_iam.client('iam')
	AdminPolicy = 'arn:aws:iam::aws:policy/AdministratorAccess'

	try:
		# We need to list the policies attached (whether inline or managed)
		# TODO: Both of these calls below should allow for pagination
		attached_managed_policies = client_iam.list_attached_role_policies(RoleName=frole)
		"""
		{
	    'AttachedPolicies': [
	        {
	            'PolicyName': 'string',
	            'PolicyArn': 'string'
	        },
	    ],
	    'IsTruncated': True|False,
	    'Marker': 'string'
		}
		"""

		attached_inline_policies = client_iam.list_role_policies(RoleName=frole)
		"""
		{
	    'PolicyNames': [
	        'string',
	    ],
	    'IsTruncated': True|False,
	    'Marker': 'string'
		}
		"""

		# Then we need to detach/ delete the policy we find
		for managed_policy in attached_managed_policies['AttachedPolicies']:
			try:
				response1 = client_iam.detach_role_policy(
					RoleName=frole,
					PolicyArn=managed_policy['PolicyArn']
				)
				logging.info(f"Successfully removed the managed policy {managed_policy['PolicyName']} from role {frole}")
				return_response['Success'] = True
			except (client_iam.exceptions.NoSuchEntityException,
					client_iam.exceptions.InvalidInputException,
					client_iam.exceptions.ServiceFailureException) as my_Error:
				logging.error(f"Error Message: {my_Error}")
				return_response['ErrorMessage'] = str(my_Error)
				return_response['Success'] = False
			if return_response['Success']:
				continue
			else:
				return return_response

		for inline_policy in attached_inline_policies['PolicyNames']:
			try:
				inline_role_deletion = client_iam.delete_role_policy(
					RoleName=frole,
					PolicyName=inline_policy
				)
				logging.info(f"Successfully removed the inline policy {inline_policy} from role {frole}")
				return_response['Success'] = True
			except (client_iam.exceptions.NoSuchEntityException,
					client_iam.exceptions.LimitExceededException,
					client_iam.exceptions.UnmodifiableEntityException,
					client_iam.exceptions.ServiceFailureException) as my_Error:
				logging.error(f"Error Message: {my_Error}")
				return_response['ErrorMessage'] = str(my_Error)
				return_response['Success'] = False
			if return_response['Success']:
				continue
			else:
				return return_response

		# Only then we can we delete the role
		try:
			response = client_iam.delete_role(RoleName=frole)
			logging.info(f"Successfully removed the role {frole}")
			return_response['Success'] = True
		except (client_iam.exceptions.NoSuchEntityException,
				client_iam.exceptions.DeleteConflictException,
				client_iam.exceptions.LimitExceededException,
				client_iam.exceptions.UnmodifiableEntityException,
				client_iam.exceptions.ConcurrentModificationException,
				client_iam.exceptions.ServiceFailureException) as my_Error:
			logging.error(f"Error Message: {my_Error}")
			return_response['ErrorMessage'] = str(my_Error)
			return_response['Success'] = False
			if return_response['Success']:
				pass
			else:
				return return_response

		print(f"{ERASE_LINE}We've successfully removed the role{Fore.GREEN} {frole} {Fore.RESET}"
			  f"from account{Fore.GREEN} {ocredentials['AccountId']} {Fore.RESET}")
	except ClientError as my_Error:
		print(my_Error)
		pass


def roleexists(ocredentials, frole):
	import boto3

	session_iam = boto3.Session(
		aws_access_key_id=ocredentials['AccessKeyId'],
		aws_secret_access_key=ocredentials['SecretAccessKey'],
		aws_session_token=ocredentials['SessionToken']
	)

	client_iam = session_iam.client('iam')
	try:
		logging.info(f"{ERASE_LINE}Checking Account {ocredentials['AccountId']} for Role {frole}")
		response = client_iam.get_role(RoleName=frole)
		return True
	except ClientError as my_Error:
		if (my_Error.response['Error']['Code']) == 'NoSuchEntity':
			logging.warning("Role %s doesn't exist in account %s", frole, ocredentials['AccountId'])
	return False


def get_credentials(fProfileList, fSkipAccounts, fRootOnly, fAccounts, fRegionList, fRolesToUse):
	"""
	fProfiles: This is a list (0..n) of profiles to be searched through
	fSkipAccounts: This is a list (0..n) of accounts that shouldn't be checked or impacted
	fRootOnly: This is a flag (True/ False) as to whether this script should impact this account only, or the Child accounts as well
	fAccounts: This is a list (0..n) of Account Numbers which this script should be limited to
	fRegionList: This is a list (1..n) of regions which this script should be run against.
	fRolesToUse: This is a list (0..n) of roles to try to access the child accounts, assuming the role used isn't a commonly used one.
		Commonly Used roles: [OrganizationAccountAccessRole, AWSCloudFormationStackSetExecutionRole, AWSControlTowerExecution, Owner]

	Returned Values:
	AccountList: A list of dictionaries, containing information about the accounts themselves - created by the "ChildAccounts" function of aws_acct_access from the account_class
	AllCredentials: A list of dictionaries of all the info and credentials for all child accounts, including those that we weren't able to get credentials for.
	"""
	AccountList = []
	AllCredentials = []

	if pProfiles is None:  # Default use case from the classes
		print("Using the default profile - gathering info")
		aws_acct = aws_acct_access()
		RegionList = Inventory_Modules.get_regions3(aws_acct, fRegionList)
		# This should populate the list "AllCreds" with the credentials for the relevant accounts.
		logging.info(f"Queueing default profile for credentials")
		profile = 'default'
		AllCredentials.extend(get_credentials_for_accounts_in_org(aws_acct, fSkipAccounts, fRootOnly, fAccounts, profile, RegionList, fRolesToUse))
		# TODO: There's a use-case here where oen of more of the accounts in 'fAccounts' doesn't show up in the list of accounts found by the profiles specified
		# 	In that case - it would be nice if this script pointed that out. Right now - it does not, yet.
		AccountList = aws_acct.ChildAccounts
	else:
		print(f"Capturing info for {len(ProfileList)} requested profiles {ProfileList}")
		for profile in fProfileList:
			# Eventually - getting credentials for a single account may require passing in the region in which it's valid, but not yet.
			try:
				aws_acct = aws_acct_access(profile)
				print(f"Validating {len(aws_acct.ChildAccounts)} accounts within {profile} profile now... ")
				RegionList = Inventory_Modules.get_regions3(aws_acct, fRegionList)
				logging.info(f"Queueing {profile} for credentials")
				# This should populate the list "AllCredentials" with the credentials for the relevant accounts.
				AllCredentials.extend(get_credentials_for_accounts_in_org(aws_acct, fSkipAccounts, fRootOnly, fAccounts, profile, RegionList, fRolesToUse))
				AccountList.extend(aws_acct.ChildAccounts)
			except AttributeError as my_Error:
				logging.error(f"Profile {profile} didn't work... Skipping")
				continue
	return AllCredentials, AccountList


##########################

ERASE_LINE = '\x1b[2K'

if pTiming:
	begin_time = time()

AllCredentials = []
AccountList = []
RegionList = ['us-east-1']
Results = []

ProfileList = Inventory_Modules.get_profiles(fSkipProfiles=pSkipProfiles, fprofiles=pProfiles)

AllCredentials, AccountList = get_credentials(ProfileList, pSkipAccounts, pRootOnly, pAccounts, RegionList, pRoleToUse)
AccountNum = len(set([acct['AccountId'] for acct in AllCredentials if 'AccountId' in acct]))

print()
UpdatedAccounts = 0

# If the user specified only one account to check, and that account isn't found within the credentials found, this line will alert them of that fact.
# However, if they specified multiple accounts to check, and SOME of them appeared, then they won't be notified of the ones that did NOT appear
if not AllCredentials:
	# print(f"{Fore.RED}The account{'' if len(pAccounts) == 1 else 's'} you requested to check {pAccounts} doesn't appear to be within the profiles you specified.{Fore.RESET}")
	print(f"{Fore.RED}The account you requested to check '{pAccounts}' doesn't appear to be within the profiles you specified.{Fore.RESET}")

for cred in AllCredentials:
	# account_credentials = Inventory_Modules.get_child_access3(aws_acct, cred['AccountId'], fRoleList=pRolesToUse)
	if not cred['Success']:
		print(f"Something failed in getting credentials for account {cred['AccountId']}\n"
			  f"We tried this list of roles '{cred['RolesTried']}', but none worked\n"
			  f"Error Message: {cred['ErrorMessage']}")
		continue
	# print(f"Checking account {cred['AccountId']} using role {cred['Role']}", end='\r')
	if cred['Role'] == pRoleNameToRemove:
		print(f"{Fore.RED}We gained access to this account using the role you specified to remove.\n"
			  f"Is this definitely what you want to do?{Fore.RESET}")
		# TODO: We ask a question here, but don't wait for an answer...
	# Checking to see if the role already exists
	if pRoleNameToCheck is not None:
		logging.info(f"Checking to see if role {pRoleNameToCheck} exists in account {cred['AccountId']}")
		if roleexists(cred, pRoleNameToCheck):
			Results.append({'AccountId': cred['AccountId'], 'Role': pRoleNameToCheck, 'Result': 'Role Exists'})
			UpdatedAccounts += 1
		else:
			Results.append({'AccountId': cred['AccountId'], 'Role': pRoleNameToCheck, 'Result': 'Nonexistent Role'})
	# If we're supposed to add the role and it already exists
	elif pRoleNameToAdd is not None and roleexists(cred, pRoleNameToAdd):
		logging.warning(f"Role {pRoleNameToAdd} already exists")
		continue
	# If we're supposed to remove the role and the role exists AND it's not the role we used to access the cred
	elif pRoleNameToRemove is not None and roleexists(cred, pRoleNameToRemove) and not (cred['Role'] == pRoleNameToAdd):
		logging.warning(f"Removing role {pRoleNameToRemove} from account {cred['AccountId']}")
		removerole(cred, pRoleNameToRemove)
		Results.append({'AccountId': cred['AccountId'], 'Role': pRoleNameToRemove, 'Result': 'Role Removed'})
		UpdatedAccounts += 1
	# If we're supposed to add the role
	elif pRoleNameToAdd is not None:
		createrole(cred, pRoleNameToAdd)
		Results.append({'AccountId': cred['AccountId'], 'Role': pRoleNameToAdd, 'Result': 'Role Created'})
		UpdatedAccounts += 1

sorted_Results = sorted(Results, key=lambda d: (d['AccountId']))
print()
# if verbose < 50:
# 	print(f"You supplied profiles including the following {len(AccountList)} accounts: {[item['AccountId'] for item in AccountList]}")
print()
if pAccounts is not None:
	print(f"You asked to check account{'' if len(pAccounts) == 1 else 's'} {pAccounts} under your supplied profiles")
else:
	print(f"We found {AccountNum} accounts provided within the profiles you provided")
	if verbose < 50:
		print(f"Of these, we successfully found creds for {len(Results)} accounts using ", end='')
		if pRoleToUse:
			print(f"the roles '{pRoleToUse}' you supplied")
		else:
			print(f"the roles we commonly use for access")

MissingAccounts = [item['AccountId'] for item in AllCredentials if not item['Success']]
if len(MissingAccounts) > 0:
	print()
	print(f"{Fore.RED}We were unsuccessful when checking the following {len(MissingAccounts)} accounts: {MissingAccounts}{Fore.RESET}")
	logging.warning(f"List of failed accounts:")
	for item in AllCredentials:
		logging.error(f"\t\t{item['AccountId']}")
		logging.warning(f"\t\t\tRoles Tried: {item['RolesTried']}")
		logging.info(f"\t\t\t\tRegions: {item['Region']}")

if pRoleNameToCheck is not None:
	print(f"We found {UpdatedAccounts} accounts that included the '{pRoleNameToCheck}' role")
	if verbose <= 40:
		for i in sorted_Results:
			print(f"\tLooking for role '{i['Role']}' in Account '{i['AccountId']}': {i['Result']}")
		# MissingAccounts = [item['AccountId'] for item in Results if not (item['Result'] == 'Role Exists')]
		# if len(MissingAccounts) > 0:
		# 	print(f"{Fore.RED}We didn't find {pRoleNameToCheck} in the following accounts: {MissingAccounts}{Fore.RESET}")
elif pRoleNameToAdd is not None:
	print(f"We updated {UpdatedAccounts} accounts to add the {pRoleNameToAdd} role")
elif pRoleNameToRemove is not None:
	print(f"We updated {UpdatedAccounts} accounts to remove the {pRoleNameToRemove} role")

if pTiming:
	print(ERASE_LINE)
	print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thanks for using the tool.")
print()
