#!/usr/bin/env python3
import sys
import os

from Inventory_Modules import display_results, get_all_credentials, find_account_enis2
from ArgumentsClass import CommonArguments
# from datetime import datetime
from colorama import init, Fore
from botocore.exceptions import ClientError
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import time

import logging

init()

__version__ = '2025.09.26'


##################
# Functions
##################


def parse_args(f_args):
	"""
	Description: Parses the arguments passed into the script
	@param f_args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	parser = CommonArguments()
	script_path, script_name = os.path.split(sys.argv[0])
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
		"--ipaddress", "--ip",
		dest="pipaddresses",
		nargs="*",
		metavar="IP address",
		default=None,
		help="IP address(es) you're looking for within your accounts")
	local.add_argument(
		"--fqdn", "--name",
		dest="pDNSNames",
		nargs="*",
		metavar="Fully Qualified Domain Name",
		default=None,
		help="DNS Name(s) you're looking to find within your accounts")
	local.add_argument(
		"--public-only", "--po",
		action="store_true",
		dest="ppublic",
		help="Whether you want to return only those results with a Public IP")
	return parser.my_parser.parse_args(f_args)


def check_accounts_for_enis(fCredentialList, fips: list = None, fPublicOnly: bool = False):
	"""
	@Description: Note that this function takes a list of Credentials and checks for ENIs in every account and region it has creds for
	@param fCredentialList: The list of credentials to check
	@param fips: The IP address to look for
	@param fPublicOnly: Whether to look for only public IPs
	@return: LIst of ENIs from the list of credentials
	"""

	class FindENIs(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_region, c_fips = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					account_enis = find_account_enis2(c_account_credentials, c_region, c_fips)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']} in region {c_region}")
					for eni in account_enis:
						eni['MgmtAccount'] = c_account_credentials['MgmtAccount']
						if fPublicOnly and eni['PublicIp'] == "No Public IP":
							pass
						else:
							Results.append(eni)
				# Results.extend(account_enis)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					# print(f"{ERASE_LINE}Finished finding ENIs in account {c_account_credentials['AccountId']} in region {c_region} - {c_PlaceCount} / {c_PlacesToLook}", end='\r')
					pbar.update()
					self.queue.task_done()

	checkqueue = Queue()

	pbar = tqdm(desc=f'Finding enis from {len(CredentialList)} accounts / regions',
	            total=len(fCredentialList), unit=' locations'
	            )

	Results = []
	WorkerThreads = min(len(fCredentialList), 50)

	for x in range(WorkerThreads):
		worker = FindENIs(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in fCredentialList:
		logging.info(f"Connecting to account {credential['AccountId']} in region {credential['Region']}")
		try:
			# print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
			checkqueue.put((credential, credential['Region'], fips))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return Results


def resolve_names_to_ips(f_fqdns: list = None):
	"""
	@Description: Resolves names to IPs before we begin to search
	@f_fqdns: A list of names that need to be resolved to external IP addresses, to search on
	@return: A list - containing the IP addresses for the names passed in
	"""
	import socket

	# Resolve FQDNs to IP addresses using DNS lookup
	resolved_ips = []
	for fqdn in f_fqdns:
		try:
			# Get all IP addresses for the FQDN
			result = socket.getaddrinfo(fqdn, None)
			# Extract unique IP addresses from the result
			ips = {'fqdn': fqdn, 'IPs': list(set([addr[4][0] for addr in result]))}
			resolved_ips.append(ips)
			logging.info(f"Resolved {fqdn} to IPs: {ips}")
		except socket.gaierror as e:
			logging.warning(f"Failed to resolve {fqdn}: {e}")

	# Remove duplicates
	# logging.info(f"Resolved IP list to search for: {ips}")
	return resolved_ips


def present_results(f_ENIsFound: list):
	"""
	Description: Presents results at the end of the script
	@param f_ENIsFound: The list of records to show...
	"""
	display_dict = {'MgmtAccount'     : {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'       : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'          : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'PrivateDnsName'  : {'DisplayOrder': 4, 'Heading': 'ENI Name'},
	                'Status'          : {'DisplayOrder': 5, 'Heading': 'Status', 'Condition': ['available', 'attaching', 'detaching']},
	                'PublicIp'        : {'DisplayOrder': 6, 'Heading': 'Public IP Address'},
	                'ENIId'           : {'DisplayOrder': 7, 'Heading': 'ENI Id'},
	                'PrivateIpAddress': {'DisplayOrder': 8, 'Heading': 'Assoc. IP'}}

	sorted_ENIs_Found = sorted(f_ENIsFound, key=lambda d: (d['MgmtAccount'], d['AccountId'], d['Region'], d['ENIId']))
	display_results(sorted_ENIs_Found, display_dict, 'None', pFilename)

	DetachedENIs = [x for x in sorted_ENIs_Found if x['Status'] in ['available', 'attaching', 'detaching']]
	RegionList = list(set([x['Region'] for x in sorted_ENIs_Found]))
	AccountList = list(set([x['AccountId'] for x in sorted_ENIs_Found]))

	print() if pSkipAccounts is not None or pSkipProfiles is not None else ""
	print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
	print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
	print()
	print(f"The output has also been written to a file beginning with '{pFilename}' + the date and time") if pFilename is not None else ""
	print(f"Found {len(f_ENIsFound)} ENIs{' with public IPs' if pPublicOnly else ''} across {len(AccountList)} accounts across {len(RegionList)} regions")
	print(f"{Fore.RED}Found {len(DetachedENIs)} ENIs that are not listed as 'in-use' and may therefore be costing you additional money while they're unused.{Fore.RESET}") if DetachedENIs else ""
	print()
	if verbose < 40:
		for x in DetachedENIs:
			print(x)


##################
# Main
##################

ERASE_LINE = '\x1b[2K'

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pAccounts = args.Accounts
	pRootOnly = args.RootOnly
	pIPaddressList = args.pipaddresses
	pDNSNames = args.pDNSNames
	pPublicOnly = args.ppublic
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	begin_time = time()
	print()
	print(f"Checking for Elastic Network Interfaces... ")
	print()

	logging.info(f"Profiles: {pProfiles}")

	# Get credentials for all relevant children accounts
	logging.debug(f"pProfiles: {pProfiles}")
	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)

	# Add into the IP list, any IPs that come from the names of the fqdns passed in
	if pDNSNames is not None:
		fqdn_resolutions = resolve_names_to_ips(pDNSNames)
		fqdn_ips = [ip for x in fqdn_resolutions for ip in x['IPs']]
	if pIPaddressList is None and pDNSNames is not None:
		pIPaddressList = fqdn_ips
	elif pIPaddressList is not None and pDNSNames is not None:
		pIPaddressList.extend(fqdn_ips)

	# Find ENIs across all children accounts
	ENIsFound = check_accounts_for_enis(CredentialList, pIPaddressList, pPublicOnly)
	# Display results
	present_results(ENIsFound)

	if verbose < 50:
		print(f"You asked me to resolve {len(pDNSNames)} DNS Names")
		for fqdn in fqdn_resolutions:
			print(f"    DNS Name: {Fore.RED}{fqdn['fqdn']}{Fore.RESET} resolved to {Fore.RED}{fqdn['IPs']}{Fore.RESET}")

	if pTiming:
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thank you for using this script")
print()
