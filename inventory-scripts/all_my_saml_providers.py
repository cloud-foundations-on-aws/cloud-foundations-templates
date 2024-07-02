#!/usr/bin/env python3
import logging
import sys
from time import time
from os.path import split

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, find_saml_components_in_acct2, get_child_access3
from account_class import aws_acct_access

init()
__version__ = "2024.03.27"

begin_time = time()
ERASE_LINE = '\x1b[2K'


##################

def parse_args(args):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()
	parser.singleregion()
	parser.roletouse()
	parser.verbosity()
	parser.save_to_file()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"+delete", "+forreal",
		dest="DeletionRun",
		const=True,
		default=False,
		action="store_const",
		help="This will delete the identity providers found - without any opportunity to confirm. Be careful!!")
	return parser.my_parser.parse_args(args)


def all_my_saml_providers(faws_acct: aws_acct_access, fChildAccounts:list, f_access_role=None) -> list:
	"""
	TODO Needs multi-threading
	Description: Finds all saml providers within the Children Accounts
	@param fChildAccounts: The list of child accounts to check
	@return: A list of the SAML providers it's found
	"""
	IdpsFound = []

	for account in fChildAccounts:
		try:
			if account['AccountStatus'] == 'ACTIVE':
				print(f"{ERASE_LINE}Getting credentials for account {account['AccountId']}", end="\r")
				try:
					account_credentials = get_child_access3(faws_acct, account['AccountId'], pRegion, f_access_role)
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						print(f"{pProfile}: Authorization Failure for account {account['AccountId']}")
					else:
						print(f"{pProfile}: Other kind of failure for account {account['AccountId']}")
						print(my_Error)
					continue

				idpNum = 0
				try:
					Idps = find_saml_components_in_acct2(account_credentials)
					idpNum = len(Idps)
					logging.info(f"Account: {account['AccountId']} | Region: {pRegion} | Found {idpNum} Idps")
					logging.info(f"{ERASE_LINE}{Fore.RED}Account: {account['AccountId']} pRegion: {pRegion} Found {idpNum} Idps.{Fore.RESET}")

					if idpNum > 0:
						for idp in Idps:
							logging.info(f"Arn: {idp['Arn']}")
							NameStart = idp['Arn'].find('/') + 1
							logging.debug(f"Name starts at character: {NameStart}")
							IdpName = idp['Arn'][NameStart:]
							IdpsFound.append({
								'MgmtAccount'  : account_credentials['MgmtAccount'],
								'AccountNumber': account_credentials['AccountId'],
								'Region'       : account_credentials['Region'],
								'IdpName'      : IdpName,
								'Arn'          : idp['Arn']})
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						print(f"{account['AccountId']}: Authorization Failure")
			else:
				print(ERASE_LINE, f"Skipping account {account['AccountId']} since it's SUSPENDED or CLOSED", end="\r")
		except KeyError as my_Error:
			logging.error(f"Key Error: {my_Error}")
			continue
	return IdpsFound


def delete_idps(faws_acct: aws_acct_access, idps_found: list):
	for idp in idps_found:
		account_credentials = get_child_access3(faws_acct, idp['AccountNumber'])
		session_aws = boto3.Session(region_name=idp['pRegion'],
		                            aws_access_key_id=account_credentials['AccessKeyId'],
		                            aws_secret_access_key=account_credentials['SecretAccessKey'],
		                            aws_session_token=account_credentials['SessionToken'])
		iam_client = session_aws.client('iam')
		print(f"Deleting Idp {idp['IdpName']} from account {idp['AccountId']} in pRegion {idp['pRegion']}")
		response = iam_client.delete_saml_provider(SAMLProviderArn=idp['Arn'])


##################

if __name__ == "__main__":
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegion = args.Region
	verbose = args.loglevel
	pTiming = args.Time
	pAccessRole = args.AccessRole
	pFilename = args.Filename
	DeletionRun = args.DeletionRun

	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")

	print()

	# Get credentials
	aws_acct = aws_acct_access(pProfile)
	ChildAccounts = aws_acct.ChildAccounts

	# Find the SAML providers
	IdpsFound = all_my_saml_providers(aws_acct,ChildAccounts, pAccessRole)
	print(f"{ERASE_LINE}")
	# Display results
	display_dict = {'MgmtAccount'  : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountNumber': {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'       : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'IdpName'      : {'DisplayOrder': 4, 'Heading': 'IdP Name'},
	                'Arn'          : {'DisplayOrder': 5, 'Heading': 'Arn'}}
	sorted_results = sorted(IdpsFound, key=lambda x: (x['AccountNumber'], x['Region'], x['IdpName']))
	display_results(sorted_results, display_dict, None, pFilename)
	AccountsFound = list(set([x['AccountNumber'] for x in IdpsFound]))
	RegionsFound = list(set([x['Region'] for x in IdpsFound]))
	print()
	print(f"{Fore.RED}Found {len(IdpsFound)} Idps across {len(AccountsFound)} accounts in {len(RegionsFound)} regions{Fore.RESET}")
	print()

	# Delete saml providers if requested
	if DeletionRun:
		logging.warning(f"Deleting {len(IdpsFound)} Idps")
		delete_idps(aws_acct, IdpsFound)

	print()
	if pTiming:
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
		print()
	print("Thanks for using this script...")
	print()
