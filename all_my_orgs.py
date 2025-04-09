#!/usr/bin/env python3

import sys
from os.path import split
import logging
from ArgumentsClass import CommonArguments
from Inventory_Modules import get_profiles, get_org_accounts_from_profiles, display_results
from time import time
# from botocore.exceptions import ClientError, NoCredentialsError, InvalidConfigError
from colorama import init, Fore, Style

init()
__version__ = "2025.04.08"
ERASE_LINE = '\x1b[2K'
begin_time = time()


# TODO: If they provide a profile that isn't a root profile, you should find out which org it belongs to, and then show the org for that.
#  This will be difficult, since we don't know which profile that belongs to. Hmmm...


##################
# Functions
##################
def parse_args(f_arguments):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()
	parser.extendedargs()
	parser.rootOnly()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')

	local.add_argument(
		'-s', '-q', '--short',
		help="Display only brief listing of the profile accounts, and not the Child Accounts under them",
		action="store_const",
		dest="pShortform",
		const=True,
		default=False)
	local.add_argument(
		'-A', '--acct',
		help="Find which Org this account is a part of",
		nargs="*",
		dest="accountList",
		default=None)
	return parser.my_parser.parse_args(f_arguments)


def all_my_orgs(f_Profiles: list, f_SkipProfiles: list, f_AccountList: list, f_Timing: bool, f_RootOnly: bool, f_SaveFilename: str, f_Shortform: bool, f_verbose):
	ProfileList = get_profiles(fSkipProfiles=f_SkipProfiles, fprofiles=f_Profiles)
	# print("Capturing info for supplied profiles")
	logging.info(f"These profiles were requested {f_Profiles}.")
	logging.warning(f"These profiles are being checked {ProfileList}.")
	print(f"Please bear with us as we run through {len(ProfileList)} profiles")
	AllProfileAccounts = get_org_accounts_from_profiles(ProfileList)
	if not AllProfileAccounts:
		logging.info(f"No profiles were found, hence we're going to look at the environment variables")
		AllProfileAccounts = get_org_accounts_from_profiles()
	AccountList = []
	FailedProfiles = []
	OrgsFound = []

	# Print out the results
	if f_Timing:
		print()
		print(f"It's taken {Fore.GREEN}{time() - begin_time:.2f}{Fore.RESET} seconds to find profile accounts...")
		print()
	fmt = '%-23s %-15s %-15s %-12s %-10s'
	print("<------------------------------------>")
	print(fmt % ("Profile Name", "Account Number", "Payer Org Acct", "Org ID", "Root Acct?"))
	print(fmt % ("------------", "--------------", "--------------", "------", "----------"))

	for item in AllProfileAccounts:
		if not item['Success']:
			# If the profile failed, don't print anything and continue on.
			FailedProfiles.append(item['profile'])
			logging.error(f"{item['profile']} errored. Message: {item['ErrorMessage']}")
		else:
			if item['RootAcct']:
				# If the account is a root account, capture it for display later
				OrgsFound.append(item['MgmtAccount'])
			# Print results for all profiles
			item['AccountId'] = item['aws_acct'].acct_number
			item['AccountStatus'] = item['aws_acct'].AccountStatus
			# item['AccountEmail'] = item['aws_acct'].
			try:
				if f_RootOnly and not item['RootAcct']:
					# If we're only looking for root accounts, and this isn't one, don't print anything and continue on.
					continue
				else:
					logging.info(f"{item['profile']} was successful.")
					print(f"{Fore.RED if item['RootAcct'] else ''}{item['profile']:23s} {item['aws_acct'].acct_number:15s} {item['MgmtAccount']:15s} {str(item['OrgId']):12s} {item['RootAcct']}{Fore.RESET}")
			except TypeError as my_Error:
				logging.error(f"Error - {my_Error} on {item}")
				pass

	'''
	If I create a dictionary from the Root Accts and Root Profiles Lists - 
	I can use that to determine which profile belongs to the root user of my (child) account.
	But this dictionary is only guaranteed to be valid after ALL profiles have been checked, 
	so... it doesn't solve our issue - unless we don't write anything to the screen until *everything* is done, 
	and we keep all output in another dictionary - where we can populate the missing data at the end... 
	but that takes a long time, since nothing would be sent to the screen in the meantime.
	'''

	print(ERASE_LINE)
	print("-------------------")

	if f_Shortform:
		# The user specified "short-form" which means they don't want any information on child accounts.
		return_response = {'OrgsFound'         : OrgsFound,
		                   'FailedProfiles'    : FailedProfiles,
		                   'AllProfileAccounts': AllProfileAccounts}
	else:
		NumOfOrgAccounts = 0
		ClosedAccounts = []
		FailedAccounts = 0
		account = dict()
		ProfileNameLength = len("Organization's Profile")

		for item in AllProfileAccounts:
			# AllProfileAccounts holds the list of account class objects of the accounts associated with the profiles it found.
			if item['Success'] and not item['RootAcct']:
				account.update(item['aws_acct'].ChildAccounts[0])
				account.update({'Profile': item['profile']})
				AccountList.append(account.copy())
			elif item['Success'] and item['RootAcct']:
				for child_acct in item['aws_acct'].ChildAccounts:
					account.update(child_acct)
					account.update({'Profile': item['profile']})
					ProfileNameLength = max(len(item['profile']), ProfileNameLength) if item['profile'] else len("Organization's Profile")
					AccountList.append(account.copy())
					if not child_acct['AccountStatus'] == 'ACTIVE':
						ClosedAccounts.append(child_acct['AccountId'])

				NumOfOrgAccounts += len(item['aws_acct'].ChildAccounts)
			elif not item['Success']:
				FailedAccounts += 1
				continue

		# Display results on screen
		if f_SaveFilename is None:
			fmt = '%-23s %-15s'
			print()
			print(fmt % ("Organization's Profile", "Root Account"))
			print(fmt % ("----------------------", "------------"))
			for item in AllProfileAccounts:
				if item['Success'] and item['RootAcct']:
					print(f"{item['profile']:{ProfileNameLength + 2}s}", end='') if item['profile'] else print(f"{'No Profile available':{ProfileNameLength + 2}s}", end='')
					print(f"{Style.BRIGHT}{item['MgmtAccount']:15s}{Style.RESET_ALL}")
					print(f"\t{'Child Account Number':{len('Child Account Number')}s} {'Child Account Status':{len('Child Account Status')}s} {'Child Email Address'}")
					for child_acct in item['aws_acct'].ChildAccounts:
						print(f"\t{Fore.RED if not child_acct['AccountStatus'] == 'ACTIVE' else ''}{child_acct['AccountId']:{len('Child Account Number')}s} {child_acct['AccountStatus']:{len('Child Account Status')}s} {child_acct['AccountEmail']}{Fore.RESET}")

		elif f_SaveFilename is not None:
			# The user specified a file name, which means they want a (pipe-delimited) CSV file with the relevant output.
			display_dict = {'MgmtAccount'  : {'DisplayOrder': 1, 'Heading': 'Parent Acct'},
			                'AccountId'    : {'DisplayOrder': 2, 'Heading': 'Account Number'},
			                'AccountStatus': {'DisplayOrder': 3, 'Heading': 'Account Status', 'Condition': ['SUSPENDED', 'CLOSED']},
			                'AccountEmail' : {'DisplayOrder': 4, 'Heading': 'Email'}}
			if pRootOnly:
				sorted_Results = sorted(AllProfileAccounts, key=lambda d: (d['MgmtAccount'], d['AccountId']))
			else:
				sorted_Results = sorted(AccountList, key=lambda d: (d['MgmtAccount'], d['AccountId']))
			display_results(sorted_Results, display_dict, "None", f_SaveFilename)

		StandAloneAccounts = [x['AccountId'] for x in AccountList if x['MgmtAccount'] == x['AccountId'] and x['AccountEmail'] == 'Not an Org Management Account']
		FailedProfiles = [i['profile'] for i in AllProfileAccounts if not i['Success']]
		OrgsFound = [i['MgmtAccount'] for i in AllProfileAccounts if i['RootAcct']]
		StandAloneAccounts.sort()
		FailedProfiles.sort()
		OrgsFound.sort()
		ClosedAccounts.sort()

		print()
		print(f"Number of Organizations: {len(OrgsFound)}")
		print(f"Number of Organization Accounts: {NumOfOrgAccounts}")
		print(f"Number of Standalone Accounts: {len(StandAloneAccounts)}")
		print(f"Number of suspended or closed accounts: {len(ClosedAccounts)}")
		print(f"Number of profiles that failed: {len(FailedProfiles)}")
		if f_verbose < 50:
			print("----------------------")
			print(f"The following accounts are the Org Accounts: {OrgsFound}")
			print(f"The following accounts are Standalone: {StandAloneAccounts}") if len(StandAloneAccounts) > 0 else None
			print(f"The following accounts are closed or suspended: {ClosedAccounts}") if len(ClosedAccounts) > 0 else None
			print(f"The following profiles failed: {FailedProfiles}") if len(FailedProfiles) > 0 else None
			print("----------------------")
		print()
		return_response = {'OrgsFound'         : OrgsFound,
		                   'StandAloneAccounts': StandAloneAccounts,
		                   'ClosedAccounts'    : ClosedAccounts,
		                   'FailedProfiles'    : FailedProfiles,
		                   'AccountList'       : AccountList}

	if f_AccountList is not None:
		print(f"Found the requested account number{'' if len(AccountList) == 1 else 's'}:")
		for acct in AccountList:
			if acct['AccountId'] in f_AccountList:
				print(f"Profile: {acct['Profile']} | Org: {acct['MgmtAccount']} | Account: {acct['AccountId']} | Status: {acct['AccountStatus']} | Email: {acct['AccountEmail']}")

	return return_response


##################
# Main
##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfiles = args.Profiles
	pRootOnly = args.RootOnly
	pTiming = args.Time
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	verbose = args.loglevel
	pSaveFilename = args.Filename
	pShortform = args.pShortform
	pAccountList = args.accountList
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(processName)s %(threadName)s %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	all_my_orgs(pProfiles, pSkipProfiles, pAccountList, pTiming, pRootOnly, pSaveFilename, pShortform, verbose)

	print()
	if pTiming:
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
		print()
	print("Thanks for using this script")
	print()
