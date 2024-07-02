#!/usr/bin/env python3
import sys

# import boto3
import Inventory_Modules
from Inventory_Modules import display_results, get_all_credentials
from ArgumentsClass import CommonArguments
from threading import Thread
from queue import Queue
from colorama import init, Fore
from time import time
from botocore.exceptions import ClientError

import logging

init()
__version__ = "2023.10.03"


##################
def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.singleprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	return parser.my_parser.parse_args(args)


def check_account_for_cloudtrail(f_AllCredentials):
	"""
	Note that this function checks the passed in account credentials only
	@param f_AllCredentials: The list of Credentials
	@return: Returns a list of dicts of CloudTrails within every account / region provided
	"""

	class CheckAccountForCloudtrailThreaded(Thread):
		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				c_account_credentials = self.queue.get()
				try:
					logging.info(f"Checking account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					Trails = Inventory_Modules.find_account_cloudtrail2(c_account_credentials, c_account_credentials['Region'])
					logging.info(f"Root Account: {c_account_credentials['MgmtAccount']} Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(Trails['trailList'])} trails")
					if 'trailList' in Trails.keys():
						for y in range(len(Trails['trailList'])):
							AllTrails.append({'MgmtAccount'     : c_account_credentials['MgmtAccount'],
							                  'AccountId'       : c_account_credentials['AccountId'],
							                  'Region'          : c_account_credentials['Region'],
							                  'TrailName'       : Trails['trailList'][y]['Name'],
							                  'MultiRegion'     : Trails['trailList'][y]['IsMultiRegionTrail'],
							                  'OrgTrail'        : "OrgTrail" if Trails['trailList'][y]['IsOrganizationTrail'] else "Account Trail",
							                  'Bucket'          : Trails['trailList'][y]['S3BucketName'],
							                  'KMS'             : Trails['trailList'][y]['KmsKeyId'] if 'KmsKeyId' in Trails.keys() else None,
							                  'CloudWatchLogArn': Trails['trailList'][y]['CloudWatchLogsLogGroupArn'] if 'CloudWatchLogsLogGroupArn' in Trails.keys() else None,
							                  'HomeRegion'      : Trails['trailList'][y]['HomeRegion'] if 'HomeRegion' in Trails.keys() else None,
							                  'SNSTopicName'    : Trails['trailList'][y]['SNSTopicName'] if 'SNSTopicName' in Trails.keys() else None,
							                  })
						# AllTrails.append(Trails['trailList'])
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into")
						pass

				finally:
					print(".", end='')
					self.queue.task_done()

	AllTrails = []
	checkqueue = Queue()
	WorkerThreads = min(len(f_AllCredentials), 50)
	for x in range(WorkerThreads):
		worker = CheckAccountForCloudtrailThreaded(checkqueue)
		worker.daemon = True
		worker.start()

	for credential in f_AllCredentials:
		try:
			checkqueue.put(credential) if credential['Success'] else None
		except ClientError as my_Error:
			logging.error(f"Error: {my_Error}")
			pass

	checkqueue.join()
	return AllTrails


##################
ERASE_LINE = '\x1b[2K'

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfile = args.Profile
	pRegionList = args.Regions
	pSkipAccounts = args.SkipAccounts
	pAccounts = args.Accounts
	pSkipProfiles = args.SkipProfiles
	pRootOnly = args.RootOnly
	pSaveFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	logging.info(f"Single Profile: {pProfile}")
	if pTiming:
		begin_time = time()

	print()
	print(f"Checking for CloudTrails... ")
	print()

	TrailsFound = []
	AllCredentials = []
	CTSummary = {}
	OrgTrailInUse = False
	ExtraCloudTrails = 0
	if pSkipAccounts is None:
		pSkipAccounts = []

	# Get credentials for all accounts
	AllCredentials = get_all_credentials(pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)
	# Use credentials to connect to each account and check for CloudTrails
	TrailsFound = check_account_for_cloudtrail(AllCredentials)

	AllChildAccountandRegionList = [[item['MgmtAccount'], item['AccountId'], item['Region']] for item in AllCredentials]
	ChildAccountsandRegionsWithCloudTrail = [[item['MgmtAccount'], item['AccountId'], item['Region']] for item in TrailsFound]
	# The list of accounts and regions with NO CloudTrail
	ProblemAccountsandRegions = [item for item in AllChildAccountandRegionList if item not in ChildAccountsandRegionsWithCloudTrail]
	UniqueRegions = list(set([item['Region'] for item in AllCredentials]))
	# The list of accounts and regions with more than 1 CloudTrail
	if verbose < 50:
		for trail in TrailsFound:
			if trail['OrgTrail'] == 'OrgTrail':
				OrgTrailInUse = True
			if trail['AccountId'] not in CTSummary.keys():
				CTSummary[trail['AccountId']] = {}
				CTSummary[trail['AccountId']]['CloudTrailNum'] = 1
			if trail['Region'] not in CTSummary[trail['AccountId']].keys():
				CTSummary[trail['AccountId']][trail['Region']] = []
				CTSummary[trail['AccountId']]['CloudTrailNum'] += 1
				CTSummary[trail['AccountId']][trail['Region']].append({'TrailName': trail['TrailName'], 'Bucket': trail['Bucket'], 'OrgTrail': trail['OrgTrail']})
			elif trail['Region'] in CTSummary[trail['AccountId']].keys():
				# If we ever get to this part of the loop, it means there was an *additional* CloudTrail in use.
				ExtraCloudTrails += 1
				CTSummary[trail['AccountId']]['CloudTrailNum'] += 1
				CTSummary[trail['AccountId']][trail['Region']].append({'TrailName': trail['TrailName'], 'Bucket': trail['Bucket'], 'OrgTrail': trail['OrgTrail']})
	print()

	display_dict = {'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Account Number'},
					'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Parent Acct'},
					'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
					'TrailName'  : {'DisplayOrder': 4, 'Heading': 'Trail Name'},
					'OrgTrail'   : {'DisplayOrder': 5, 'Heading': 'Trail Type'},
					'Bucket'     : {'DisplayOrder': 6, 'Heading': 'S3 Bucket'}}
	sorted_Results = sorted(TrailsFound, key=lambda d: (d['MgmtAccount'], d['AccountId'], d['Region'], d['TrailName']))
	ProblemAccountsandRegions.sort()
	display_results(sorted_Results, display_dict, "None", pSaveFilename)

	if pSkipAccounts is not None:
		print(f"These accounts were skipped - as requested: {pSkipAccounts}")
	if pSkipProfiles is not None:
		print(f"These profiles were skipped - as requested: {pSkipProfiles}")
	if len(ProblemAccountsandRegions) > 0:
		print(f"There were {len(ProblemAccountsandRegions)} accounts and regions that didn't seem to have a CloudTrail associated: \n")
		for item in ProblemAccountsandRegions:
			print(item)
		print()
	else:
		print(f"All accounts and regions checked seem to have a CloudTrail associated")
	if verbose < 50:
		print(f"We found {ExtraCloudTrails} extra cloud trails in use")
		print(f"Which is silly because we have an Org Trail enabled for the whole Organization") if OrgTrailInUse else ''
		print(f"Removing these extra trails would save considerable money (can't really quantify how much right now)") if ExtraCloudTrails > 0 else ''
		print()
	print(f"Found {len(TrailsFound)} trails across {len(AllCredentials)} accounts/ regions across {len(UniqueRegions)} regions")
	print()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

print("Thank you for using this script")
print()
