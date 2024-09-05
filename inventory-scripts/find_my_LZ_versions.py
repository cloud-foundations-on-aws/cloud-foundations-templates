#!/usr/bin/env python3

import Inventory_Modules
from ArgumentsClass import CommonArguments
import boto3
from colorama import init
from botocore.exceptions import ClientError, CredentialRetrievalError, InvalidConfigError

import logging

init()

__version__ = '2023.05.31'

parser = CommonArguments()
parser.multiprofile()
parser.verbosity()
parser.version(__version__)
args = parser.my_parser.parse_args()

pProfiles = args.Profiles
verbose = args.loglevel
logging.basicConfig(level=args.loglevel,
					format="[%(filename)s:%(lineno)s:%(levelname)s - %(funcName)30s() ] %(message)s")

##########################
ERASE_LINE = '\x1b[2K'
SkipProfiles = ['default']

if pProfiles is None:
	print(f"You've provided no profile, so we'll use the default")
	AllProfiles = ['default']
elif 'all' in pProfiles or 'ALL' in pProfiles or 'All' in pProfiles:
	logging.info(f"You specified 'all' as the profile, so we're going to check ALL of the profiles to find all of the management accounts, and list out all of their ALZ versions.")
	print("You've specified multiple profiles, so we've got to find them, determine which profiles represent Management Accounts, \n"
		  "and then parse through those. This will take a few moments.")
	AllProfiles = Inventory_Modules.get_profiles(fSkipProfiles=SkipProfiles, fprofiles=pProfiles)
else:
	AllProfiles = Inventory_Modules.get_profiles(fSkipProfiles=SkipProfiles, fprofiles=pProfiles)

ALZProfiles = []
for profile in AllProfiles:
	print(f"{ERASE_LINE}Checking profile: {profile}", end='\r')
	try:
		ALZMgmntAcct = Inventory_Modules.find_if_alz(profile)
		if ALZMgmntAcct['ALZ']:
			accountnum = Inventory_Modules.find_account_number(profile)
			ALZProfiles.append({
				'Profile': profile,
				'Acctnum': accountnum,
				'Region' : ALZMgmntAcct['Region']
			})
	except ClientError as my_Error:
		if str(my_Error).find("UnrecognizedClientException") > 0:
			logging.error("%s: Security Issue", profile)
		elif str(my_Error).find("InvalidClientTokenId") > 0:
			logging.error("%s: Security Token is bad - probably a bad entry in config", profile)
			pass
	except CredentialRetrievalError as my_Error:
		if str(my_Error).find("CredentialRetrievalError") > 0:
			logging.error("%s: Some custom process isn't working", profile)
			pass
	except InvalidConfigError as my_Error:
		if str(my_Error).find("InvalidConfigError") > 0:
			logging.error(
				"%s: profile is invalid. Probably due to a config profile based on a credential that doesn't work",
				profile)
			pass

print(ERASE_LINE)
fmt = '%-20s %-13s %-15s %-35s %-21s'
print(fmt % ("Profile", "Account", "Region", "ALZ Stack Name", "ALZ Version"))
print(fmt % ("-------", "-------", "------", "--------------", "-----------"))

for item in ALZProfiles:
	aws_session = boto3.Session(profile_name=item['Profile'], region_name=item['Region'])
	aws_client = aws_session.client('cloudformation')
	stack_list = aws_client.describe_stacks()['Stacks']
	for i in range(len(stack_list)):
		logging.warning(f"Checking stack {stack_list[i]['StackName']} to see if it is the ALZ initiation stack")
		if 'Description' in stack_list[i].keys() and stack_list[i]['Description'].find("SO0044") > 0:
			for j in range(len(stack_list[i]['Outputs'])):
				if stack_list[i]['Outputs'][j]['OutputKey'] == 'LandingZoneSolutionVersion':
					ALZVersion = stack_list[i]['Outputs'][j]['OutputValue']
					print(fmt % (
						item['Profile'], item['Acctnum'], item['Region'], stack_list[i]['StackName'], ALZVersion))

print(ERASE_LINE)
print(f"Checked {len(AllProfiles)} accounts/ Orgs. Found {len(ALZProfiles)} ALZs")
print()
print("Thank you for using this script.")
print()
