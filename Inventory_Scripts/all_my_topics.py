#!/usr/bin/env python3
import logging
import sys
from queue import Queue
from threading import Thread
from time import time

from botocore.exceptions import ClientError
from colorama import Fore, init

import Inventory_Modules
from ArgumentsClass import CommonArguments
from Inventory_Modules import display_results, get_all_credentials

init()
__version__ = "2023.11.08"
begin_time = time()

def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	parser.my_parser.description = "Finding all the topics for the accounts we can find... "
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.fragment()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	return parser.my_parser.parse_args(args)


def find_topics(CredentialList:list, ftopic_frag:str=None, fexact:bool=False)->list:
	"""
	Description: Note that this function takes a list of Credentials and checks for topics in every account it has creds for
	@param CredentialList: List of credentials
	@param ftopic_frag: topic fragment
	@return: list of topics found in all found accounts
	"""

	class FindTopics(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_topic_frag, c_exact, c_PlacesToLook, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					account_topics = Inventory_Modules.find_sns_topics2(c_account_credentials, c_topic_frag, c_exact)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for topic in account_topics:
						AllTopics.append({'MgmtAccount': c_account_credentials['MgmtAccount'],
						                  'AccountId'  : c_account_credentials['AccountId'],
						                  'Region'     : c_account_credentials['Region'],
						                  'TopicName'  : topic})
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					# print(f"{ERASE_LINE}Finished finding Topics in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']} - {c_PlaceCount} / {c_PlacesToLook}", end='\r')
					self.queue.task_done()

	checkqueue = Queue()

	AllTopics = []
	PlaceCount = 0
	PlacesToLook = len(CredentialList)
	WorkerThreads = min(len(CredentialList), 50)

	for x in range(WorkerThreads):
		worker = FindTopics(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		# for region in fRegionList:
		try:
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			checkqueue.put((credential, ftopic_frag, fexact, PlacesToLook, PlaceCount))
			PlaceCount += 1
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	return AllTopics

def present_results(f_data_found: list):
	"""
	Description: Shows off results at the end
	@param f_data_found: List of Topics found and their attributes.
	"""
	display_dict = {'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'TopicName'  : {'DisplayOrder': 4, 'Heading': 'Topic Name'}}
	AccountNum = len(set([acct['AccountId'] for acct in AllCredentials]))
	RegionNum = len(set([acct['Region'] for acct in AllCredentials]))
	sorted_Topics_Found = sorted(f_data_found, key=lambda x: (x['MgmtAccount'], x['AccountId'], x['Region'], x['TopicName']))
	display_results(sorted_Topics_Found, display_dict, 'None', pFilename)
	print()
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
	print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
	print(f"The output has also been written to a file beginning with '{pFilename}' + the date and time") if pFilename is not None else ""
	print()
	print(f"Found {len(f_data_found)} topics across {AccountNum} accounts across {RegionNum} regions")


##########################
ERASE_LINE = '\x1b[2K'

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegions = args.Regions
	pAccounts = args.Accounts
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pRootOnly = args.RootOnly
	pExact = args.Exact
	pTopicFrag = args.Fragments
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")

	# Get credentials
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegions)
	AllAccounts = list(set([x['AccountId'] for x in AllCredentials]))
	AllRegions = list(set([x['Region'] for x in AllCredentials]))
	print()
	# RegionList = Inventory_Modules.get_ec2_regions3(aws_acct, pRegions)
	# ChildAccounts = aws_acct.ChildAccounts
	logging.info(f"# of Regions: {len(AllRegions)}")
	logging.info(f"# of Child Accounts: {len(AllAccounts)}")
	account_credentials = None

	# Find topics
	all_topics_found = find_topics(AllCredentials, pTopicFrag, pExact)

	# Display data
	present_results(all_topics_found)

	print()
	if pTiming:
		print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")
		print()
print("Thank you for using this script.")
