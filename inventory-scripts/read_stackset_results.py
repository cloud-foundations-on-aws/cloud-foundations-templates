#!/usr/bin/env python3

from ArgumentsClass import CommonArguments
from colorama import init, Fore
import logging
import re

"""
TODO: 
This script was created to help analyze the output from other scripts and tie things together.
Eventually I have to add some visuals, and better output.  
"""

init()
__version__ = "2024.06.20"

parser = CommonArguments()
parser.verbosity()  # Allows for the verbosity to be handled.
parser.version(__version__)
parser.my_parser.add_argument(
	"--stacksets_filename", "--ssf",
	dest="StackSetsFilename",
	metavar="Stacksets results from the script",
	help="String fragment of the cloudformation stack or stackset(s) you want to check for.")
parser.my_parser.add_argument(
	"--org_filename", "--of",
	dest="OrgsFilename",
	metavar="Stacksets results from the script",
	help="String fragment of the cloudformation stack or stackset(s) you want to check for.")
args = parser.my_parser.parse_args()

pStackSetsFilename = args.StackSetsFilename
pOrgsFilename = args.OrgsFilename
verbose = args.loglevel
# Setup logging levels
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

##########################
ERASE_LINE = '\x1b[2K'
# AccountList = [account['AccountId'] for account in ChildAccounts]

StackSets = {}
with open(pStackSetsFilename, 'r') as StackSets_infile:
	for line in StackSets_infile:
		line = line.strip('\n')
		# print(f"Beginning--{line}--End")
		if re.match('^[A-Za-z]', line) and line.find('MANAGED):$'):
			stackset_name = line.split(' ', 1)[0]
			StackSets[stackset_name] = {}
		elif re.search('CURRENT|OUTDATED|INOPERABLE', line):
			Status = line.split(':', 1)[0].strip()
			StackSets[stackset_name][Status] = []
		elif re.search('[0-9]{12}', line):
			acctid, regions = line.split(':')
			acctid = acctid.strip()
			region_list = regions.replace('[', '').replace(']', '').replace('\'', '').replace(' ','').split(',')
			StackSets[stackset_name][Status].append({'AccountId': acctid.lstrip(), 'Regions': region_list})

OrgAccounts = []
with open(pOrgsFilename, 'r') as Orgs_infile:
	for line in Orgs_infile:
		if not re.match('^\t\t[0-9]{12}', line):
			continue
		acct_number = line.split()[0]
		Status = line.split()[1]
		Email = line.split()[2]
		OrgAccounts.append({'AcctId': acct_number,
		                    'Status': Status,
		                    'Email' : Email})

AccountList = [x['AcctId'] for x in OrgAccounts]
StacksToCleanUp = []
StackInstancesToCheckOn = []
RegionHistogram = {}
AccountHistogram = {}
for stackset_name, stackset_data in StackSets.items():
	logging.debug(f"stackset_name: {stackset_name} | stackset_data: {stackset_data}")
	for status, instances in stackset_data.items():
		logging.debug(f"status: {status} | instances: {instances}")
		for i in range(len(instances)):
			logging.debug(f"AccountId: {StackSets[stackset_name][status][i]['AccountId']}")
			if StackSets[stackset_name][status][i]['AccountId'] not in AccountHistogram.keys():
				AccountHistogram[StackSets[stackset_name][status][i]['AccountId']] = {}
			for region in StackSets[stackset_name][status][i]['Regions']:
				if region not in RegionHistogram.keys():
					RegionHistogram[region] = {}
				if region not in AccountHistogram[StackSets[stackset_name][status][i]['AccountId']].keys():
					AccountHistogram[StackSets[stackset_name][status][i]['AccountId']][region] = list()
				if StackSets[stackset_name][status][i]['AccountId'] not in RegionHistogram[region].keys():
					RegionHistogram[region][StackSets[stackset_name][status][i]['AccountId']] = list()
				RegionHistogram[region][StackSets[stackset_name][status][i]['AccountId']].append(stackset_name)
				AccountHistogram[StackSets[stackset_name][status][i]['AccountId']][region].append(stackset_name)
			if StackSets[stackset_name][status][i]['AccountId'] in AccountList:
				StackSets[stackset_name][status][i]['Status'] = 'ACTIVE'
				if not status == 'CURRENT':
					StackInstancesToCheckOn.append({'StackSetName': stackset_name,
					                                'Status'      : status,
					                                'Account'     : StackSets[stackset_name][status][i]['AccountId'],
					                                'Regions'     : StackSets[stackset_name][status][i]['Regions']})
			else:
				StackSets[stackset_name][status][i]['Status'] = 'MISSING'
				StacksToCleanUp.append({'StackSetName': stackset_name,
				                        'Account'     : StackSets[stackset_name][status][i]['AccountId']})

Missing_Stuff = {}
for stackset_name, stackset_data in StackSets.items():
	for status, stack_instances in stackset_data.items():
		if status == 'CURRENT':
			account_list = [x['AccountId'] for x in stack_instances] if len(stack_instances) > 1 else []
			Missing_Stuff[stackset_name] = list(set(AccountList) - set(account_list))

print()
print("Thanks for using this script...")
print()
