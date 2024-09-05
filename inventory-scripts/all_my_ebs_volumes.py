#!/usr/bin/env python3
import sys

from Inventory_Modules import display_results, get_all_credentials, find_account_volumes2
from ArgumentsClass import CommonArguments
from colorama import init, Fore
from botocore.exceptions import ClientError
from queue import Queue
from threading import Thread
from time import time
from tqdm.auto import tqdm

import logging

init()
__version__ = "2024.05.31"


##################
def parse_args(f_arguments):
	"""
	Description: Parses the arguments passed into the script
	@param f_arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""

	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.fragment()
	parser.rootOnly()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	return parser.my_parser.parse_args(f_arguments)


def present_results(fVolumesFound: list):
	"""
	Description: This will present the results found by the main function
	@param fVolumesFound: A list of all the volumes found across all the child accounts
	"""
	display_dict = {'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'VolumeName' : {'DisplayOrder': 4, 'Heading': 'Volume Name'},
					'VolumeId' : {'DisplayOrder': 5, 'Heading': 'Volume Id'},
	                'State'      : {'DisplayOrder': 5, 'Heading': 'State', 'Condition': ['available', 'creating', 'deleting', 'deleted', 'error']},
	                'Size'       : {'DisplayOrder': 6, 'Heading': 'Size (GBs)'},
	                # 'KmsKeyId'   : {'DisplayOrder': 9, 'Heading': 'Encryption Key'},
	                'Throughput' : {'DisplayOrder': 8, 'Heading': 'Throughput'},
	                'VolumeType' : {'DisplayOrder': 7, 'Heading': 'Type'}}
	OrphanedVolumes = [x for x in fVolumesFound if x['State'] in ['available', 'error']]
	RegionsFound = list(set([x['Region'] for x in fVolumesFound]))
	AccountsFound = list(set([x['AccountId'] for x in fVolumesFound]))

	# de-dup this list
	de_dupe_VolumesFound = []
	seen = set()
	for volume in fVolumesFound:
			key = volume['VolumeId']
			if key not in seen:
				seen.add(key)
				de_dupe_VolumesFound.append(volume)

	sorted_Volumes_Found = sorted(de_dupe_VolumesFound, key=lambda x: (x['MgmtAccount'], x['AccountId'], x['Region'], x['VolumeName'], x['Size']))
	display_results(sorted_Volumes_Found, display_dict, 'None', pFilename)

	print()
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
	print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
	print(f"This output has also been written to a file beginning with '{pFilename}' + the date and time") if pFilename is not None else ""
	print()
	print(f"Found {len(VolumesFound)} volumes across {len(AccountsFound)} account{'' if len(AccountsFound) == 1 else 's'} "
	      f"across {len(RegionsFound)} region{'' if len(RegionsFound) == 1 else 's'}")
	print()
	print(f"{Fore.RED}Found {len(OrphanedVolumes)} volume{'' if len(OrphanedVolumes) == 1 else 's'} that aren't attached to anything.\n"
	      f"Th{'is' if len(OrphanedVolumes) == 1 else 'ese'} are likely orphaned, and should be considered for deletion to save costs.{Fore.RESET}") if len(OrphanedVolumes) > 0 else ""


def check_accounts_for_ebs_volumes(f_CredentialList, f_fragment_list=None):
	"""
	Note that this function takes a list of Credentials and checks for EBS Volumes in every account it has creds for
	@param f_CredentialList: List of credentials for all accounts to check
	@param f_fragment_list: List of name tag fragments to limit the searching to
	@return:
	"""

	class FindVolumes(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				# c_account_credentials, c_region, c_text_to_find, c_PlacesToLook, c_PlaceCount = self.queue.get()
				c_account_credentials, c_region, c_fragment = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					# account_volumes = find_account_volumes2(c_account_credentials, c_text_to_find)
					account_volumes = find_account_volumes2(c_account_credentials)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for _ in range(len(account_volumes)):
						account_volumes[_]['MgmtAccount'] = c_account_credentials['MgmtAccount']
					AllVolumes.extend(account_volumes)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					logging.info(f"{ERASE_LINE}Finished finding EBS volumes in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					pbar.update()
					self.queue.task_done()

	if f_fragment_list is None:
		f_fragment_list = []
	AllVolumes = []
	WorkerThreads = min(len(f_CredentialList), 50)

	checkqueue = Queue()

	pbar = tqdm(desc=f'Finding ebs volumes from {len(f_CredentialList)} accounts and regions',
	            total=len(f_CredentialList), unit=' accounts & regions'
	            )

	for x in range(WorkerThreads):
		worker = FindVolumes(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in f_CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			checkqueue.put((credential, credential['Region'], f_fragment_list))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in '{credential['Region']}' region")
				logging.warning(f"It's possible that the region '{credential['Region']}' hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllVolumes


##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pAccounts = args.Accounts
	pFragments = args.Fragments
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pRootOnly = args.RootOnly
	# pText_to_find = args.pText_To_Find
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	ERASE_LINE = '\x1b[2K'

	begin_time = time()
	print()
	print(f"Checking for EBS Volumes... ")
	logging.info(f"Profiles: {pProfiles}")
	print()

	# Get credentials for all accounts in scope.
	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)
	# RegionList = list(set([x['Region'] for x in CredentialList]))
	# AccountList = list(set([x['AccountId'] for x in CredentialList]))

	# Collect EBS Information
	VolumesFound = check_accounts_for_ebs_volumes(CredentialList, pFragments)

	# Display Results
	present_results(VolumesFound)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thank you for using this script")
print()
