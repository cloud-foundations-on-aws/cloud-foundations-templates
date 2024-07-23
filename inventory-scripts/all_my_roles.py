#!/usr/bin/env python3
import sys

from Inventory_Modules import display_results, get_all_credentials, find_in
import boto3
from ArgumentsClass import CommonArguments
from time import sleep, time
from colorama import init, Fore
from botocore.exceptions import ClientError
import logging

init()
__version__ = "2023.11.06"

###########################
def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all roles within any of the accounts we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.fragment()
	parser.deletion()
	parser.rootOnly()
	parser.verbosity()
	parser.timing()
	parser.save_to_file()
	parser.version(__version__)
	parser.my_parser.add_argument(
		"+d", "+delete",
		dest="pDelete",
		action="store_const",
		const=True,
		default=False,
		help="Whether you'd like to delete that specified role.")
	return parser.my_parser.parse_args(args)

def my_delete_role(fRoleList):
	iam_session = boto3.Session(
		aws_access_key_id=fRoleList['AccessKeyId'],
		aws_secret_access_key=fRoleList['SecretAccessKey'],
		aws_session_token=fRoleList['SessionToken'],
		region_name=fRoleList['Region']
	)
	iam_client = iam_session.client('iam')
	try:
		attached_role_policies = iam_client.list_attached_role_policies(RoleName=fRoleList['RoleName'])['AttachedPolicies']
		for _ in range(len(attached_role_policies)):
			response = iam_client.detach_role_policy(
				RoleName=fRoleList['RoleName'],
				PolicyArn=attached_role_policies[_]['PolicyArn']
			)
		inline_role_policies = iam_client.list_role_policies(RoleName=fRoleList['RoleName'])['PolicyNames']
		for _ in range(len(inline_role_policies)):
			response = iam_client.delete_role_policy(
				RoleName=fRoleList['RoleName'],
				PolicyName=inline_role_policies[_]['PolicyName']
			)
		response = iam_client.delete_role(
			RoleName=fRoleList['RoleName']
		)
		return True
	except ClientError as my_Error:
		logging.error(f"Error: {my_Error}")
		return False

def find_and_collect_roles_across_accounts(fAllCredentials:list, frole_fragments:list) -> list:
	"""
	TODO: Need to add multi-threading here
	Description: Finds roles in Org Accounts that contains supplied fragments
	@param fAllCredentials: Listing of Credentials
	@param frole_fragments: list of strings to find roles that match
	@return: List of roles found across all accounts
	"""
	print()
	if pFragments is None:
		print(f"Listing out all roles across {len(fAllCredentials)} accounts")
		print()
	elif pExact:
		print(f"Looking for a role {Fore.RED}exactly{Fore.RESET} named one of these strings {frole_fragments} across {len(fAllCredentials)} accounts")
		print()
	else:
		print(f"Looking for a role containing one of these strings {frole_fragments} across {len(fAllCredentials)} accounts")
		print()

	Roles = []
	for account in fAllCredentials:
		if account['Success']:
			iam_session = boto3.Session(aws_access_key_id=account['AccessKeyId'],
			                            aws_secret_access_key=account['SecretAccessKey'],
			                            aws_session_token=account['SessionToken'],
			                            region_name=account['Region'])
			iam_client = iam_session.client('iam')
		else:
			continue
		try:
			response = iam_client.list_roles()
			for i in range(len(response['Roles'])):
				Roles.append({
					'AccessKeyId'    : account['AccessKeyId'],
					'SecretAccessKey': account['SecretAccessKey'],
					'SessionToken'   : account['SessionToken'],
					'MgmtAcct'       : account['MgmtAccount'],
					'Region'         : account['Region'],
					'AccountId'      : account['AccountNumber'],
					'RoleName'       : response['Roles'][i]['RoleName']
				})
			num_of_roles_in_account = len(response['Roles'])
			while response['IsTruncated']:
				response = iam_client.list_roles(Marker=response['Marker'])
				for i in range(len(response['Roles'])):
					Roles.append({
						'AccessKeyId'    : account['AccessKeyId'],
						'SecretAccessKey': account['SecretAccessKey'],
						'SessionToken'   : account['SessionToken'],
						'MgmtAcct'       : account['MgmtAccount'],
						'Region'         : account['Region'],
						'AccountId'      : account['AccountNumber'],
						'RoleName'       : response['Roles'][i]['RoleName']
					})
				num_of_roles_in_account = len(response['Roles'])
			print(f"Found {num_of_roles_in_account} roles in account {account['AccountNumber']}", end="\r")
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				print(f"\nAuthorization Failure for account {account['AccountId']}")
			else:
				print(f"\nError: {my_Error}")
	if pFragments is None:
		found_roles = Roles
	else:
		found_roles = [x for x in Roles if find_in([x['RoleName']], pFragments, pExact)]
	return found_roles

def delete_roles(roles_to_delete):
	confirm = False
	if pDelete:
		if pFragments is None:
			print(f"You asked to delete roles, but didn't give a specific role to delete, so we're not going to delete anything.")
		elif len(roles_to_delete) > 0 and not pForce:
			print(f"Your specified role fragment matched at least 1 role.\n"
			      f"Please confirm you want to really delete all {len(roles_to_delete)} roles found")
			confirm = (input(f"Really delete {len(roles_to_delete)} across {len(AllCredentials)} accounts. Are you still sure? (y/n): ").lower() == 'y')
		elif pForce and len(roles_to_delete) > 0:
			print(f"You specified a fragment that matched multiple roles.\n"
			      f"And you specified the 'FORCE' parameter - so we're not asking again, BUT we'll wait {time_to_sleep} seconds to give you the option to Ctrl-C here...")
			sleep(time_to_sleep)

	if (pDelete and confirm) or (pDelete and pForce):
		for i in range(len(roles_to_delete)):
			logging.info(f"Deleting role {roles_to_delete[i]['RoleName']} from account {roles_to_delete[i]['AccountId']}")
			result = my_delete_role(roles_to_delete[i])
			if result:
				roles_to_delete[i].update({'Action': 'deleted'})
			else:
				roles_to_delete[i].update({'Action': 'delete failed'})

###########################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	# pRole = args.pRole
	pFragments = args.Fragments
	pAccounts = args.Accounts
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pDelete = args.pDelete
	pForce = args.Force
	pExact = args.Exact
	pRootOnly = args.RootOnly
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(""message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)


	ERASE_LINE = '\x1b[2K'
	time_to_sleep = 5
	begin_time = time()

	print()

	# Get credentials for all Child Accounts
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)
	# Collect the stacksets, AccountList and RegionList involved
	all_found_roles = find_and_collect_roles_across_accounts(AllCredentials, pFragments)
	# Display the information we've found this far
	sorted_Results = sorted(all_found_roles, key=lambda d: (d['MgmtAcct'], d['AccountId'], d['RoleName']))
	display_dict = {'AccountId': {'DisplayOrder': 2, 'Heading': 'Account Number'},
	                'MgmtAcct' : {'DisplayOrder': 1, 'Heading': 'Parent Acct'},
	                'RoleName' : {'DisplayOrder': 3, 'Heading': 'Role Name'},
	                'Action'   : {'DisplayOrder': 4, 'Heading': 'Action Taken'}}

	display_results(sorted_Results, display_dict, "No Action", pFilename)

	# Modify stacks, if requested
	if pDelete:
		delete_roles(sorted_Results)

	print()
	if pFragments is None:
		print(f"Found {len(sorted_Results)} roles across {len(AllCredentials)} accounts")
	else:
		print(f"Found {len(sorted_Results)} instances where role containing {pFragments} was found across {len(AllCredentials)} accounts")

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print()
	print("Thanks for using this script...")
	print()
