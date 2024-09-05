#!/usr/bin/env python3

import logging
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, get_all_credentials, get_region_azs2
from time import time
from colorama import init, Fore
import sys

init()
__version__ = "2024.03.06"
ERASE_LINE = '\x1b[2K'
begin_time = time()


###########################
# Functions
###########################
def parse_args(args):
	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.timing()
	parser.save_to_file()
	parser.rolestouse()
	parser.verbosity()
	parser.version(__version__)
	return parser.my_parser.parse_args(args)


def azs_across_accounts(fProfiles, fRegionList, fSkipProfiles, fSkipAccounts, fAccountList, fTiming, fRootOnly, fverbose, fRoleList) -> dict:
	if fTiming:
		begin_time = time()
	logging.warning(f"These profiles are being checked {fProfiles}.")
	AllCredentials = get_all_credentials(fProfiles, fTiming, fSkipProfiles, fSkipAccounts, fRootOnly, fAccountList, fRegionList, fRoleList)
	OrgList = list(set([x['MgmtAccount'] for x in AllCredentials]))
	print(f"Please bear with us as we run through {len(OrgList)} organizations / standalone accounts")

	print(ERASE_LINE)

	AllOrgAZs = dict()
	SuccessfulCredentials = [x for x in AllCredentials if x['Success']]
	passnumber = 0
	for item in SuccessfulCredentials:
		if item['AccountNumber'] not in AllOrgAZs.keys():
			AllOrgAZs[item['AccountNumber']] = dict()
		passnumber += 1
		if item['Success']:
			region_azs = get_region_azs2(item)
			print(f"{ERASE_LINE}Looking at account {item['AccountNumber']} in region {item['Region']} -- {passnumber}/{len(SuccessfulCredentials)}", end='\r')
		AllOrgAZs[item['AccountNumber']][item['Region']] = region_azs
	return AllOrgAZs


###########################
# Main
###########################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfiles = args.Profiles
	pRegions = args.Regions
	pRootOnly = args.RootOnly
	pTiming = args.Time
	pSkipProfiles = args.SkipProfiles
	pSkipAccounts = args.SkipAccounts
	pverbose = args.loglevel
	pSaveFilename = args.Filename
	pAccountList = args.Accounts
	pRoleList = args.AccessRoles
	# Setup logging levels
	logging.basicConfig(level=pverbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	print(f"Collecting credentials for all accounts in your org, across multiple regions")
	AllOrgAZs = azs_across_accounts(pProfiles, pRegions, pSkipProfiles, pSkipAccounts, pAccountList, pTiming, pRootOnly, pverbose, pRoleList)
	histogram = list()
	for account, account_info in AllOrgAZs.items():
		for region, az_info in account_info.items():
			for az in az_info:
				if az['ZoneType'] == 'availability-zone':
					# print(az)
					histogram.append({'AccountNumber': account,
					                  'Region'       : az['Region'],
					                  'Name'         : az['ZoneName'],
					                  'Id'           : az['ZoneId']})

	summary = dict()
	for item in histogram:
		if item['AccountNumber'] not in summary.keys():  # item['AccountNumber'] not in t:
			summary[item['AccountNumber']] = dict()
			summary[item['AccountNumber']][item['Region']] = list()
			summary[item['AccountNumber']][item['Region']].append((item['Name'], item['Id']))
		elif item['AccountNumber'] in summary.keys() and item['Region'] not in summary[item['AccountNumber']].keys():
			summary[item['AccountNumber']][item['Region']] = list()
			summary[item['AccountNumber']][item['Region']].append((item['Name'], item['Id']))
		elif item['AccountNumber'] in summary.keys():
			summary[item['AccountNumber']][item['Region']].append((item['Name'], item['Id']))

	display_dict = {'AccountNumber': {'DisplayOrder': 1, 'Heading': 'Account Number'},
	                'Region'       : {'DisplayOrder': 2, 'Heading': 'Region Name'},
	                'ZoneName'     : {'DisplayOrder': 3, 'Heading': 'Zone Name'},
	                'ZoneId'       : {'DisplayOrder': 4, 'Heading': 'Zone Id'},
	                'ZoneType'     : {'DisplayOrder': 5, 'Heading': 'Zone Type'}}
	# How to sort a dictionary by the key:
	sorted_summary = dict(sorted(summary.items()))
	# sorted_Results = sorted(summary, key=lambda d: (d['MgmtAccount'], d['AccountId'], d['Region']))
	display_results(summary, display_dict, "None", pSaveFilename)

	print()
	if pTiming:
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print("Thanks for using this script")
	print()
