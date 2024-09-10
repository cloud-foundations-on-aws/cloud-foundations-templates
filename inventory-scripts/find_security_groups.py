#!/usr/bin/env python3
import sys
from os.path import split
from Inventory_Modules import display_results, get_all_credentials, find_security_groups2, find_references_to_security_groups2
from ArgumentsClass import CommonArguments
from colorama import init, Fore
from botocore.exceptions import ClientError
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import time

import logging

init()
__version__ = '2024.08.24'
ERASE_LINE = '\x1b[2K'
begin_time = time()


##################
# Functions
##################
def parse_args(f_arguments):
	"""
	Description: Parses the arguments passed into the script
	@param f_arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.fragment()
	parser.rootOnly()
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--default",
		dest="pDefault",
		action="store_true",
		help="flag to determines if you're only looking for default security groups")
	local.add_argument(
		"--references",
		dest="pReferences",
		action="store_true",
		help="flag to further get references to the security groups found")
	local.add_argument(
		"--noempty",
		dest="pNoEmpty",
		action="store_true",
		help="flag to remove empty Security Groups (no references) before display")
	local.add_argument(
		"--rules",
		dest="pRules",
		action="store_true",
		help="flag to further break out the rules within the security groups found")
	return parser.my_parser.parse_args(f_arguments)


def check_accounts_for_security_groups(fCredentialList, fFragment: list = None, fExact: bool = False, fDefault: bool = False, fReferences: bool = False, fRules: bool = False):
	"""
	Note that this function takes a list of Credentials and checks for Default Security Groups in every account and region it has creds for
	:param fCredentialList: This is a list of dictionaries containing the credentials for each account
	:param fFragment: This is an optional parameter that specifies a string that must be present in the name of a security group for it to be considered
	:param fExact: This is an optional parameter that specifies whether the string specified in fFragment must be present exactly
	:param fDefault: This is an optional parameter that specifies whether to only consider default security groups or not
	:param fReferences: This is an optional parameter that specifies whether to find references to security groups or not
	:param fRules: This is an optional parameter that specifies whether to break out the rules within the security groups or not
	:return: Returns a list of dictionaries containing the security groups and their associated resources
	"""

	class FindSecurityGroups(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials, c_fragments, c_exact, c_default = self.queue.get()
				logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
				try:
					# TODO:
					#   If I wanted to find the arns of the resources that belonged to the security groups,
					#   I'd have to get a listing of all the resources that could possibly have a security group attached
					#   and then use that list to reverse-match the enis we find to the enis attached to the resources,
					#   so I could figure out which resources were being represented by the enis.
					#   This seems like a lot of work, although I understand why it would be useful
					#   It's possible we could start with just EC2 instances, and eventually widen the scope
					# Now go through each credential (account / region), and find all default security groups
					SecurityGroups = find_security_groups2(c_account_credentials, c_fragments, c_exact, c_default)
					"""
					instances = aws_acct.session.client('ec2').describe_instances()
					for sg in SecurityGroups:
						for instance in instances['Reservations']:
							for inst in instance['Instances']:
								for secgrp in inst['SecurityGroups']: 
									if sg['GroupName'] in secgrp['GroupName']:
										print(inst['InstanceId'], inst['PrivateIpAddress'], inst['State']['Name'], inst['PrivateDnsName'], sg['GroupName'], sg['Description'])
					"""
					logging.info(f"Account: {c_account_credentials['AccountId']} | Region: {c_account_credentials['Region']} | Found {len(SecurityGroups)} groups")
					# Checking whether the list is empty or not
					if SecurityGroups:
						for security_group in SecurityGroups:
							if fReferences:
								ResourcesReferencingSG = find_references_to_security_groups2(c_account_credentials, security_group)
							if fRules:
								for inbound_permission in security_group['IpPermissions']:
									inbound_permission['Protocol'] = 'AllTraffic' if inbound_permission['IpProtocol'] == '-1' else inbound_permission['IpProtocol']
									if AnySource in inbound_permission['IpRanges']:
										inbound_permission['From'] = 'Any'
									elif inbound_permission['IpRanges']:
										inbound_permission['From'] = inbound_permission['IpRanges']
									elif inbound_permission['UserIdGroupPairs']:
										inbound_permission['From'] = inbound_permission['UserIdGroupPairs']
										if inbound_permission['From'][0]['GroupId'] == security_group['GroupId']:
											inbound_permission['From'] = 'Myself'
									elif inbound_permission['PrefixListIds']:
										inbound_permission['From'] = inbound_permission['PrefixListIds']
									else:
										inbound_permission['From'] = None
								for outbound_permission in security_group['IpPermissionsEgress']:
									outbound_permission['Protocol'] = 'AllTraffic' if outbound_permission['IpProtocol'] == '-1' else outbound_permission['IpProtocol']
									if AnyDest in outbound_permission['IpRanges']:
										outbound_permission['To'] = 'Any'
									elif outbound_permission['IpRanges']:
										outbound_permission['To'] = outbound_permission['IpRanges']
									elif outbound_permission['UserIdGroupPairs']:
										outbound_permission['To'] = outbound_permission['UserIdGroupPairs']
									elif outbound_permission['PrefixListIds']:
										outbound_permission['To'] = outbound_permission['PrefixListIds']
									else:
										outbound_permission['To'] = None
							AllSecurityGroups.append({'MgmtAccount'        : c_account_credentials['MgmtAccount'],
							                          'AccountId'          : c_account_credentials['AccountId'],
							                          'Region'             : c_account_credentials['Region'],
							                          'Profile'            : c_account_credentials['Profile'] if c_account_credentials['Profile'] is not None else 'default',
							                          'GroupName'          : security_group['GroupName'],
							                          'VpcId'              : security_group['VpcId'],
							                          'GroupId'            : security_group['GroupId'],
							                          'OwnerId'            : security_group['OwnerId'],
							                          'Description'        : security_group['Description'],
							                          'Default'            : security_group['Default'],
							                          'IpPermissions'      : security_group['IpPermissions'],
							                          'IpPermissionsEgress': security_group['IpPermissionsEgress'],
							                          'Tags'               : security_group['Tags'] if 'Tags' in security_group.keys() else None,
							                          'ReferencedResources': ResourcesReferencingSG if fReferences else None,
							                          'NumOfReferences'    : len(ResourcesReferencingSG) if fReferences else 'N/A',
							                          'NumOfRules'         : (len(security_group['IpPermissions']) + len(security_group['IpPermissionsEgress'])) if fRules else 'N/A'})
					else:
						continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong")
					logging.warning(my_Error)
					continue
				except ClientError as my_Error:
					if 'AuthFailure' in str(my_Error):
						logging.error(f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region")
						logging.warning(f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into")
						continue
					else:
						logging.error(f"Error: Likely throttling errors from too much activity")
						logging.warning(my_Error)
						continue
				finally:
					pbar.update()
					self.queue.task_done()

	###########
	AnyDest = {'CidrIp': '0.0.0.0/0'}
	AnySource = {'CidrIp': '0.0.0.0/0'}

	checkqueue = Queue()

	AllSecurityGroups = []
	WorkerThreads = min(len(fCredentialList), 10)

	pbar = tqdm(desc=f'Finding security groups from {len(fCredentialList)} accounts / regions',
	            total=len(fCredentialList), unit=' locations'
	            )

	for x in range(WorkerThreads):
		worker = FindSecurityGroups(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in fCredentialList:
		logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
		try:
			# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
			checkqueue.put((credential, fFragment, fExact, fDefault))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllSecurityGroups


# Find all security groups (Done)
# Determine whether these Security Groups are in use (Done)
# For each security group, find if any rules mention the security group found (either ENI or in other Security Groups) (Done)
# TODO:
#  To find the arn of the resource using that security group, instead of just the ENI.
#  To fix the use of a default security group:
#   For each security group, find if any rules mention the security group found
#   Once all the rules are found, create a new security group - cloning those rules
#   Find all the ENIs (not just EC2 instances) that might use that security group
#   Determine if there's a way to update those resources to use the new security group
#   Present what we've found, and ask the user if they want to update those resources to use the new security group created

def save_data_to_file(f_AllSecurityGroups: list, f_Filename: str, f_References: bool = False, f_Rules: bool = False, f_NoEmpty: bool = False) -> str:
	"""
	Description: Saves the data to a file
	@param f_AllSecurityGroups: The security groups and associated data that were found
	@param f_Filename: The file to save the data to
	@param f_References: Whether to include the references to the security groups or not
	@param f_Rules: Whether to include the rules within the security groups or not
	@param f_NoEmpty: Whether to include non-referenced security groups or not
	@return: The filename that was saved
	"""
	# Save the header to the file
	Heading = f"AccountId|Region|SG Group Name|SG Group ID|VPC ID|Default(T/F)|Description"
	reference_Heading = f"|Resource Type|Resource ID|Resource Status|Attachment ID|Instance Name Tag|IP Address|Description"
	rules_Heading = f"|InboundRule|Port From|Port To|From"
	if f_References:
		Heading += reference_Heading
	if f_Rules:
		Heading += rules_Heading
	# Save the data to a file
	with open(f_Filename, 'w') as f:
		f.write(Heading + '\n')
		for sg in f_AllSecurityGroups:
			sg_line = f"{sg['AccountId']}|{sg['Region']}|{sg['GroupName']}|{sg['GroupId']}|{sg['VpcId']}|{sg['Default']}|{sg['Description']}"
			if pReferences:
				if sg['NumOfReferences'] == 0 and f_NoEmpty:
					# This means that the SG had no references, and the "NoEmpty" means we don't want non-referenced SGs, so it skips ahead
					continue
				elif sg['NumOfReferences'] == 0:
					sg_line_with_references = sg_line + f"{'|None' * 7}"
				# f.write(sg_line)
				elif sg['NumOfReferences'] > 0:
					for reference in sg['ReferencedResources']:
						reference_line = f"|{reference['ResourceType']}|{reference['Id']}|{reference['Status']}|{reference['AttachmentId']}|{reference['InstanceNameTag']}|{reference['IpAddress']}|{reference['Description']}"
						sg_line_with_references = sg_line + reference_line
					# f.write(sg_line + reference_line)
			if pRules:
				if sg['NumOfRules'] == 0:
					sg_line_with_rules = sg_line + f"{'|None' * 4}\n"
				# f.write(sg_line)
				else:
					for inbound_permission in sg['IpPermissions']:
						inbound_permission_line = f"|{inbound_permission['Protocol']}|{inbound_permission['FromPort']}|{inbound_permission['ToPort']}|{inbound_permission['From']}"
						row = sg_line + inbound_permission_line + '\n'
						f.write(row)
					for outbound_permission in sg['IpPermissionsEgress']:
						outbound_permission_line = f"|{outbound_permission['Protocol']}|{outbound_permission['FromPort']}|{outbound_permission['ToPort']}|{outbound_permission['To']}"
						row = sg_line + outbound_permission_line + '\n'
						f.write(row)
			elif not pReferences:
				row = sg_line + '\n'
				f.write(row)
			elif pReferences:
				row = sg_line_with_references + '\n'
				f.write(row)
	logging.info(f"Data saved to {f_Filename}")
	return f_Filename


def find_resource_using_eni(f_eni: str, f_sg: dict, f_AllSecurityGroups: list) -> dict:
	"""
	Description: Finds the resource using the ENI
	@param f_eni: The ENI to find the resource for
	@param f_sg: The security group to find the resource for
	@param f_AllSecurityGroups: The list of all security groups and associated data
	@return: The resource using the ENI
	"""
	for resource in f_AllSecurityGroups:
		if resource['GroupId'] == f_sg['GroupId']:
			for eni in resource['NetworkInterfaces']:
				if eni['NetworkInterfaceId'] == f_eni:
					return resource
	return None


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
	pFragment = args.Fragments
	pExact = args.Exact
	pDefault = args.pDefault
	pReferences = args.pReferences
	pRules = args.pRules
	pNoEmpty = args.pNoEmpty
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	print()
	print(f"Checking for Security Groups... ")
	print()

	logging.info(f"Profiles: {pProfiles}")

	display_dict = {
		'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
		'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
		'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
		'GroupName'  : {'DisplayOrder': 4, 'Heading': 'Group Name'},
		'GroupId'    : {'DisplayOrder': 5, 'Heading': 'Group ID'},
		'VpcId'      : {'DisplayOrder': 6, 'Heading': 'VPC ID'},
		'Default'    : {'DisplayOrder': 7, 'Heading': 'Default', 'Condition': [True]},
		'Description': {'DisplayOrder': 10, 'Heading': 'Description'}}
	display_dict.update({'NumOfReferences'    : {'DisplayOrder': 8, 'Heading': '# Refs'},
	                     'ReferencedResources': {'DisplayOrder': 11, 'Heading': 'References',
	                                             'SubDisplay'  : {'ResourceType'   : {'DisplayOrder': 1, 'Heading': 'Resource Type'},
	                                                              'Id'             : {'DisplayOrder': 2, 'Heading': 'ID'},
	                                                              'Status'         : {'DisplayOrder': 3, 'Heading': 'Status'},
	                                                              'AttachmentId'   : {'DisplayOrder': 4, 'Heading': 'Instance Id'},
	                                                              'InstanceNameTag': {'DisplayOrder': 5, 'Heading': 'Name'},
	                                                              'IpAddress'      : {'DisplayOrder': 6, 'Heading': 'Private IP'},
	                                                              'Description'    : {'DisplayOrder': 7, 'Heading': 'Description'}}}}) if pReferences else None
	# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_security_groups.html
	display_dict.update({'NumOfRules'         : {'DisplayOrder': 9, 'Heading': '# Rules'},
	                     'IpPermissions'      : {'DisplayOrder': 12, 'Heading': 'Inbound Rules',
	                                             'SubDisplay'  : {'Protocol': {'DisplayOrder': 1, 'Heading': 'In Protocol'},
	                                                              'FromPort': {'DisplayOrder': 2, 'Heading': 'Port From', 'Delimiter': False},
	                                                              'ToPort'  : {'DisplayOrder': 3, 'Heading': 'Port To', 'Delimiter': False},
	                                                              'From'    : {'DisplayOrder': 4, 'Heading': 'From', 'Condition': ['10.1.1.0/24']},
	                                                              # 'UserIdGroupPairs': {'DisplayOrder': 5, 'Heading': 'Group Pairs'},
	                                                              # 'Description'     : {'DisplayOrder': 6, 'Heading': 'Description'}
	                                                              }},
	                     'IpPermissionsEgress': {'DisplayOrder': 13, 'Heading': 'Outbound Rules',
	                                             'SubDisplay'  : {'Protocol': {'DisplayOrder': 1, 'Heading': 'Out Protocol'},
	                                                              'FromPort': {'DisplayOrder': 2, 'Heading': 'Port From', 'Delimiter': False},
	                                                              'ToPort'  : {'DisplayOrder': 3, 'Heading': 'Port To', 'Delimiter': False},
	                                                              'To'      : {'DisplayOrder': 4, 'Heading': 'To'},
	                                                              # 'UserIdGroupPairs': {'DisplayOrder': 5, 'Heading': 'Group Pairs'},
	                                                              # 'Description'     : {'DisplayOrder': 6, 'Heading': 'Description'}
	                                                              }}}) if pRules else None

	# Get credentials for all relevant children accounts

	CredentialList = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList)
	AccountList = list(set([x['AccountId'] for x in CredentialList if x['Success']]))
	RegionList = list(set([x['Region'] for x in CredentialList if x['Success']]))
	# Find Security Groups across all children accounts
	# This same function also does the references check, if you want it to...
	AllSecurityGroups = check_accounts_for_security_groups(CredentialList, pFragment, pExact, pDefault, pReferences, pRules)
	sorted_AllSecurityGroups = sorted(AllSecurityGroups, key=lambda k: (k['MgmtAccount'], k['AccountId'], k['Region'], k['GroupName']))

	# Display results
	display_results(sorted_AllSecurityGroups, display_dict, None)

	if pFilename:
		saved_filename = save_data_to_file(sorted_AllSecurityGroups, pFilename, pReferences, pRules, pNoEmpty)
		print(f"Data has been saved to {saved_filename}")
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

	print(f"We found {len(AllSecurityGroups)} {'default ' if pDefault else ''}security group{'' if len(AllSecurityGroups) == 1 else 's'} across {len(AccountList)} accounts and {len(RegionList)} regions")
	print()
	print("Thank you for using this script")
	print()
