#!/usr/bin/env python3


import re
import sys
from os.path import split
from datetime import timedelta, datetime, timezone
from time import time
from tqdm.auto import tqdm

from Inventory_Modules import display_results, get_all_credentials, find_ssm_parameters2
from colorama import init, Fore
from botocore.exceptions import ClientError
from ArgumentsClass import CommonArguments

import logging

init()
__version__ = "2024.05.07"
begin_time = time()
ERASE_LINE = '\x1b[2K'


##################
# Functions
##################

def parse_args(arguments):
	"""
	Description: Parses the arguments passed into the script
	@param arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		'--ALZ',
		help="Identify left-over parameters created by the ALZ solution",
		action="store_const",
		dest="ALZParam",
		const=True,
		default=False)
	local.add_argument(
		'-b', '--daysback',
		help="Only keep the last x days of Parameters (default 90)",
		dest="DaysBack",
		default=90)
	local.add_argument(
		'+delete',
		help="Deletion is not working currently (as of 6/22/23)",
		# help="Delete left-over parameters created by the ALZ solution. DOES NOT DELETE ANY OTHER PARAMETERS!!",
		action="store_const",
		dest="DeletionRun",
		const=True,
		default=False)
	return parser.my_parser.parse_args(arguments)


def find_ssm_parameters(f_credentialList):
	parameter_list = []
	print(f"Gathering parameters from {len(f_credentialList)} accounts and regions")
	for credential in tqdm(f_credentialList, desc="Gathering SSM Parameters", leave=True):
		try:
			# Since there could be 10,000 parameters stored in the Parameter Store - this function COULD take a long time
			# Consider making this a multi-threaded operation. Perhaps the library function would multi-thread it.
			parameter_list.extend(find_ssm_parameters2(credential))
		# if verbose < 50 or len(parameter_list) == 0:
		# 	print(f"Found a running total of {len(parameter_list)} parameters in account {Fore.RED}{credential['AccountNumber']}{Fore.RESET} in region {Fore.RED}{credential['Region']}{Fore.RESET}")
		except ClientError as my_Error:
			if 'AuthFailure' in str(my_Error):
				logging.error(f"Profile {credential['Profile']}: Authorization Failure for account {credential['AccountNumber']}")
	return parameter_list


##################
# Main
##################
if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccounts = args.Accounts
	pRootOnly = args.RootOnly
	ALZParam = args.ALZParam
	pTiming = args.Time
	pFilename = args.Filename
	DeletionRun = args.DeletionRun
	dtDaysBack = timedelta(days=int(args.DaysBack))
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	##########################
	ALZRegex = "/\w{8,8}-\w{4,4}-\w{4,4}-\w{4,4}-\w{12,12}/\w{3,3}"
	print()

	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)
	RegionList = list(set([x['Region'] for x in CredentialList]))
	AccountList = list(set([x['AccountId'] for x in CredentialList]))

	ParamsToDelete = []

	AllParameters = find_ssm_parameters(CredentialList)

	display_dict = {'AccountNumber'   : {'DisplayOrder': 1, 'Heading': 'Acct Number'},
	                'Region'          : {'DisplayOrder': 2, 'Heading': 'Region'},
	                'Name'            : {'DisplayOrder': 3, 'Heading': 'Parameter Name'},
	                'LastModifiedDate': {'DisplayOrder': 4, 'Heading': 'Last Modified'}}
	sorted_Parameters = sorted(AllParameters, key=lambda x: (x['AccountNumber'], x['Region'], x['Name']))
	display_results(sorted_Parameters, display_dict, 'Default', pFilename)

	if ALZParam:
		ALZParams = 0
		today = datetime.now(tz=timezone.utc)
		for y in range(len(AllParameters)):
			# If the parameter matches the string regex of "/2ac07efd-153d-4069-b7ad-0d18cc398b11/105" - then it should be a candidate for deletion
			# With Regex - I'm looking for "/\w{8,8}-\w{4,4}-\w{4,4}-\w{4,4}-\w{12,12}/\w{3,3}"
			ParameterDate = AllParameters[y]['LastModifiedDate']
			mydelta = today - ParameterDate  # this is a "timedelta" object
			p = re.compile(ALZRegex)  # Sets the regex to look for
			logging.info(f"Parameter{y}: {AllParameters[y]['Name']} with date {AllParameters[y]['LastModifiedDate']}")
			if p.match(AllParameters[y]['Name']) and mydelta > dtDaysBack:
				logging.error(f"Parameter {AllParameters[y]['Name']} with date of {AllParameters[y]['LastModifiedDate']} matched")
				ALZParams += 1
				ParamsToDelete.append({'Credentials': AllParameters[y]['credentials'],
				                       'Name'       : AllParameters[y]['Name']})

	if DeletionRun:
		print(f"Currently the deletion function for errored ALZ parameters isn't working. Please contact the author if this functionality is still needed for you... ")

		"""
		The reason this looks so weird, is that the SSM Parameters had to be deleted with a single API call, but the call could only take 10 parameters at a time, 
		so instead of multi-threading this deletion for one at a time (which would still have been a lot of work), I grouped the deletions to run 10 at a time. 
		However, that only worked when it was certain that the parameters found were all in the same account and the same region, to allow the API to run (one account / one region)
		So - since the update above allows this script to find parameters across accounts and regions. the deletion piece no longer works properly. 
		I can update it to figure a way to group the parameters by account and region, and then delete 10 at a time, but that's more work than I think is worthwhile, since I don't 
		think too many people are still using this script... Prove me wrong, and I'll write it...  
		"""

	print()
	print(ERASE_LINE)
	print(f"Found {len(AllParameters)} total parameters")
	print(f"And {ALZParams} of them were from buggy ALZ runs more than {dtDaysBack.days} days back") if ALZParam else None
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print()
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else None
	print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else None
	print()
	print(f"Found {len(AllParameters)} SSM parameters across {len(AccountList)} account{'' if len(AccountList) == 1 else 's'} across {len(RegionList)} region{'' if len(RegionList) == 1 else 's'}")
	print()
	print("Thank you for using this script")
	print(f"Your output was saved to {Fore.GREEN}'{pFilename}-{datetime.now().strftime('%y-%m-%d--%H:%M:%S')}'{Fore.RESET}") if pFilename is not None else None
	print()
