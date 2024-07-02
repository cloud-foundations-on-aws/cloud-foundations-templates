#!/usr/bin/env python3

import logging
import sys
import platform
from os.path import split
from time import time, sleep
from datetime import datetime, timedelta
from typing import Any, List

import Inventory_Modules
from Inventory_Modules import get_all_credentials, get_regions3, RemoveCoreAccounts, display_results
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
from colorama import init, Fore
from botocore.exceptions import ClientError
import boto3
from botocore.config import Config

init()
__version__ = "2024.03.10"
ERASE_LINE = '\x1b[2K'
begin_time = time()
sleep_interval = 5


#####################
# Functions
#####################

def parse_args(args):
	"""
	Description: Parses the arguments passed into the script
	@param args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleprofile()
	parser.multiregion()
	parser.roletouse()
	parser.rootOnly()
	parser.save_to_file()
	parser.extendedargs()
	parser.timing()
	parser.verbosity()  # Allows for the verbosity to be handled.
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--start",
		dest="pStartDate",
		metavar="Start Date",
		type=str,
		default=None,
		help="Start date for the search. Format: YYYY-MM-DD. Note you need to pad the month and day if single digit. Default will be 5 days ago.")
	local.add_argument(
		"--end",
		dest="pEndDate",
		metavar="End Date",
		type=str,
		default=None,
		help="End date for the search. Format: YYYY-MM-DD. Note you need to pad the month and date if single digit.\n Default is YESTERDAY at 23:59:59, in order to give full days.")
	return parser.my_parser.parse_args(args)


def setup_auth_accounts_and_regions(fProfile: str) -> (aws_acct_access, list, list):
	"""
	Description: This function takes in a profile, and returns the account object and the regions valid for this account / org.
	@param fProfile: A string representing the profile provided by the user. If nothing, then use the default profile or credentials
	@return:
		- an object of the type "aws_acct_access"
		- a list of regions valid for this particular profile/ account.
	"""
	try:
		aws_acct = aws_acct_access(fProfile)
	except ConnectionError as my_Error:
		logging.error(f"Exiting due to error: {my_Error}")
		sys.exit(8)

	ChildAccounts = aws_acct.ChildAccounts
	RegionList = get_regions3(aws_acct, pRegionList)

	ChildAccounts = RemoveCoreAccounts(ChildAccounts, pSkipAccounts)
	if pAccountList is None:
		AccountList = [account['AccountId'] for account in ChildAccounts]
	elif pAccessRole is not None:
		AccountList = pAccountList
	else:
		AccountList = [account['AccountId'] for account in ChildAccounts if account['AccountId'] in pAccountList]

	print(f"You asked to sum flow log data")
	print(f"\tin these accounts: {Fore.RED}{AccountList}{Fore.RESET}")
	print(f"\tin these regions: {Fore.RED}{RegionList}{Fore.RESET}")
	print(f"\tFrom: {pStartDate} until {pEndDate}")
	if pSkipAccounts is not None:
		print(f"\tWhile skipping these accounts: {Fore.RED}{pSkipAccounts}{Fore.RESET}")

	return aws_acct, AccountList, RegionList


def check_account_access(faws_acct, faccount_num, fAccessRole=None):
	if fAccessRole is None:
		logging.error(f"Role must be provided")
		return_response = {'Success': False, 'ErrorMessage': "Role wasn't provided"}
		return return_response
	sts_client = faws_acct.session.client('sts')
	try:
		role_arn = f"arn:aws:iam::{faccount_num}:role/{fAccessRole}"
		credentials = sts_client.assume_role(RoleArn=role_arn,
		                                     RoleSessionName='TheOtherGuy')['Credentials']
		return_response = {'AccountNumber': faccount_num, 'Credentials': credentials, 'Success': True, 'ErrorMessage': ""}
		return return_response
	except ClientError as my_Error:
		print(f"Client Error: {my_Error}")
		return_response = {'Success': False, 'ErrorMessage': "Client Error"}
		return return_response
	except sts_client.exceptions.MalformedPolicyDocumentException as my_Error:
		print(f"MalformedPolicy: {my_Error}")
		return_response = {'Success': False, 'ErrorMessage': "Malformed Policy"}
		return return_response
	except sts_client.exceptions.PackedPolicyTooLargeException as my_Error:
		print(f"Policy is too large: {my_Error}")
		return_response = {'Success': False, 'ErrorMessage': "Policy is too large"}
		return return_response
	except sts_client.exceptions.RegionDisabledException as my_Error:
		print(f"Region is disabled: {my_Error}")
		return_response = {'Success': False, 'ErrorMessage': "Region Disabled"}
		return return_response
	except sts_client.exceptions.ExpiredTokenException as my_Error:
		print(f"Expired Token: {my_Error}")
		return_response = {'Success': False, 'ErrorMessage': "Expired Token"}
		return return_response


def get_flow_log_cloudwatch_groups(ocredentials) -> list[dict]:
	"""
	Description: Gets the flow logs for the VPCs in this account and this region
	@param ocredentials:
	@return:
	"""

	session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_ec2 = session_ec2.client('ec2', config=my_config)
	# client_logs = session_ec2.client('logs', config=my_config)
	try:
		response = client_ec2.describe_flow_logs()
		CW_LogGroups = [{'Credentials' : ocredentials,
		                 'AccountId'   : ocredentials['AccountId'],
		                 'Region'      : ocredentials['Region'],
		                 'VPCId'       : x['ResourceId'],
		                 'LogGroupName': x['LogGroupName']} for x in response['FlowLogs'] if 'LogGroupName' in x.keys() and x['ResourceId'].find('vpc-') == 0]
	except Exception as my_Error:
		raise my_Error
	return CW_LogGroups


def prep_cloudwatch_log_query(f_flow_logs: list) -> list[dict]:
	"""
	Description: Prepares the query to get the outbound VPC data
	@param f_flow_logs: 
	@return: 
	"""""
	import ipaddress

	vpc_cidr_blocks = list()
	for flow_log in f_flow_logs:
		session_ec2 = boto3.Session(aws_access_key_id=flow_log['Credentials']['AccessKeyId'],
		                            aws_secret_access_key=flow_log['Credentials']['SecretAccessKey'],
		                            aws_session_token=flow_log['Credentials']['SessionToken'],
		                            region_name=flow_log['Credentials']['Region'])
		client_ec2 = session_ec2.client('ec2', config=my_config)
		VPCs = client_ec2.describe_vpcs()['Vpcs']
		for vpc in VPCs:
			if vpc['VpcId'] == flow_log['VPCId']:
				tag_dict = {x['Key']: x['Value'] for x in vpc['Tags']} if 'Tags' in vpc.keys() else {}
				if 'Name' in tag_dict.keys():
					vpc_name = tag_dict['Name']
				else:
					vpc_name = None
				for cidr_block in vpc['CidrBlockAssociationSet']:
					new_record = flow_log
					# Debugging statement below
					# cidr_block.update({'CidrBlock': '172.16.64.0/22'})
					cidr_net_name = ipaddress.ip_network(cidr_block['CidrBlock'])
					first_dot = cidr_block['CidrBlock'].find('.')
					first_octet = cidr_block['CidrBlock'][:first_dot]
					second_dot = cidr_block['CidrBlock'].find('.', first_dot + 1)
					second_octet = cidr_block['CidrBlock'][first_dot + 1:second_dot]
					third_dot = cidr_block['CidrBlock'].find('.', second_dot + 1)
					third_octet = cidr_block['CidrBlock'][second_dot + 1:third_dot]
					fourth_octet = cidr_block['CidrBlock'].find('.', third_dot + 1)
					if cidr_net_name.prefixlen == 8:
						network_name = f"{first_octet}"
						query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and srcAddr like '{network_name}' and dstAddr not like '{network_name}' | sort @timestamp desc | stats sum(bytes)"
					elif cidr_net_name.prefixlen > 8 and cidr_net_name.prefixlen < 16:
						# Create a list that includes all possible values for the second octet, based on the second octet of the CIDR, plus the possible values from the netmask
						# Somewhere the mat will have to be that the variable octet = the original octet + all numbers up to the original number * 2^(prefixlen%8)
						# So for instance for a prefix length of 12 (172.16-172.31), it would be 172.16+0, 172.16+1, 172.16+2, 172.16+3, 172.16+4, 172.16+5, 172.16+6, 172.16+7, 172.16+8, 172.16+9, 172.16+10, 172.16+11, 172.16+12, 172.16+13, 172.16+14, 172.16+15
						and_string = ' and '
						or_string = ' or '
						dst_query_seq = [f"dstAddr not like '{first_octet}.{int(second_octet) + x}'" for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))]
						src_query_seq = [f"srcAddr like '{first_octet}.{int(second_octet) + x}'" for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))]
						dst_string = and_string.join(dst_query_seq)
						src_string = or_string.join(src_query_seq)
						filter_query = f"{src_string} and {dst_string}"
						query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and {filter_query} | sort @timestamp desc | stats sum(bytes)"
					elif cidr_net_name.prefixlen == 16:
						network_name = f"{first_octet}.{second_octet}"
						query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and srcAddr like '{network_name}' and dstAddr not like '{network_name}' | sort @timestamp desc | stats sum(bytes)"
					elif cidr_net_name.prefixlen > 16 and cidr_net_name.prefixlen < 24:
						and_string = ' and '
						or_string = ' or '
						dst_query_seq = [f"dstAddr not like '{first_octet}.{second_octet}.{int(third_octet) + x}'" for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))]
						src_query_seq = [f"srcAddr like '{first_octet}.{second_octet}.{int(third_octet) + x}'" for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))]
						dst_string = and_string.join(dst_query_seq)
						src_string = or_string.join(src_query_seq)
						filter_query = f"{src_string} and {dst_string}"
						query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and {filter_query} | sort @timestamp desc | stats sum(bytes)"
					elif cidr_net_name.prefixlen == 24:
						network_name = f"{first_octet}.{second_octet}.{third_octet}"
						query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and srcAddr like '{network_name}' and dstAddr not like '{network_name}' | sort @timestamp desc | stats sum(bytes)"
					elif cidr_net_name.prefixlen > 24 and cidr_net_name.prefixlen <= 28:
						and_string = ' and '
						or_string = ' or '
						dst_query_seq = [f"dstAddr not like '{first_octet}.{second_octet}.{third_octet}.{int(fourth_octet) + x}'" for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))]
						src_query_seq = [f"srcAddr like '{first_octet}.{second_octet}.{third_octet}.{int(fourth_octet) + x}'" for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))]
						dst_string = and_string.join(dst_query_seq)
						src_string = or_string.join(src_query_seq)
						filter_query = f"{src_string} and {dst_string}"
						query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and {filter_query} | sort @timestamp desc | stats sum(bytes)"
					elif cidr_net_name.prefixlen < 8 or cidr_net_name.prefixlen > 28:
						raise ValueError(f"Netmask of {cidr_net_name.prefixlen} is not supported")
					else:
						query_string = None
					new_record.update({'VPC'       : vpc['VpcId'],
					                   'VPCName'   : vpc_name if vpc_name is not None else 'No Name Available',
					                   'cidr_block': cidr_block['CidrBlock'],
					                   'Query'     : query_string})
					vpc_cidr_blocks.append(new_record.copy())
			else:
				continue
	return vpc_cidr_blocks


# def query_cloudwatch_logs(ocredentials, queries: list, f_all_cw_log_groups: list, fRegion: str = 'us-east-1') -> list:
def query_cloudwatch_logs(f_queries: list, f_start: datetime, f_end: datetime) -> list[dict]:
	"""
	Description: Prepares and runs the query to run within CloudWatch
	@param f_queries: The listing of flow logs and queries to run for each VPC found
	@param f_start: The start date for the flow log queries
	@param f_end: The end date for the flow log queries
	@return:
	"""
	from botocore.exceptions import ClientError

	all_query_ids = list()
	for query in f_queries:
		new_record = query
		session_logs = boto3.Session(aws_access_key_id=query['Credentials']['AccessKeyId'],
		                             aws_secret_access_key=query['Credentials']['SecretAccessKey'],
		                             aws_session_token=query['Credentials']['SessionToken'],
		                             region_name=query['Credentials']['Region'])
		client_logs = session_logs.client('logs', config=my_config)
		logging.debug(f"About to try to connect to describe the log groups within account {query['Credentials']['AccountId']}")
		log_group_retention = client_logs.describe_log_groups(logGroupNamePrefix=query['LogGroupName'])
		logging.debug(f"Just tried to connect to describe the log groups within account {query['Credentials']['AccountId']}")
		if log_group_retention['logGroups'][0]['retentionInDays'] < (yesterday - start_date_time).days:
			logging.warning(f"Log group {query['LogGroupName']} has a {log_group_retention['logGroups'][0]['retentionInDays']} day retention policy, so data will be constrained to that period.")
			f_start = (yesterday - timedelta(days=log_group_retention['logGroups'][0]['retentionInDays'])).replace(hour=0, minute=0, second=0, microsecond=0)
			f_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
		logging.debug(f"About to start the query for {query['LogGroupName']} with retention of {log_group_retention['logGroups'][0]['retentionInDays']} days, with start of {f_start} and end of {f_end}.")
		logging.debug(f"Query: {query['Query']}")
		try:
			query_id = client_logs.start_query(logGroupName=query['LogGroupName'],
			                                   startTime=int((f_start - epoch_time).total_seconds()),
			                                   endTime=int((f_end - epoch_time).total_seconds()),
			                                   queryString=query['Query'])
			logging.debug("Was able to run query...")
			new_record.update({'QueryId': query_id['queryId'], 'StartDate': f_start, 'EndDate': f_end, 'Days': (f_end - f_start).days})
			all_query_ids.append(query.copy())
		except ClientError as my_Error:
			logging.error(f"Received ClientError ({my_Error.operation_name} - {my_Error.response['Error']['Code']} - {my_Error.response['Error']['Message']} - {my_Error.response['Error']['Type']}) - {my_Error.response}")
			logging.error(f"Unable to run query for {query['LogGroupName']} in account {query['Credentials']['AccountId']} in region {query['Credentials']['Region']}")
			continue
		except Exception as my_Error:
			logging.error(f"Unable to run query for {query['LogGroupName']} in account {query['Credentials']['AccountId']} in region {query['Credentials']['Region']} - {my_Error}")
			continue
	return all_query_ids


def get_cw_query_results(fquery_requests: list) -> list[dict]:
	"""
	Description: Gets the results of a query from CloudWatch Logs
	@param fquery_requests:
	@return:
	"""
	all_query_results = list()
	print()
	print(f"Checking {len(fquery_requests)} flow logs that launched scanning across {SpannedDaysChecked} days. \n"
	      f"Based on how much data is in the flow logs, this could take {SpannedDaysChecked * 5} seconds for the busiest VPCs")
	print()
	for query in fquery_requests:
		new_record = query
		session_logs = boto3.Session(aws_access_key_id=query['Credentials']['AccessKeyId'],
		                             aws_secret_access_key=query['Credentials']['SecretAccessKey'],
		                             aws_session_token=query['Credentials']['SessionToken'],
		                             region_name=query['Credentials']['Region'])
		client_logs = session_logs.client('logs', config=my_config)
		# query_ready = client_logs.describe_queries(queryIds=[fquery['QueryId']])
		response = client_logs.get_query_results(queryId=query['QueryId'])
		# Check on whether query is finished...
		waited_seconds_total = 0

		while response['status'] == 'Running':
			waited_seconds_total += sleep_interval
			if waited_seconds_total > (SpannedDaysChecked * 5):
				print(f"{ERASE_LINE}Query is still running... Waited {waited_seconds_total} seconds already, we'll have to check manually later. ")
				break
			print(f"{ERASE_LINE}Query for vpc {query['VPCId']} in account {query['AccountId']} in region {query['Region']} is still running... It's been {waited_seconds_total} seconds so far", end='\r')
			sleep(sleep_interval)
			response = client_logs.get_query_results(queryId=query['QueryId'])
		if response['statistics']['recordsMatched'] > 0:
			new_record.update({'Results': response['results'][0][0]['value'], 'Status': response['status'], 'Stats': response['statistics']})
			all_query_results.append(query.copy())
		else:
			logging.info(f"The CloudWatch query for vpc {query['VPCId']} in account {query['AccountId']} in region {query['Region']} returned no results:")
			new_record.update({'Results': 0, 'Status': response['status'], 'Stats': response['statistics']})
			all_query_results.append(query.copy())
	return all_query_results


#####################
# Main
#####################

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegionList = args.Regions
	pAccessRole = args.AccessRole
	# pAccountFile = args.pAccountFile
	pSkipProfiles = args.SkipProfiles
	pSkipAccounts = args.SkipAccounts
	pRootOnly = args.RootOnly
	pAccountList = args.Accounts
	pTiming = args.Time
	verbose = args.loglevel
	pFilename = args.Filename
	pStartDate = args.pStartDate
	pEndDate = args.pEndDate
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	my_config = Config(
		signature_version='v4',
		retries={
			'max_attempts': 6,
			'mode'        : 'standard'
			}
		)

	if platform.system() == 'Linux':
		platform = 'Linux'
	elif platform.system() == 'Windows':
		platform = 'Windows'
	else:
		platform = 'Mac'

	display_dict = {'AccountId'     : {'DisplayOrder': 1, 'Heading': 'Acct Number'},
	                'Region'        : {'DisplayOrder': 2, 'Heading': 'Region'},
	                'VPCName'       : {'DisplayOrder': 3, 'Heading': 'VPC Name'},
	                'cidr_block'    : {'DisplayOrder': 4, 'Heading': 'CIDR Block'},
	                'Days'          : {'DisplayOrder': 5, 'Heading': '# of Days'},
	                'Results'       : {'DisplayOrder': 6, 'Heading': 'Raw Bytes'},
	                'OutboundGBData': {'DisplayOrder': 7, 'Heading': 'GBytes'}}

	# Validate the parameters passed in
	try:
		yesterday = datetime.today() - timedelta(days=1)
		if pStartDate is None:
			start_date_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
		else:
			start_date_time = datetime.strptime(pStartDate, '%Y-%m-%d')
			start_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
	except Exception as my_Error:
		logging.error(f"Start Date must be entered as 'YYYY-MM-DD'")
		print(f"Start Date input Error: {my_Error}")
		sys.exit(1)
	try:
		if pEndDate is None:
			end_date_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
		else:
			end_date_time = datetime.strptime(pEndDate, '%Y-%m-%d')
	except Exception as my_Error:
		logging.error(f"End Date must be entered as 'YYYY-MM-DD'")
		print(f"End Date input Error: {my_Error}")
		sys.exit(1)

	epoch_time = datetime(1970, 1, 1)

	SpannedDaysChecked = (end_date_time - start_date_time).days
	# Setup the aws_acct object
	aws_acct, AccountList, RegionList = setup_auth_accounts_and_regions(pProfile)
	# Get credentials for all Child Accounts
	if pAccessRole is None:
		pAccessRoles = pAccessRole
	else:
		pAccessRoles = [pAccessRole]
	CredentialList = get_all_credentials(pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, AccountList, RegionList, pAccessRoles)

	all_query_requests = list()
	for credential in CredentialList:
		logging.info(f"Accessing account #{credential['AccountId']} as {pAccessRole} using account {aws_acct.acct_number}'s credentials")
		# response = check_account_access(aws_acct, account_num, pAccessRole)
		if credential['Success']:
			logging.info(f"Account {credential['AccountId']} was successfully connected via role {credential.get('Role', pAccessRole)} from {aws_acct.acct_number}")
			print(f"{ERASE_LINE}Checking account {Fore.BLUE}{credential['AccountId']}{Fore.RESET} in region {Fore.BLUE}{credential['Region']}{Fore.RESET}...", end='\r')
			"""
			Put more commands here... Or you can write functions that represent your commands and call them from here.
			"""
			try:
				# Get flow log names from each account and region
				logging.debug("Getting flow_log cloudwatch groups")
				acct_flow_logs = get_flow_log_cloudwatch_groups(credential)
				# Create the queries necessary for CloudWatch to get the necessary data
				logging.debug("Preparing the queries - getting VPC info")
				queries = prep_cloudwatch_log_query(acct_flow_logs)
				# Run the queries against the CloudWatch in each account / region
				logging.debug("Running the queries with the start/end dates")
				query_ids = query_cloudwatch_logs(queries, start_date_time, end_date_time)
				logging.debug("Successfully ran queries - now adding all efforts to the final dictionary")
				all_query_requests.extend(query_ids)
			except Exception as my_Error:
				logging.debug(f"Credential: {credential}")
				print(f"Exception Error: {my_Error}")
		else:
			print(f"Failed to connect to {credential['AccountId']} from {aws_acct.acct_number} {'with Access Role ' + pAccessRole if pAccessRole is not None else ''} with error: {credential['ErrorMessage']}")

	# Using the list of queries created above, go back into each account and region and get the query results
	all_query_results = get_cw_query_results(all_query_requests)

	# Display the information we've found this far
	sorted_all_query_results = sorted(all_query_results, key=lambda k: (k['AccountId'], k['Region'], k['VPCName']))
	for query_result in all_query_results:
		query_result['OutboundGBData'] = int(query_result['Results']) / 1000000000
	display_results(sorted_all_query_results, display_dict, None, pFilename)

	print()
	print("Thanks for using this script...")
	print()
