#!/usr/bin/env python3

# import boto3
import sys
import Inventory_Modules
from Inventory_Modules import display_results
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
from time import time
from colorama import init, Fore
from botocore.exceptions import ClientError

import logging

init()

__version__ = '2024.09.23'

def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all rds instances within any of the accounts we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	return parser.my_parser.parse_args(args)


def check_accounts_for_instances(faws_acct: aws_acct_access, fRegionList: list = None) -> list:
	"""
	Description: Note that this function checks the account AND any children accounts in the Org.
	@param faws_acct: the well-known account class object
	@param fRegionList: listing of regions to look in
	@return: The list of RDS instances found
	"""
	ChildAccounts = faws_acct.ChildAccounts
	AllInstances = []
	Instances = dict()
	if fRegionList is None:
		fRegionList = [faws_acct.Region]
	for account in ChildAccounts:
		acct_instances = []
		logging.info(f"Connecting to account {account['AccountId']}")
		try:
			account_credentials = Inventory_Modules.get_child_access3(faws_acct, account['AccountId'])
			logging.info(f"Connected to account {account['AccountId']} using role {account_credentials['Role']}")
		# TODO: We shouldn't refer to "account_credentials['Role']" below, if there was an error.
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"{account['AccountId']}: Authorization failure using role: {account_credentials['Role']}")
				logging.warning(my_Error)
			elif str(my_Error).find("AccessDenied") > 0:
				logging.error(f"{account['AccountId']}: Access Denied failure using role: {account_credentials['Role']}")
				logging.warning(my_Error)
			else:
				logging.error(f"{account['AccountId']}: Other kind of failure using role: {account_credentials['Role']}")
				logging.warning(my_Error)
			continue
		except AttributeError as my_Error:
			logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
			logging.warning(my_Error)
			continue
		for region in fRegionList:
			try:
				print(f"{ERASE_LINE}Checking account {account['AccountId']} in region {region}", end='\r')
				Instances = Inventory_Modules.find_account_rds_instances2(account_credentials, region)
				logging.info(f"Root Account: {faws_acct.acct_number} Account: {account['AccountId']} Region: {region} | Found {len(Instances['DBInstances'])} instances")
			except ClientError as my_Error:
				if "AuthFailure" in str(my_Error):
					logging.error(f"Authorization Failure accessing account {account['AccountId']} in {region} region")
					logging.warning(f"It's possible that the region {region} hasn't been opted-into")
					pass
			if 'DBInstances' in Instances.keys():
				for y in range(len(Instances['DBInstances'])):
					Name = Instances['DBInstances'][y]['DBName'] if 'DBName' in Instances['DBInstances'][y].keys() else 'No Name'
					LastBackup = Instances['DBInstances'][y]['LatestRestorableTime'] if 'LatestRestorableTime' in Instances['DBInstances'][y].keys() else 'No Backups'
					acct_instances.append({
						'MgmtAccount'  : faws_acct.acct_number,
						'AccountNumber': account['AccountId'],
						'Region'       : region,
						'InstanceType' : Instances['DBInstances'][y]['DBInstanceClass'],
						'State'        : Instances['DBInstances'][y]['DBInstanceStatus'],
						'DBId'         : Instances['DBInstances'][y]['DBInstanceIdentifier'],
						'Name'         : Name,
						'Size'         : Instances['DBInstances'][y]['AllocatedStorage'],
						'LastBackup'   : LastBackup,
						'Engine'       : Instances['DBInstances'][y]['Engine']
					})
		AllInstances.extend(acct_instances)
	return AllInstances


##################


if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pTiming = args.Time
	pFilename = args.Filename
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	ERASE_LINE = '\x1b[2K'
	begin_time = time()
	logging.info(f"Profiles: {pProfiles}")

	print()
	print(f"Checking for rds instances... ")
	print()

	InstancesFound = []
	AllChildAccounts = []
	RegionList = ['us-east-1']

	if pProfiles is None:  # Default use case from the classes
		logging.info("Using whatever the default profile is")
		aws_acct = aws_acct_access()
		RegionList = Inventory_Modules.get_regions3(aws_acct, pRegionList)
		logging.warning(f"Default profile will be used")
		InstancesFound.extend(check_accounts_for_instances(aws_acct, RegionList))
		AllChildAccounts.extend(aws_acct.ChildAccounts)
	else:
		ProfileList = Inventory_Modules.get_profiles(fprofiles=pProfiles, fSkipProfiles="skipplus")
		logging.warning(f"These profiles are being checked {ProfileList}.")
		for profile in ProfileList:
			aws_acct = aws_acct_access(profile)
			logging.warning(f"Looking at {profile} account now... ")
			RegionList = Inventory_Modules.get_regions3(aws_acct, pRegionList)
			InstancesFound.extend(check_accounts_for_instances(aws_acct, RegionList))
			AllChildAccounts.extend(aws_acct.ChildAccounts)

	# Display RDS Instances found
	display_dict = {'MgmtAccount'  : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountNumber': {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'       : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'InstanceType' : {'DisplayOrder': 4, 'Heading': 'Instance Type'},
	                'Name'         : {'DisplayOrder': 5, 'Heading': 'DB Name'},
	                'DBId'         : {'DisplayOrder': 6, 'Heading': 'Database ID'},
	                'Engine'       : {'DisplayOrder': 7, 'Heading': 'DB Engine'},
	                'Size'         : {'DisplayOrder': 8, 'Heading': 'Size (GB)'},
	                'LastBackup'   : {'DisplayOrder': 9, 'Heading': 'Latest Backup'},
	                'State'        : {'DisplayOrder': 10, 'Heading': 'State', 'Condition': ['Failed', 'Deleting', 'Maintenance', 'Rebooting', 'Upgrading']}}
	display_results(InstancesFound, display_dict, None, pFilename)

	print(ERASE_LINE)
	print(f"Found {len(InstancesFound)} instances across {len(AllChildAccounts)} accounts across {len(RegionList)} regions")
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print()
	print("Thank you for using this script")
	print()
