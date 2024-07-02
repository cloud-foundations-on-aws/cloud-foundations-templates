#!/usr/bin/env python3

import sys
import Inventory_Modules
import vpc_modules
from colorama import init, Fore
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from account_class import aws_acct_access
from prettytable import PrettyTable
import logging

init()
__version__ = "2023.05.04"

parser = CommonArguments()
parser.singleprofile()
parser.verbosity()
parser.version(__version__)
parser.my_parser.add_argument(
		"--explain",
		dest="pExplain",
		const=True,
		default=False,
		action="store_const",
		help="This flag prints out the explanation of what this script would do.")
parser.my_parser.add_argument(
		"-R", "--role",
		dest="Role",
		metavar="rolename",
		default=None,
		help="This allows the provision of a role to be used to access the child account(s).")
parser.my_parser.add_argument(
		"-a", "--account",
		dest="pChildAccountId",
		metavar="New Account to be adopted into LZ",
		default=None,
		# required=True,
		help="This is the account number of the account you're checking, to see if it can be adopted into the ALZ. By default, we will check every account in the Organization")
parser.my_parser.add_argument(
		"-q", "--quick",
		dest="Quick",
		metavar="Shortcut the checking to only a single region",
		const=True,
		default=False,
		action="store_const",
		help="This flag only checks 'us-east-1', so makes the whole script run really fast.")
parser.my_parser.add_argument(
		"+fix", "+delete",
		dest="FixRun",
		const=True,
		default=False,
		action="store_const",
		help="This will fix the issues found. If default VPCs must be deleted, you'll be asked to confirm.")
parser.my_parser.add_argument(
		"+force",
		dest="pVPCConfirm",
		const=True,
		default=False,
		action="store_const",
		help="This will delete the default VPCs found with NO confirmation. You still have to specify the +fix too")
# TODO: There should be an additional parameter here that would take a role name for access into the account,
#  since it's likely that users won't be able to use the AWSControlTowerExecution role

args = parser.my_parser.parse_args()

Quick = args.Quick
pProfile = args.Profile
pChildAccountId = args.pChildAccountList
verbose = args.loglevel
pRole = args.Role
FixRun = args.FixRun
pExplain = args.pExplain
pVPCConfirm = args.pVPCConfirm
logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")
# This is hard-coded, because this is the listing of regions that are supported by Automated Landing Zone.
if Quick:
	RegionList = ['us-east-1']
else:
	# RegionList = Inventory_Modules.get_ec2_regions('all', pProfile)
	# ap-northeast-3 doesn't support Config (and therefore doesn't support ALZ), but is a region that is normally included within EC2. Therefore - this is easier.
	RegionList = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
	              'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1',
	              'us-east-2', 'us-west-1', 'us-west-2']

ERASE_LINE = '\x1b[2K'

ExplainMessage = """

0. The Child account MUST allow the Management account access into the Child IAM role called "AWSCloudFormationStackSetExecutionRole"
0a. There must be an "AWSCloudFormationStackSetExecution" or "AWSControlTowerExecutionRole" role present in the account so that StackSets can assume it and deploy stack instances. This role must trust the Organizations Management account. In LZ the account is created with that role name so stacksets just works. You can add this role manually via CloudFormation in the existing account. [I did this as a step 0]
0b. STS must be active in all regions. You can check from the Account Settings page in IAM. Since we're using STS to connect to the account from the Management Account, this requirement is checked by successfully completing step 0.

1. The account must not contain any resources/config associated with the Default VPCs in ANY region e.g. security groups cannot exist associated with the Default VPC. Default VPCs will be deleted in the account in all regions, if they contain some dependency (usually a Security Group or an EIP) then deleting the VPC fails and the deployment rolls back. You can either manually delete them all or verify there are no dependencies, in some cases manually deleting them all is faster than roll back.

2. There must be no active config channel and recorder in the account as “there can be only one” of each. This must also be deleted via CLI, not console, switching config off in the console is NOT good enough and just disables it. To Delete the delivery channel and the configuration recorder (can be done via CLI and Python script only):
aws configservice describe-delivery-channels
aws configservice describe-delivery-channel-status
aws configservice describe-configuration-recorders
aws configservice stop-configuration-recorder --configuration-recorder-name <NAME-FROM-DESCRIBE-OUTPUT>
aws configservice delete-delivery-channel --delivery-channel-name <NAME-FROM-DESCRIBE-OUTPUT>
aws configservice delete-configuration-recorder --configuration-recorder-name <NAME-FROM-DESCRIBE-OUTPUT

3. The account must not have a Cloudtrail Trail name the same name as the LZ Trail ("AWS-Landing-Zone-BaselineCloudTrail")

4. The account must not have a pending guard duty invite. You can check from the Guard Duty Console

5. The account must be part of the Organization and the email address being entered into the LZ parameters must match the account. If you try to add an email from an account which is not part of the Org, you will get an error that you are not using a unique email address. If it’s part of the Org, LZ just finds the account and uses the CFN roles.
- If the existing account is to be imported as a Core Account, modify the manifest.yaml file to use it.
- If the existing account will be a child account in the Organization, use the AVM launch template through Service Catalog and enter the appropriate configuration parameters.

6. The existing account can not be in any of the LZ-managed Organizations OUs. By default, these OUs are Core and Applications, but the customer may have chosen different or additional OUs to manage by LZ.

"""
print()
if pExplain:
	print(ExplainMessage)
	sys.exit("Exiting after Script Explanation...")

# TODO: This is supposed to be the recommended Trust Policy for the cross-account role access,
#  so that we can recommend people add it to their "AWSCloudFormationStackSetExecutionRole"
json_formatted_str_TP = ""


##########
def _initdict(StepCount, faccountList):
	fProcessStatus = {}
	for account in faccountList:
		fProcessStatus[account] = {'ChildIsReady': False, 'IssuesFound': 0, 'IssuesFixed': 0}
		for _ in range(StepCount):
			Step = f"Step{str(_)}"
			fProcessStatus[account][Step] = dict()
			fProcessStatus[account][Step]['Success'] = False
			fProcessStatus[account][Step]['IssuesFound'] = 0
			fProcessStatus[account][Step]['IssuesFixed'] = 0
	return fProcessStatus


###########


# Step 0 -
"""
0. The Child account MUST allow the Management account access into the Child IAM role called "AWSCloudFormationStackSetExecutionRole"
Technically, only the Lambda function roles REQUIRE access, but for this script to run, we need that same level of access.
TODO: Eventually, we should update this script to run as that role - which may mean we have to update this script to become a Lambda function, 
but that's sometime in the future.
"""

print("This script does 6 things... ")
print(
	f"{Fore.BLUE}  0.{Fore.RESET} Checks to ensure you have the necessary cross-account role access to the child account.")
print(f"{Fore.BLUE}  1.{Fore.RESET} Checks to ensure the {Fore.RED}Default VPCs {Fore.RESET}in each region are deleted")
if FixRun and not pVPCConfirm:
	print(
		f"{Fore.BLUE}	You've asked to delete any default VPCs we find - with confirmation on each one.{Fore.RESET}")
elif FixRun and pVPCConfirm:
	print()
	print(
		f"{Fore.RED}	You've asked to delete any default VPCs we find - WITH NO CONFIRMATION on each one.{Fore.RESET}")
	print()
elif pVPCConfirm and not FixRun:
	print()
	print(
		f"{Fore.BLUE}	You asked us to delete the default VPCs with no confirmation, but didn't provide the '+fixrun' parameter, so we're proceeding with NOT deleting. You can safely interupt this script and run it again with the necessary parameters.{Fore.RESET}")
	print()
print(f"{Fore.BLUE}  2.{Fore.RESET} Checks the child account in each of the regions")
print(f"     to see if there's already a {Fore.RED}Config Recorder and Delivery Channel {Fore.RESET}enabled...")
print(
	f"{Fore.BLUE}  3.{Fore.RESET} Checks that there isn't a duplicate {Fore.RED}CloudTrail{Fore.RESET} trail in the account.")
print(
	f"{Fore.BLUE}  4.{Fore.RESET} Checks to see if {Fore.RED}GuardDuty{Fore.RESET} has been enabled for this child account.")
print("     If it has been, it needs to be deleted before we can adopt this new account")
print("     into the Org's Automated Landing Zone.")
print(
	f"{Fore.BLUE}  5.{Fore.RESET} This child account {Fore.RED}must exist{Fore.RESET} within the Parent Organization.")
print("     If it doesn't - then you must move it into this Org")
print("     (this script can't do that for you).")
print()
print("Since this script is fairly new - All comments or suggestions are enthusiastically encouraged")
print()

DefaultVPCs = []

aws_account = aws_acct_access(pProfile)
if aws_account.AccountType.lower() == 'root' and pChildAccountId is None:
	# Creates a list of the account numbers in the Org.
	ChildAccountList = [d['AccountId'] for d in aws_account.ChildAccounts]
	print(
		f"Since you didn't specify a specific account, we'll check all {len(aws_account.ChildAccounts)} accounts in the Org.")
elif pChildAccountId is None:
	sys.exit(
		f"Account {aws_account.acct_number} is a {aws_account.AccountType} account. This script should be run with Management Account credentials.")
else:
	print(f"Account {aws_account.acct_number} is a {aws_account.AccountType} account."
	      f"We're checking to validate that account {pChildAccountId} can be adopted into the Landing Zone")
	ChildAccountList = [pChildAccountId]

Steps = 6

ProcessStatus = _initdict(Steps, ChildAccountList)

logging.error(f"There are {Steps} steps to go through for {len(ChildAccountList)} accounts")

# Determining access to each child account
accountsleft = len(ChildAccountList)
for childaccount in ChildAccountList:
	accountsleft -= 1
	# Step 0
	"""
	This part will ascertain whether access to the child works. 
	"""
	try:
		account_credentials = Inventory_Modules.get_child_access3(aws_account, childaccount)
	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			# TODO: This whole section is waiting on an enhancement. Until then, we have to assume that ProServe or someone familiar with ALZ is running this script
			print(f"Authorization Failure for account {childaccount}")
			print(
				f"The child account MUST allow access into the necessary IAM roles from the Organization's Master Account for the rest of this script (and the overall migration) to run.")
			print("You must add the following lines to the Trust Policy of that role in the child account")
			print(json_formatted_str_TP)
			print(my_Error)
			ProcessStatus[childaccount]['Step0']['Success'] = False
		elif str(my_Error).find("AccessDenied") > 0:
			# TODO: This whole section is waiting on an enhancement. Until then, we have to assume that ProServe or someone familiar with ALZ is running this script
			print(f"Access Denied Failure for account {childaccount}")
			print(
				f"The child account MUST allow access into the necessary IAM roles from the Organization's Master Account for the rest of this script (and the overall migration) to run.")
			print("You must add the following lines to the Trust Policy of that role in the child account")
			print(json_formatted_str_TP)
			print(my_Error)
			ProcessStatus[childaccount]['Step0']['Success'] = False
		else:
			print(f"Other kind of failure for account {childaccount}")
			print(my_Error)
			ProcessStatus[childaccount]['Step0']['Success'] = False
	finally:
		if account_credentials['AccessKeyId'] is None:
			logging.error(
				f"Was {Fore.RED}not{Fore.RESET} able to successfully connect to account {childaccount} using credentials from account {aws_account.acct_number}... ")
			print()
			print(f"{Fore.RED}** Step 0 failed for account {childaccount}{Fore.RESET}")
			print()
			ProcessStatus[childaccount]['Step0']['Success'] = False
			ProcessStatus[childaccount]['Step0']['IssuesFound'] += 1
			continue
		else:
			logging.error(
				f"Was able to successfully connect to account {childaccount} using credentials from account {aws_account.acct_number}... ")
			print()
			print(f"{Fore.GREEN}** Step 0 completed without issues{Fore.RESET}")
			print()
			ProcessStatus[childaccount]['Step0']['Success'] = True

	# Step 1
	"""
	This part will find and delete the Default VPCs in each region for the child account. 
	We only delete if you provided that in the parameters list.
	"""
	try:
		print(f"Checking account {childaccount} for default VPCs in any region")
		DefaultVPCFound = False
		for region in RegionList:
			print(ERASE_LINE,
			      f"Checking account {childaccount} in region {region} for {Fore.RED}default VPCs{Fore.RESET}",
			      end='\r')
			logging.info("Looking for Default VPCs in account {} from Region {}}", childaccount, region)
			DefaultVPC = Inventory_Modules.find_account_vpcs2(account_credentials, True)
			if len(DefaultVPC['Vpcs']) > 0:
				DefaultVPCs.append({
					'VPCId'    : DefaultVPC['Vpcs'][0]['VpcId'],
					'AccountID': childaccount,
					'Region'   : region
					})
				ProcessStatus[childaccount]['Step1']['IssuesFound'] += 1
				DefaultVPCFound = True
		if DefaultVPCFound:
			ProcessStatus[childaccount]['Step1']['Success'] = False
		else:
			ProcessStatus[childaccount]['Step1']['Success'] = True
	except ClientError as my_Error:
		logging.warning("Failed to identify the Default VPCs in the region properly")
		ProcessStatus[childaccount]['Step1']['Success'] = False
		print(my_Error)

	print(ERASE_LINE, end='\r')
	for i in range(len(DefaultVPCs)):
		logging.info(
			f"I found a default VPC for account {DefaultVPCs[i]['AccountID']} in region {DefaultVPCs[i]['Region']}")
		if FixRun:
			logging.warning(
				f"Deleting VpcId {DefaultVPCs[i]['VPCId']} in account {DefaultVPCs[i]['AccountID']} in region {DefaultVPCs[i]['Region']}")
			try:  # confirm the user really want to delete the VPC. This is irreversible
				if pVPCConfirm:
					ReallyDelete = True
				else:
					ReallyDelete = (input(
						f"Deletion of {DefaultVPCs[i]['Region']} default VPC has been requested. Are you still sure? (y/n): ") in [
						                'y', 'Y'])
				if ReallyDelete:
					DelVPC_Success = (vpc_modules.del_vpc(account_credentials, DefaultVPCs[i]['VPCId'],
					                                      DefaultVPCs[i]['Region']) == 0)
					if DelVPC_Success:
						ProcessStatus[childaccount]['Step1']['IssuesFixed'] += 1
					else:
						print("Something went wrong with the VPC Deletion")
						ProcessStatus[childaccount]['Step1']['Success'] = False
						sys.exit(9)
				else:
					logging.warning("User answered False to the 'Are you sure' question")
					print(
						f"Skipping VPC ID {DefaultVPCs[i]['VPCId']} in account {DefaultVPCs[i]['AccountID']} in region {DefaultVPCs[i]['Region']}")
					ProcessStatus[childaccount]['Step1']['Success'] = False
			except ClientError as my_Error:
				logging.error("Failed to delete the Default VPCs in the region properly")
				ProcessStatus[childaccount]['Step1']['Success'] = False
				print(my_Error)

	print()
	if ProcessStatus[childaccount]['Step1']['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 1 completed with no issues{Fore.RESET}")
	elif ProcessStatus[childaccount]['Step1']['IssuesFound'] - ProcessStatus[childaccount]['Step1']['IssuesFixed'] == 0:
		print(
			f"{ERASE_LINE + Fore.GREEN}** Step 1 found {ProcessStatus[childaccount]['Step1']['IssuesFound']} issues, but they were fixed by deleting the default vpcs{Fore.RESET}")
		ProcessStatus[childaccount]['Step1']['Success'] = True
	elif ProcessStatus[childaccount]['Step1']['IssuesFound'] > ProcessStatus[childaccount]['Step1']['IssuesFixed']:
		print(
			f"{ERASE_LINE + Fore.RED}** Step 1 completed, but there were {ProcessStatus[childaccount]['Step1']['IssuesFound'] - ProcessStatus[childaccount]['Step1']['IssuesFixed']} vpcs that couldn't be fixed{Fore.RESET}")
	else:
		print(f"{ERASE_LINE + Fore.RED}** Step 1 completed with blockers found{Fore.RESET}")

	# Step 2
	# This part will check the Config Recorder and  Delivery Channel. If they have one, we need to delete it, so we can create another. We'll ask whether this is ok before we delete.
	ConfigList = []
	DeliveryChanList = []
	config_deliv_channels_found = False
	try:
		# RegionList=Inventory_Modules.get_service_regions('config', 'all')
		print(f"Checking account {childaccount} for Config Recorders and Delivery Channels in any region")
		# TODO: Need to find a way to gracefully handle the error processing of opt-in regions.
		# Until then - we're using a hard-coded listing of regions, instead of dynamically finding those.
		for region in RegionList:
			print(ERASE_LINE, f"Checking account {childaccount} in region {region} for Config Recorder", end='\r')
			logging.info(f"Looking for Config Recorders in account {childaccount} from Region {region}")
			ConfigRecorder = Inventory_Modules.find_config_recorders2(account_credentials, region)
			logging.debug("Tried to capture Config Recorder")
			if len(ConfigRecorder['ConfigurationRecorders']) > 0:
				ConfigList.append({
					'Name'     : ConfigRecorder['ConfigurationRecorders'][0]['name'],
					'roleARN'  : ConfigRecorder['ConfigurationRecorders'][0]['roleARN'],
					'AccountID': childaccount,
					'Region'   : region
					})
			print(ERASE_LINE, f"Checking account {childaccount} in region {region} for Delivery Channel", end='\r')
			DeliveryChannel = Inventory_Modules.find_delivery_channels2(account_credentials, region)
			logging.debug("Tried to capture Delivery Channel")
			if len(DeliveryChannel['DeliveryChannels']) > 0:
				DeliveryChanList.append({
					'Name'     : DeliveryChannel['DeliveryChannels'][0]['name'],
					'AccountID': childaccount,
					'Region'   : region
					})
		logging.error(
			f"Checked account {childaccount} in {len(RegionList)} regions. Found {len(ConfigList) + len(DeliveryChanList)} issues with Config Recorders and Delivery Channels")
	except ClientError as my_Error:
		logging.warning("Failed to capture Config Recorder and Delivery Channels")
		ProcessStatus[childaccount]['Step2']['Success'] = False
		print(my_Error)

	for i in range(len(ConfigList)):
		logging.error(f"{Fore.RED}Found a config recorder for account %s in region %s", ConfigList[i]['AccountID'],
		              ConfigList[i]['Region'] + Fore.RESET)
		ProcessStatus[childaccount]['Step2']['IssuesFound'] += 1
		config_deliv_channels_found = True
		if FixRun:
			logging.warning("Deleting %s in account %s in region %s", ConfigList[i]['Name'], ConfigList[i]['AccountID'],
			                ConfigList[i]['Region'])
			DelConfigRecorder = Inventory_Modules.del_config_recorder2(account_credentials, ConfigList[i]['Region'],
			                                                           ConfigList[i]['Name'])
			# We assume the process worked. We should probably NOT assume this.
			ProcessStatus[childaccount]['Step2']['IssuesFixed'] += 1
	for i in range(len(DeliveryChanList)):
		logging.error(f"{Fore.RED}I found a delivery channel for account %s in region %s",
		              DeliveryChanList[i]['AccountID'], DeliveryChanList[i]['Region'] + Fore.RESET)
		ProcessStatus[childaccount]['Step2']['IssuesFound'] += 1
		config_deliv_channels_found = True
		if FixRun:
			logging.warning("Deleting %s in account %s in region %s", DeliveryChanList[i]['Name'],
			                DeliveryChanList[i]['AccountID'], DeliveryChanList[i]['Region'])
			DelDeliveryChannel = Inventory_Modules.del_delivery_channel2(account_credentials, ConfigList[i]['Region'],
			                                                             DeliveryChanList[i]['Name'])
			# We assume the process worked. We should probably NOT assume this.
			ProcessStatus[childaccount]['Step2']['IssuesFixed'] += 1
	if config_deliv_channels_found:
		ProcessStatus[childaccount]['Step2']['Success'] = False
	else:
		ProcessStatus[childaccount]['Step2']['Success'] = True

	if ProcessStatus[childaccount]['Step2']['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 2 completed with no issues{Fore.RESET}")
	elif ProcessStatus[childaccount]['Step2']['IssuesFound'] - ProcessStatus[childaccount]['Step2']['IssuesFixed'] == 0:
		print(
			f"{ERASE_LINE + Fore.GREEN}** Step 2 found {ProcessStatus[childaccount]['Step2']['IssuesFound']} issues, but they were fixed by deleting the existing Config Recorders and Delivery Channels{Fore.RESET}")
		ProcessStatus[childaccount]['Step2']['Success'] = True
	elif ProcessStatus[childaccount]['Step2']['IssuesFound'] > ProcessStatus[childaccount]['Step2']['IssuesFixed']:
		print(
			f"{ERASE_LINE + Fore.RED}** Step 2 completed, but there were {ProcessStatus[childaccount]['Step2']['IssuesFound'] - ProcessStatus[childaccount]['Step2']['IssuesFixed']} items found that couldn't be deleted{Fore.RESET}")
	else:
		print(f"{ERASE_LINE + Fore.RED}** Step 2 completed with blockers found{Fore.RESET}")
	print()

	# Step 3
	# 3. The account must not have a Cloudtrail Trail name the same name as the LZ Trail ("AWS-Landing-Zone-BaselineCloudTrail")
	CTtrails2 = []
	trailname = None
	ct_trail_found = False
	try:
		print(f"Checking account {childaccount} for a specially named CloudTrail in all regions")
		for region in RegionList:
			print(ERASE_LINE, f"Checking account {childaccount} in region {region} for CloudTrail trails", end='\r')
			CTtrails = Inventory_Modules.find_cloudtrails2(account_credentials, region,
			                                               ['AWS-Landing-Zone-BaselineCloudTrail'])
			if len(CTtrails) > 0:
				logging.error(
					f"Unfortunately, we've found existing CloudTrails in account {childaccount} in the {region} region, which means we'll have to delete it before this account can be adopted.")
				# CTtrails['trailList'][0]['region'] = region
				CTtrails2.extend(CTtrails)
				ct_trail_found = True
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[childaccount]['Step3']['Success'] = False

	for i in range(len(CTtrails2)):
		logging.error(
			f"{Fore.RED}Found a CloudTrail trail for account {childaccount} in region {CTtrails2[i]['HomeRegion']} named {CTtrails2[i]['Name']}{Fore.RESET}")
		ProcessStatus[childaccount]['Step3']['IssuesFound'] += 1
		if FixRun:
			try:
				logging.error("CloudTrail trail deletion commencing...")
				delresponse = Inventory_Modules.del_cloudtrails2(account_credentials, CTtrails2[i]['HomeRegion'],
				                                                 CTtrails2[i]['TrailARN'])
				ProcessStatus[childaccount]['Step3']['IssuesFixed'] += 1
			except ClientError as my_Error:
				print(my_Error)
	if ct_trail_found:
		ProcessStatus[childaccount]['Step3']['Success'] = False
	else:
		ProcessStatus[childaccount]['Step3']['Success'] = True

	if ProcessStatus[childaccount]['Step3']['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 3 completed with no issues{Fore.RESET}")
	elif ProcessStatus[childaccount]['Step3']['IssuesFound'] - ProcessStatus[childaccount]['Step3']['IssuesFixed'] == 0:
		print(
			f"{ERASE_LINE + Fore.GREEN}** Step 3 found {ProcessStatus[childaccount]['Step3']['IssuesFound']} issues, but they were fixed by deleting the existing CloudTrail trail names{Fore.RESET}")
		ProcessStatus[childaccount]['Step3']['Success'] = True
	elif ProcessStatus[childaccount]['Step3']['IssuesFound'] > ProcessStatus[childaccount]['Step3']['IssuesFixed']:
		print(
			f"{ERASE_LINE + Fore.RED}** Step 3 completed, but there were {ProcessStatus[childaccount]['Step3']['IssuesFound'] - ProcessStatus[childaccount]['Step3']['IssuesFixed']} trail names found that couldn't be deleted{Fore.RESET}")
	else:
		print(f"{ERASE_LINE + Fore.RED}** Step 3 completed with blockers found{Fore.RESET}")
	print()

	# Step 4
	# 4. The account must not have a pending guard duty invite. You can check from the Guard Duty Console
	GDinvites2 = []
	gdinvites_found = False
	try:
		print(f"Checking account {childaccount} for any GuardDuty invites")
		for region in RegionList:
			print(
				f"{ERASE_LINE}Checking account {childaccount} in region {region} for {Fore.RED}GuardDuty{Fore.RESET}invitations",
				end='\r')
			GDinvites = Inventory_Modules.find_gd_invites2(account_credentials, region)
			if len(GDinvites['Invitations']) > 0:
				gdinvites_found = True
				for x in range(len(GDinvites['Invitations'])):
					logging.warning("GD Invite: %s", str(GDinvites['Invitations'][x]))
					logging.error(
						f"Unfortunately, we've found a GuardDuty invitation for account {childaccount} in the {region} region from account {GDinvites['Invitations'][x]['AccountId']}, which means we'll have to delete it before this account can be adopted.")
					ProcessStatus[childaccount]['Step4']['IssuesFound'] += 1
					GDinvites2.append({
						'AccountId'   : GDinvites['Invitations'][x]['AccountId'],
						'InvitationId': GDinvites['Invitations'][x]['InvitationId'],
						'Region'      : region
						})
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[childaccount]['Step4']['Success'] = False

	for i in range(len(GDinvites2)):
		logging.error(f"{Fore.RED}I found a GuardDuty invitation for account %s in region %s from account %s ",
		              childaccount, GDinvites2[i]['Region'], GDinvites2[i]['AccountId'] + Fore.RESET)
		ProcessStatus[childaccount]['Step4']['IssuesFound'] += 1
		if FixRun:
			for x in range(len(GDinvites2)):
				try:
					logging.warning("GuardDuty invite deletion commencing...")
					delresponse = Inventory_Modules.delete_gd_invites2(account_credentials, GDinvites2[x]['Region'],
					                                                   GDinvites2[x]['AccountId'])
					ProcessStatus[childaccount]['Step4']['IssuesFixed'] += 1
				# We assume the process worked. We should probably NOT assume this.
				except ClientError as my_Error:
					print(my_Error)
	if gdinvites_found:
		ProcessStatus[childaccount]['Step4']['Success'] = False
	else:
		ProcessStatus[childaccount]['Step4']['Success'] = True

	if ProcessStatus[childaccount]['Step4']['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 4 completed with no issues{Fore.RESET}")
	elif ProcessStatus[childaccount]['Step4']['IssuesFound'] - ProcessStatus[childaccount]['Step4']['IssuesFixed'] == 0:
		print(
			f"{ERASE_LINE + Fore.GREEN}** Step 4 found {ProcessStatus[childaccount]['Step4']['IssuesFound']} guardduty invites, but they were deleted{Fore.RESET}")
		ProcessStatus[childaccount]['Step4']['Success'] = True
	elif ProcessStatus[childaccount]['Step4']['IssuesFound'] > ProcessStatus[childaccount]['Step4']['IssuesFixed']:
		print(
			f"{ERASE_LINE + Fore.RED}** Step 4 completed, but there were {ProcessStatus[childaccount]['Step4']['IssuesFound'] - ProcessStatus[childaccount]['Step4']['IssuesFixed']} guardduty invites found that couldn't be deleted{Fore.RESET}")
	else:
		print(f"{ERASE_LINE + Fore.RED}** Step 4 completed with blockers found{Fore.RESET}")
	print()

	"""
	# Step 4.5
	# STS must be active in all regions. You can check from the Account Settings page in IAM.
	We would have already verified this - since we've used STS to connect to each region already for the previous steps.
	"""
	# Step 5
	'''
	5. The account must be part of the Organization and the email address being entered into the LZ parameters must match the account. If 	you try to add an email from an account which is not part of the Org, you will get an error that you are not using a unique email address. If it’s part of the Org, LZ just finds the account and uses the CFN roles.
	- If the existing account is to be imported as a Core Account, modify the manifest.yaml file to use it.
	- If the existing account will be a child account in the Organization, use the AVM launch template through Service Catalog and enter the appropriate configuration parameters.
	'''
	print("Checking that the account is part of the AWS Organization.")
	if childaccount in [d['AccountId'] for d in aws_account.ChildAccounts]:
		ProcessStatus[childaccount]['Step5']['Success'] = True
	else:
		print()
		print(
			f"Account # {childaccount} is not a part of the Organization. This account needs to be moved into the Organization to be adopted into the Landing Zone tool")
		print("This is easiest done manually right now.")
		ProcessStatus[childaccount]['Step5']['Success'] = False
		ProcessStatus[childaccount]['Step5']['IssuesFound'] += 1

	if ProcessStatus[childaccount]['Step5']['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 5 completed with no issues{Fore.RESET}")
	elif ProcessStatus[childaccount]['Step5']['IssuesFound'] - ProcessStatus[childaccount]['Step5']['IssuesFixed'] == 0:
		print(
			f"{ERASE_LINE + Fore.GREEN}** Step 5 found {ProcessStatus[childaccount]['Step5']['IssuesFound']} issues, but we were able to move the account into the they were able to be fixed{Fore.RESET}")
		ProcessStatus[childaccount]['Step5']['Success'] = True
	elif ProcessStatus[childaccount]['Step5']['IssuesFound'] > ProcessStatus[childaccount]['Step5']['IssuesFixed']:
		print(
			f"{ERASE_LINE + Fore.RED}** Step 5 completed, but there were {ProcessStatus[childaccount]['Step5']['IssuesFound'] - ProcessStatus[childaccount]['Step5']['IssuesFixed']} blockers found that couldn't be fixed{Fore.RESET}")
	else:
		print(f"{ERASE_LINE + Fore.RED}** Step 5 completed with blockers found{Fore.RESET}")
	print()

	print(f"{Fore.CYAN}Account {childaccount} is complete. {accountsleft} more to go!!{Fore.RESET}")

	"""
	# Step 6
	# 6. The existing account can not be in any of the LZ-managed Organizations OUs. By default, these OUs are Core and Applications, but the customer may have chosen different or additional OUs to manage by LZ.
	So we'll need to verify that the parent OU of the account is the root of the organization.
	"""

x = PrettyTable()
y = PrettyTable()

x.field_names = ['Account', 'Issues Found', 'Issues Fixed', 'Ready?']
# The following headers represent Step0 through Step5,
y.field_names = ['Account', 'Account Access', 'Default VPCs', 'Recorders', 'CloudTrail', 'GuardDuty', 'Org Member',
                 'Ready?']
for item in ProcessStatus:
	for _ in range(Steps):
		Step = f"Step{str(_)}"
		ProcessStatus[item]['IssuesFound'] += ProcessStatus[item][Step]['IssuesFound']
		ProcessStatus[item]['IssuesFound'] += ProcessStatus[item][Step]['IssuesFixed']
	x.add_row([item, ProcessStatus[item]['IssuesFound'], ProcessStatus[item]['IssuesFixed'],
	           ProcessStatus[item]['ChildIsReady']])
	y.add_row([
		item,
		ProcessStatus[item]['Step0']['IssuesFound'] - ProcessStatus[item]['Step0']['IssuesFixed'],
		ProcessStatus[item]['Step1']['IssuesFound'] - ProcessStatus[item]['Step1']['IssuesFixed'],
		ProcessStatus[item]['Step2']['IssuesFound'] - ProcessStatus[item]['Step2']['IssuesFixed'],
		ProcessStatus[item]['Step3']['IssuesFound'] - ProcessStatus[item]['Step3']['IssuesFixed'],
		ProcessStatus[item]['Step4']['IssuesFound'] - ProcessStatus[item]['Step4']['IssuesFixed'],
		ProcessStatus[item]['Step5']['IssuesFound'] - ProcessStatus[item]['Step5']['IssuesFixed'],
		ProcessStatus[item]['Step0']['Success'] and ProcessStatus[item]['Step1']['Success'] and
		ProcessStatus[item]['Step2']['Success'] and ProcessStatus[item]['Step3']['Success'] and
		ProcessStatus[item]['Step4']['Success'] and ProcessStatus[item]['Step5']['Success']
		])
print(
	"The following table represents the accounts looked at, and whether they are ready to be incorporated into an ALZ environment.")
print(x)
print()
print(
	"The following table represents the accounts looked at, and gives details under each type of issue as to what might prevent a successful migration of this account into an ALZ environment.")
print(y)

print("Thanks for using this script...")
