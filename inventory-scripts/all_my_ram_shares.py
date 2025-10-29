#!/usr/bin/env python3

import sys
from os.path import split
from Inventory_Modules import get_all_credentials, display_results
from ArgumentsClass import CommonArguments
from queue import Queue
from threading import Thread, Lock
from time import time
import logging
import boto3
from botocore.exceptions import ClientError

# Optional imports
try:
	from colorama import init, Fore
	init()
except ImportError:
	class Fore:
		GREEN = ''
		RESET = ''

try:
	from tqdm.auto import tqdm
except ImportError:
	class tqdm:
		def __init__(self, *args, **kwargs):
			self.total = kwargs.get('total', 0)
			self.current = 0
		def update(self):
			self.current += 1
		def close(self):
			pass
__version__ = "2025.01.01"
ERASE_LINE = '\x1b[2K'
begin_time = time()


##################
# Functions
##################

def explain_columns():
	"""
	Description: Explains the meaning of each CSV column
	"""
	print("\nRAM Shares CSV Column Explanations:")
	print("=" * 50)
	print("MgmtAccount       - Management/Organization root account ID")
	print("OwnerAccount      - Account that created/owns the RAM share")
	print("ViewingAccount    - Account from whose perspective this row is viewed")
	print("ShareType         - OWNED (you created it) or RECEIVED (shared with you)")
	print("Region            - AWS region where the share exists")
	print("ShareName         - Name of the RAM resource share")
	print("Status            - Share status (ACTIVE, DELETING, FAILED, PENDING)")
	print("ResourceCount     - Number of resources in this share")
	print("SharedWithCount   - Number of principals (accounts/OUs) shared with")
	print("AllowExternalPrincipals - Whether external AWS accounts can be added")
	print("Resources         - List of shared resources (ARNs and types)")
	print("SharedWith        - Who the resources are shared with")
	print("ShareArn          - Unique ARN identifier for the RAM share")
	print("CreationTime      - When the share was created")
	print("LastUpdatedTime   - When the share was last modified")
	print("Tags              - Key-value tags associated with the share")
	print("\nKey Relationships:")
	print("- When OwnerAccount = ViewingAccount: ShareType = OWNED")
	print("- When OwnerAccount ≠ ViewingAccount: ShareType = RECEIVED")
	print("- OWNED shares show full resource details")
	print("- RECEIVED shares show limited details for security")
	print()

def parse_args(f_arguments):
	"""
	Description: Parses the arguments passed into the script
	@param f_arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all RAM shares within any of the accounts we have access to, given the profile(s) provided."
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rolestouse()
	parser.rootOnly()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"-s", "--status",
		dest="pStatus",
		choices=['ACTIVE', 'DELETING', 'FAILED', 'PENDING'],
		type=str,
		default=None,
		help="Filter RAM shares by status. Default is all statuses")
	local.add_argument(
		"-t", "--type",
		dest="pType",
		choices=['OWNED', 'RECEIVED'],
		type=str,
		default=None,
		help="Filter by share type - OWNED (shares you created) or RECEIVED (shares shared with you). Default is both")
	local.add_argument(
		"--explain-columns",
		dest="explainColumns",
		action="store_true",
		help="Show explanation of CSV column meanings and exit")
	return parser.my_parser.parse_args(f_arguments)


def find_ram_shares2(ocredentials, fStatus=None, fType=None):
	"""
	Description: Finds all RAM shares in an account/region
	@param ocredentials: AWS credentials dictionary
	@param fStatus: Filter by share status
	@param fType: Filter by share type (OWNED or RECEIVED)
	@return: List of RAM shares
	"""

	session_ram = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_ram = session_ram.client('ram')
	
	all_shares = []
	
	try:
		# Get owned shares
		if fType is None or fType == 'OWNED':
			logging.info(f"Looking for owned RAM shares in account {ocredentials['AccountId']} in region {ocredentials['Region']}")
			
			# Get resource shares owned by this account
			paginator = client_ram.get_paginator('get_resource_shares')
			page_iterator = paginator.paginate(resourceOwner='SELF')
			
			for page in page_iterator:
				for share in page['resourceShares']:
					if fStatus is None or share['status'] == fStatus:
						# Get associated resources for this share
						try:
							resources_response = client_ram.get_resource_share_associations(
								associationType='RESOURCE',
								resourceShareArns=[share['resourceShareArn']]
							)
							resources = resources_response.get('resourceShareAssociations', [])
						except ClientError as e:
							logging.warning(f"Could not get resources for share {share['name']}: {e}")
							resources = []
						
						# Get principals (who it's shared with)
						try:
							principals_response = client_ram.get_resource_share_associations(
								associationType='PRINCIPAL',
								resourceShareArns=[share['resourceShareArn']]
							)
							principals = principals_response.get('resourceShareAssociations', [])
						except ClientError as e:
							logging.warning(f"Could not get principals for share {share['name']}: {e}")
							principals = []
						
						share_info = {
							'ShareType': 'OWNED',
							'ShareArn': share['resourceShareArn'],
							'ShareName': share['name'],
							'Status': share['status'],
							'OwningAccountId': share['owningAccountId'],
							'CreationTime': str(share.get('creationTime', '')),
							'LastUpdatedTime': str(share.get('lastUpdatedTime', '')),
							'AllowExternalPrincipals': share.get('allowExternalPrincipals', False),
							'Tags': share.get('tags', []),
							'Resources': [{'Arn': r['associatedEntity'], 'Type': r.get('resourceType', 'Unknown'), 'Status': r.get('status', 'Unknown')} for r in resources],
							'SharedWith': [{'Principal': p['associatedEntity'], 'Status': p['status']} for p in principals]
						}
						all_shares.append(share_info)
	
		# Get received shares
		if fType is None or fType == 'RECEIVED':
			logging.info(f"Looking for received RAM shares in account {ocredentials['AccountId']} in region {ocredentials['Region']}")
			
			paginator = client_ram.get_paginator('get_resource_shares')
			page_iterator = paginator.paginate(resourceOwner='OTHER-ACCOUNTS')
			
			for page in page_iterator:
				for share in page['resourceShares']:
					if fStatus is None or share['status'] == fStatus:
						# Get associated resources for this share
						try:
							resources_response = client_ram.get_resource_share_associations(
								associationType='RESOURCE',
								resourceShareArns=[share['resourceShareArn']]
							)
							resources = resources_response.get('resourceShareAssociations', [])
						except ClientError as e:
							logging.debug(f"Account {ocredentials['AccountId']}: Could not get resources for received share {share['name']}: {e}")
							resources = []
						
						share_info = {
							'ShareType': 'RECEIVED',
							'ShareArn': share['resourceShareArn'],
							'ShareName': share['name'],
							'Status': share['status'],
							'OwningAccountId': share['owningAccountId'],
							'CreationTime': str(share.get('creationTime', '')),
							'LastUpdatedTime': str(share.get('lastUpdatedTime', '')),
							'AllowExternalPrincipals': share.get('allowExternalPrincipals', False),
							'Tags': share.get('tags', []),
							'Resources': [{'Arn': r['associatedEntity'], 'Type': r.get('resourceType', 'Unknown'), 'Status': r.get('status', 'Unknown')} for r in resources],
							'SharedWith': [f"This account ({ocredentials['AccountId']})"]
						}
						all_shares.append(share_info)
	
	except ClientError as e:
		if 'AccessDenied' in str(e):
			logging.warning(f"Access denied for RAM in account {ocredentials['AccountId']} region {ocredentials['Region']}")
		else:
			logging.error(f"Error accessing RAM in account {ocredentials['AccountId']} region {ocredentials['Region']}: {e}")
	
	return all_shares


def find_all_ram_shares(fAllCredentials: list, fStatus: str, fType: str) -> list:
	"""
	Description: Finds all RAM shares from all accounts/regions within the credentials supplied
	@param fAllCredentials: list of all credentials for all member accounts supplied
	@param fStatus: string determining share status filter
	@param fType: string determining share type filter (OWNED/RECEIVED)
	@return: Returns a list of RAM shares
	"""

	class FindRAMShares(Thread):

		def __init__(self, queue, ram_shares_lock):
			Thread.__init__(self)
			self.queue = queue
			self.ram_shares_lock = ram_shares_lock

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					# Check if we have valid credentials
					if 'AccessKeyId' not in c_account_credentials:
						logging.warning(f"No valid credentials for account {c_account_credentials['AccountId']}")
						self.queue.task_done()
						continue
					
					# Find RAM shares in this account/region
					ram_shares = find_ram_shares2(c_account_credentials, fStatus, fType)
					logging.info(f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(ram_shares)} RAM shares")
					
					for share in ram_shares:
						# Format resources
						resource_list = []
						for resource in share['Resources']:
							resource_list.append(f"{resource['Type']}: {resource['Arn']}")
						
						# Format principals/recipients based on share type
						if share['ShareType'] == 'OWNED':
							shared_with_list = []
							for principal in share['SharedWith']:
								if isinstance(principal, dict):
									shared_with_list.append(principal['Principal'])
								else:
									shared_with_list.append(str(principal))
							shared_with_display = '; '.join(shared_with_list) if shared_with_list else 'None'
						else:  # RECEIVED
							shared_with_list = [c_account_credentials['AccountId']]
							shared_with_display = f"This account ({c_account_credentials['AccountId']})"
						
						# Format tags
						tag_list = []
						for tag in share['Tags']:
							tag_list.append(f"{tag['key']}={tag['value']}")
						
						share_data = {
							'MgmtAccount': c_account_credentials['MgmtAccount'],
							'OwnerAccount': share['OwningAccountId'],
							'ViewingAccount': c_account_credentials['AccountId'],
							'ShareType': share['ShareType'],
							'Region': c_account_credentials['Region'],
							'ShareName': share['ShareName'],
							'ShareArn': share['ShareArn'],
							'Status': share['Status'],
							'ResourceCount': len(resource_list),
							'Resources': '; '.join(resource_list) if resource_list else 'None',
							'SharedWithCount': len(shared_with_list),
							'SharedWith': shared_with_display,
							'AllowExternalPrincipals': share['AllowExternalPrincipals'],
							'CreationTime': str(share['CreationTime']),
							'LastUpdatedTime': str(share['LastUpdatedTime']),
							'Tags': '; '.join(tag_list) if tag_list else 'None'
						}
						with self.ram_shares_lock:
							AllRAMShares.append(share_data)
				except Exception as my_Error:
					logging.error(f"Failed to find RAM shares in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					logging.error(f"Error: {my_Error}")
					logging.debug(f"Error details: {my_Error}", exc_info=True)
				finally:
					self.queue.task_done()

	AllRAMShares = []
	ram_shares_lock = Lock()
	WorkerThreads = min(len(fAllCredentials), 50)

	work_queue = Queue()
	for x in range(WorkerThreads):
		worker = FindRAMShares(work_queue, ram_shares_lock)
		worker.daemon = True
		worker.start()

	for credential in fAllCredentials:
		logging.info(f"Queuing account {credential['AccountId']} in region {credential['Region']}")
		work_queue.put(credential)

	work_queue.join()
	return AllRAMShares


##################
# Main
##################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	
	# Handle column explanation request
	if args.explainColumns:
		explain_columns()
		sys.exit(0)
	
	verbose = args.loglevel < 50
	logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

	print()
	print(f"Checking for RAM shares...")
	print()

	# Get credentials for all accounts  
	profiles_list = args.Profiles if args.Profiles else []
	Credentials = get_all_credentials(profiles_list, args.Time, args.SkipProfiles, args.SkipAccounts, args.RootOnly, args.Accounts, args.Regions)
	AccountNum = len(set([x['AccountId'] for x in Credentials]))
	RegionNum = len(set([x['Region'] for x in Credentials]))
	print(f"Searching {AccountNum} accounts across {RegionNum} regions")
	print()

	# Find all RAM shares
	AllRAMShares = find_all_ram_shares(Credentials, args.pStatus, args.pType)

	if verbose:
		print(f"{ERASE_LINE}Found {len(AllRAMShares)} RAM shares across {AccountNum} accounts across {RegionNum} regions")
		print()

	if len(AllRAMShares) > 0:
		sorted_results = sorted(AllRAMShares, key=lambda x: (x['OwnerAccount'], x['ShareType'], x['Region'], x['ShareName']))
		
		print(f"Found {len(AllRAMShares)} RAM shares - writing to CSV file")
		import csv
		from datetime import datetime
		timestamp = datetime.now().strftime("%y-%m-%d--%H-%M-%S")
		
		# Use provided filename or default
		if args.Filename:
			# Insert timestamp before file extension
			if '.' in args.Filename:
				name, ext = args.Filename.rsplit('.', 1)
				filename = f"{name}-{timestamp}.{ext}"
			else:
				filename = f"{args.Filename}-{timestamp}"
		else:
			filename = f"ram_shares-{timestamp}.csv"
		
		with open(filename, 'w', newline='') as csvfile:
			fieldnames = ['MgmtAccount', 'OwnerAccount', 'ViewingAccount', 'ShareType', 'Region', 'ShareName', 'Status', 'ResourceCount', 'SharedWithCount', 'AllowExternalPrincipals', 'Resources', 'SharedWith', 'ShareArn', 'CreationTime', 'LastUpdatedTime', 'Tags']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			for row in sorted_results:
				writer.writerow(row)
		print(f"Results written to: {filename}")
	else:
		print("No RAM shares found")

	if verbose:
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print()
