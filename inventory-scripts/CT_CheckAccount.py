#!/usr/bin/env python3

from pprint import pprint
import sys
import os
import Inventory_Modules
from time import time
from colorama import init, Fore
from queue import Queue
from threading import Thread
from botocore.exceptions import ClientError
from prettytable import PrettyTable
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access

import logging

init()
__version__ = "2024.05.18"

script_path, script_name = os.path.split(sys.argv[0])
parser = CommonArguments()
parser.singleprofile()
parser.multiregion()
# The following includes "force", "skipaccount", "skipprofile", "account"
parser.extendedargs()
parser.deletion()
parser.roletouse()
parser.verbosity()
parser.timing()
parser.version(__version__)
local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
local.add_argument(
	"--explain",
	dest="pExplain",
	const=True,
	default=False,
	action="store_const",
	help="This flag prints out the explanation of what this script would do.")
local.add_argument(
	"-q", "--quick",
	dest="Quick",
	metavar="Shortcut the checking to only a single region",
	const=True,
	default=False,
	action="store_const",
	help="This flag only checks 'us-east-1', so makes the whole script run really fast.")
local.add_argument(
	"+fix", "+delete",
	dest="FixRun",
	const=True,
	default=False,
	action="store_const",
	help="This will fix the issues found. If default VPCs must be deleted, you'll be asked to confirm.")
args = parser.my_parser.parse_args()

Quick = args.Quick
pProfile = args.Profile
pRegions = args.Regions
pSkipAccounts = args.SkipAccounts
pTiming = args.Time
verbose = args.loglevel
pAccessRole = args.AccessRole
pChildAccountList = args.Accounts
FixRun = args.FixRun
pExplain = args.pExplain
pVPCConfirm = args.Force
# Setup logging levels
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def intersection(lst1, lst2):
	lst3 = [value for value in lst1 if value in lst2]
	return lst3


def explain_script():
	print("This script does the following... ")
	print(f"{Fore.BLUE}  0.{Fore.RESET} Checks to ensure you have the necessary cross-account role access to the child account.")
	print(f"{Fore.BLUE}  1.{Fore.RESET} This check previously checked for default VPCs, but has since been removed.")
	print(f"{Fore.BLUE}  2.{Fore.RESET} Checks the child account in each of the regions")
	print(f"     to see if there's already a {Fore.RED}Config Recorder and Delivery Channel {Fore.RESET}enabled...")
	print(f"{Fore.BLUE}  3.{Fore.RESET} Checks that there isn't a duplicate {Fore.RED}CloudTrail{Fore.RESET} trail in the account.")
	print(f"{Fore.BLUE}  4.{Fore.RESET} This check previously checked for the presence of GuardDuty within this account, but has since been removed.")
	print(f"{Fore.BLUE}  5.{Fore.RESET} This child account {Fore.RED}must exist{Fore.RESET} within the Parent Organization.")
	print("     If it doesn't - then you must move it into this Org - this script can't do that for you.")
	print(f"{Fore.BLUE}  6.{Fore.RESET} The target account {Fore.RED}can't exist{Fore.RESET} within an already managed OU.")
	print("     If it does - then you're already managing this account with Control Tower and just don't know it.")
	print(f"{Fore.BLUE}  7.{Fore.RESET} Looking for {Fore.RED}SNS Topics{Fore.RESET} with duplicate names.")
	print("     If found, we can delete them, but you probably want to do that manually - to be sure.")
	print(f"{Fore.BLUE}  8.{Fore.RESET} Looking for {Fore.RED}Lambda Functions{Fore.RESET} with duplicate names.")
	print("     If found, we can delete them, but you probably want to do that manually - to be sure.")
	print(f"{Fore.BLUE}  9.{Fore.RESET} Looking for {Fore.RED}IAM Roles{Fore.RESET} with duplicate names.")
	print("     If found, we can delete them, but you probably want to do that manually - to be sure.")
	print(f"{Fore.BLUE}  10.{Fore.RESET} Looking for duplicate {Fore.RED}CloudWatch Log Groups.{Fore.RESET}")
	print("     If found, we can delete them, but you probably want to do that manually - to be sure.")
	print()
	print("Since this script is fairly new - All comments or suggestions are enthusiastically encouraged")
	print()


def summarizeOrgResults(fOrgResults):
	summary = {}
	for record in fOrgResults:
		account = record['AccountId']
		region = record['Region']
		if account not in summary:
			summary[account] = {'AccountId': account, 'Regions': [], 'IssuesFound': 0, 'IssuesFixed': 0, 'Ready': True}
		if region not in summary[account]['Regions']:
			summary[account]['Regions'].append(region)
		summary[account]['IssuesFound'] += record['IssuesFound']
		summary[account]['IssuesFixed'] += record['IssuesFixed']
		if not record['Ready']:
			summary[account]['Ready'] = False
	return dict(sorted(summary.items()))


def DoAccountSteps(fChildAccountId, aws_account, fFixRun, fRegion):
	def InitDict(StepCount):
		fProcessStatus = {}
		# fProcessStatus['ChildAccountIsReady']=True
		# fProcessStatus['IssuesFound']=0
		# fProcessStatus['IssuesFixed']=0
		for item in range(StepCount):
			Step = f"Step{str(item)}"
			fProcessStatus[Step] = {}
			fProcessStatus[Step]['Success'] = True
			fProcessStatus[Step]['IssuesFound'] = 0
			fProcessStatus[Step]['IssuesFixed'] = 0
			fProcessStatus[Step]['ProblemsFound'] = []
		return fProcessStatus

	NumOfSteps = 11

	# Step 0
	ProcessStatus = InitDict(NumOfSteps)
	OrgAccountList = [d['AccountId'] for d in aws_account.ChildAccounts]
	account_credentials = {'Success': False, 'AccessError': True, 'ErrorMessage': 'Initialization Parameters'}
	Step = 'Step0'
	# This next list is the list of attempted roles. If you use a different named role for broad access, make sure it appears in this list.
	CTRoles = [pAccessRole, 'AWSControlTowerExecution', 'AWSCloudFormationStackSetExecutionRole', 'Owner', 'OrganizationAccountAccessRole']
	# TODO: I don't use this next variable, but eventually I intend to supply the JSON code needed to update a role with.
	json_formatted_str_TP = ""
	print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
	print(f"Confirming we have the necessary cross-account access to account {fChildAccountId} in region {fRegion}") if verbose < 50 else None
	try:
		account_credentials = Inventory_Modules.get_child_access3(aws_account, fChildAccountId, fRegion, CTRoles)
	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			# TODO: This whole section is waiting on an enhancement. Until then, we have to assume that ProServe or someone familiar with Control Tower is running this script
			print(f"{aws_account.acct_number}: Authorization Failure for account {fChildAccountId}")
			print("The child account MUST allow access into the proper IAM role from the Organization's Management Account for the rest of this script (and the overall migration) to run.")
			print("You must add the following lines to the Trust Policy of that role in the child account")
			print(json_formatted_str_TP)
			print(my_Error)
			ProcessStatus[Step]['Success'] = False
			sys.exit("Exiting due to Authorization Failure...")
		elif str(my_Error).find("AccessDenied") > 0:
			# TODO: This whole section is waiting on an enhancement. Until then, we have to assume that ProServe or someone familiar with Control Tower is running this script
			print(f"{aws_account.acct_number}: Access Denied Failure for account {fChildAccountId}")
			print("The child account MUST allow access into the proper IAM role from the Organization's Management Account for the rest of this script (and the overall migration) to run.")
			print("You must add the following lines to the Trust Policy of that role in the child account")
			print(json_formatted_str_TP)
			print(my_Error)
			ProcessStatus[Step]['Success'] = False
			sys.exit("Exiting due to Access Denied Failure...")
		else:
			print(f"{aws_account.acct_number}: Other kind of failure for account {fChildAccountId}")
			print(my_Error)
			ProcessStatus[Step]['Success'] = False
			sys.exit("Exiting for other failure...")
	except Exception as my_Error:
		error_message = f"This shouldn't happen - failing to access {fChildAccountId} from this Management Account {aws_account.acct_number} for region {fRegion}"
		logging.error(f"Error Message: {error_message}\n"
		              f"Error: {my_Error}")
	finally:
		if account_credentials['AccessError']:
			print(f"{Fore.RED}We weren't able to connect to the Child Account {fChildAccountId} from this Management Account {aws_account.acct_number}. Please check the role Trust Policy and re-run this script.{Fore.RESET}")
			print(f"The following list of roles were tried, but none were allowed access to account {fChildAccountId} using the {aws_account.acct_number} account in region {fRegion}")
			print(Fore.RED, CTRoles, Fore.RESET)
			logging.debug(account_credentials)
			ProcessStatus[Step]['Success'] = False
			sys.exit("Exiting due to cross-account access failure")

	logging.info("Was able to successfully connect using the credentials... ")
	print() if verbose < 50 else None
	print(f"Confirmed the role {Fore.GREEN}{account_credentials['Role']}{Fore.RESET}"
	      f" exists in account {Fore.GREEN}{fChildAccountId}{Fore.RESET} and trusts the Management Account") if verbose < 50 else None
	print(f"{Fore.GREEN}** Step 0 completed without issues{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	"""
	Step 1 - We should check whether Config is enabled as an Organizationally Trusted Service here. 

	"""
	Step = 'Step1'
	serviceName = 'config.amazonaws.com'
	print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
	print(f"Checking Org Account {fChildAccountId} to see if Config is enabled at the Org Level\n"
	      f"Which means we only run this step if this is the Root Account\n"
	      f"{'which this account is not, so we are continuing...' if not account_credentials['AccountId'] == account_credentials['ParentAcctId'] else None}") if verbose < 50 else None
	# Checks to see if 'config.amazonaws.com' is a trusted org service in the Management Account. If so - we'll FAIL, since Control Tower wants to turn it on.
	result = Inventory_Modules.find_org_services2(account_credentials, [serviceName]) if account_credentials['AccountId'] == account_credentials['ParentAcctId'] else None
	if result is not None and len(result) != 0:
		print() if verbose < 50 else None
		print(f"{serviceName} is enabled within your Organization. Control Tower needs it to be disabled before continuing.") if verbose < 50 else None
		print("This is easiest done manually right now, or you could re-run this script with the '+fix' parameter and we'll fix EVERYTHING we find - without asking first.") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = False
		ProcessStatus[Step]['IssuesFound'] += 1

	if fFixRun:
		logging.warning(f"{Fore.RED}Found {serviceName} is enabled as an Organizational Service and you've requested that we remedy that for you... {Fore.RESET}")
		ProcessStatus[Step]['Success'] = False
		ProcessStatus[Step]['IssuesFound'] += 1
		ProcessStatus[Step]['ProblemsFound'].extend({'Name'     : result['ServicePrincipal'],
		                                             'AccountId': account_credentials['AccountId'],
		                                             'Region'   : account_credentials['Region']})
		logging.warning(f"Deleting in account {account_credentials['AccountId']} in region {account_credentials['Region']}")
		DelConfigService = Inventory_Modules.disable_org_service2(account_credentials, serviceName)
		if DelConfigService['Success']:
			ProcessStatus[Step]['IssuesFixed'] += 1
		else:
			ProcessStatus[Step]['Success'] = False
			logging.error(DelConfigService['ErrorMessage'])

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issue, but we were able to fix it{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed, but there was {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} blocker found that wasn't fixed{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	# Step 2
	# This part will check the Config Recorder and  Delivery Channel. If they have one, we need to delete it, so we can create another. We'll ask whether this is ok before we delete.
	Step = 'Step2'
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f" Checking account {fChildAccountId} for a Config Recorders and Delivery Channels in any region") if verbose < 50 else None
		ConfigList = []
		DeliveryChanList = []
		print(ERASE_LINE, f"Checking account {fChildAccountId} in region {fRegion} for Config Recorder", end='\r') if verbose < 50 else None
		logging.info("Looking for Config Recorders in account %s from Region %s", fChildAccountId, fRegion)
		ConfigRecorder = Inventory_Modules.find_config_recorders2(account_credentials, fRegion)
		logging.debug("Tried to capture Config Recorder")
		if len(ConfigRecorder['ConfigurationRecorders']) > 0:
			ConfigList.append({
				'Name'     : ConfigRecorder['ConfigurationRecorders'][0]['name'],
				'roleARN'  : ConfigRecorder['ConfigurationRecorders'][0]['roleARN'],
				'AccountID': fChildAccountId,
				'Region'   : fRegion
			})
		print(f"{ERASE_LINE}Checking account {fChildAccountId} in region {fRegion} for Delivery Channel", end='\r') if verbose < 50 else None
		DeliveryChannel = Inventory_Modules.find_delivery_channels2(account_credentials, fRegion)
		logging.debug("Tried to capture Delivery Channel")
		if len(DeliveryChannel['DeliveryChannels']) > 0:
			DeliveryChanList.append({
				'Name'     : DeliveryChannel['DeliveryChannels'][0]['name'],
				'AccountID': fChildAccountId,
				'Region'   : fRegion
			})
		logging.warning(f"Checked account {fChildAccountId} in {len(RegionList)} regions. Found {len(ConfigList) + len(DeliveryChanList)} issues with Config Recorders and Delivery Channels")
	except ClientError as my_Error:
		logging.warning("Failed to capture Config Recorder and Delivery Channels")
		ProcessStatus[Step]['Success'] = False
		print(my_Error)

	for _ in range(len(ConfigList)):
		logging.warning(f"{Fore.RED}Found a config recorder for account %s in region %s", ConfigList[_]['AccountID'], ConfigList[_]['Region'] + Fore.RESET)
		ProcessStatus[Step]['Success'] = False
		ProcessStatus[Step]['IssuesFound'] += 1
		ProcessStatus[Step]['ProblemsFound'].extend(ConfigList)
		if fFixRun:
			logging.warning("Deleting %s in account %s in region %s", ConfigList[_]['Name'], ConfigList[_]['AccountID'], ConfigList[_]['Region'])
			DelConfigRecorder = Inventory_Modules.del_config_recorder2(account_credentials, ConfigList[_]['Region'], ConfigList[_]['Name'])
			# We assume the process worked. We should probably NOT assume this.
			ProcessStatus[Step]['IssuesFixed'] += 1
	for _ in range(len(DeliveryChanList)):
		logging.warning(f"{Fore.RED}Found a delivery channel for account {DeliveryChanList[_]['AccountID']} in region {DeliveryChanList[_]['Region']}{Fore.RESET}")
		ProcessStatus[Step]['Success'] = False
		ProcessStatus[Step]['IssuesFound'] += 1
		ProcessStatus[Step]['ProblemsFound'].extend(DeliveryChanList)
		if fFixRun:
			logging.warning("Deleting %s in account %s in region %s", DeliveryChanList[_]['Name'], DeliveryChanList[_]['AccountID'], DeliveryChanList[_]['Region'])
			DelDeliveryChannel = Inventory_Modules.del_delivery_channel2(account_credentials, DeliveryChanList[_]['Region'], DeliveryChanList[_]['Name'])
			# We assume the process worked. We should probably NOT assume this.
			ProcessStatus[Step]['IssuesFixed'] += 1

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 2 completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** Step 2 found {ProcessStatus[Step]['IssuesFound']} issues, but they were fixed by deleting the existing Config Recorders and Delivery Channels{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** Step 2 completed, but there were {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} items found that weren't deleted{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** Step 2 completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	# Step 3
	# 3. The account must not have a Cloudtrail Trail name the same name as the CT Trail ("AWS-Landing-Zone-BaselineCloudTrail")
	Step = 'Step3'
	CTtrails2 = []
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f" Checking account {fChildAccountId} for a specially named CloudTrail in all regions") if verbose < 50 else None
		print(ERASE_LINE, f"Checking account {fChildAccountId} in region {fRegion} for CloudTrail trails", end='\r') if verbose < 50 else None
		CTtrails = Inventory_Modules.find_cloudtrails2(account_credentials, fRegion, ['aws-controltower-BaselineCloudTrail'])
		if len(CTtrails) > 0:
			logging.warning(f"Unfortunately, we've found a CloudTrail log named {CTtrails[0]['Name']} in account {fChildAccountId} "
			                f"in the {fRegion} region, which means we'll have to delete it before this account can be adopted.")
			CTtrails2.append(CTtrails[0])
			ProcessStatus[Step]['Success'] = False
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success'] = False

	for _ in range(len(CTtrails2)):
		logging.warning(f"{Fore.RED}Found a CloudTrail trail for account {fChildAccountId} in region {CTtrails2[_]['HomeRegion']} named {CTtrails2[_]['Name']}{Fore.RESET}")
		ProcessStatus[Step]['IssuesFound'] += 1
		ProcessStatus[Step]['ProblemsFound'].extend(CTtrails2)
		if fFixRun:
			try:
				logging.warning("CloudTrail trail deletion commencing...")
				delresponse = Inventory_Modules.del_cloudtrails2(account_credentials, fRegion, CTtrails2[_]['TrailARN'])
				ProcessStatus[Step]['IssuesFixed'] += 1
			except ClientError as my_Error:
				print(my_Error)

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issues, but they were fixed by deleting the existing CloudTrail trail names{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed, but there were {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} trail names found that wasn't deleted{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	""" Step 4
	# Step 4 -- The lack of or use of GuardDuty isn't a pre-requisite for Control Tower --
	# 4. This section checks for a pending guard duty invite. You can also check from the Guard Duty Console
	Step='Step4'
	try:
		print(Fore.BLUE + "{}:".format(Step) + Fore.RESET)
		print(" Checking account {} for any GuardDuty invites".format(fChildAccountId))
		GDinvites2=[]
		for region in fRegionList:
			logging.warning("Checking account %s in region %s for", fChildAccountId, region+Fore.RED+" GuardDuty"+Fore.RESET+" invitations")
			logging.warning("Checking account %s in region %s for GuardDuty invites", fChildAccountId, region)
			GDinvites=Inventory_Modules.find_gd_invites(account_credentials, region)
			if len(GDinvites) > 0:
				for x in range(len(GDinvites['Invitations'])):
					logging.warning("GD Invite: %s", str(GDinvites['Invitations'][x]))
					logging.warning("Unfortunately, we've found a GuardDuty invitation for account %s in the %s region from account %s, which means we'll have to delete it before this account can be adopted.", fChildAccountId, region, GDinvites['Invitations'][x]['AccountId'])
					ProcessStatus[Step]['IssuesFound']+=1
					GDinvites2.append({
						'AccountId': GDinvites['Invitations'][x]['AccountId'],
						'InvitationId': GDinvites['Invitations'][x]['InvitationId'],
						'Region': region
					})
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success']=False

	for i in range(len(GDinvites2)):
		logging.warning(Fore.RED+"I found a GuardDuty invitation for account %s in region %s from account %s ", fChildAccountId, GDinvites2[i]['Region'], GDinvites2[i]['AccountId']+Fore.RESET)
		ProcessStatus[Step]['IssuesFound']+=1
		ProcessStatus[Step]['Success']=False
		if fFixRun:
			for x in range(len(GDinvites2)):
				try:
					logging.warning("GuardDuty invite deletion commencing...")
					delresponse=Inventory_Modules.delete_gd_invites(account_credentials, region, GDinvites2[x]['AccountId'])
					ProcessStatus[Step]['IssuesFixed']+=1
					# We assume the process worked. We should probably NOT assume this.
				except ClientError as my_Error:
					print(my_Error)

	if ProcessStatus[Step]['Success']:
		print(ERASE_LINE+Fore.GREEN+"** {} completed with no issues".format(Step)+Fore.RESET)
	elif ProcessStatus[Step]['IssuesFound']-ProcessStatus[Step]['IssuesFixed']==0:
		print(ERASE_LINE+Fore.GREEN+"** {} found {} guardduty invites, but they were deleted".format(Step,ProcessStatus[Step]['IssuesFound'])+Fore.RESET)
		ProcessStatus[Step]['Success']=True
	elif (ProcessStatus[Step]['IssuesFound']>ProcessStatus[Step]['IssuesFixed']):
		print(ERASE_LINE+Fore.RED+"** {} completed, but there were {} guardduty invites found that couldn't be deleted".format(Step,ProcessStatus[Step]['IssuesFound']-ProcessStatus[Step]['IssuesFixed'])+Fore.RESET)
	else:
		print(ERASE_LINE+Fore.RED+"** {} completed with blockers found".format(Step)+Fore.RESET)
	print()
	"""

	# Step 4a
	# 4a. STS must be active in all regions. You can check from the Account Settings page in IAM.
	# TODO: We would have already verified this - since we've used STS to connect to each region already for the previous steps.
	# 	Except for the "quick" shortcut - which means we probably need to point that out in this section.

	# Step 5
	'''
	5. The account must be part of the Organization and the email address being entered into the CT parameters must match the account. 
		If you try to add an email from an account which is not part of the Org, you will get an error that you are not using a unique email address. If it’s part of the Org, CT just finds the account and uses the CFN roles.
	- If the existing account is to be imported as a Core Account, modify the manifest.yaml file to use it.
	- If the existing account will be a child account in the Organization, use the AVM launch template through Service Catalog and enter the appropriate configuration parameters.
	'''
	# try:
	Step = 'Step5'
	print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
	print(" Checking that the account is part of the AWS Organization.") if verbose < 50 else None
	if not (fChildAccountId in OrgAccountList):
		print() if verbose < 50 else None
		print(f"Account # {fChildAccountId} is not a part of the Organization. This account needs to be moved into the Organization to be adopted into Control Tower") if verbose < 50 else None
		print("This is easiest done manually right now.") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = False
		ProcessStatus[Step]['IssuesFound'] += 1
	else:
		print("Which it is - so ...") if verbose < 50 else None

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issue, but we were able to fix it{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed, but there was {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} blocker found that wasn't fixed{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	# Step 6
	# 6. The existing account can not be in any of the CT-managed Organizations OUs.
	# By default, these OUs are Core and Applications, but the customer may have chosen different or additional OUs to manage by CT.
	# TODO: This step should only be done once per Org, instead of per region...

	Step = 'Step6'
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f" Checking account {fChildAccountId} to make sure it's not already in a Control-Tower managed OU") if verbose < 50 else None
		# TODO: So we'll need to verify that the parent OU of the account is the root of the organization.
		print(" -- Not yet implemented because Control Tower doesn't list the OUs they manage vs. those they don't via an API -- ") if verbose < 50 else None
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success'] = False
	print() if verbose < 50 else None

	# Step 7 - Check for other resources which have 'controltower' in the name
	# Checking for SNS Topics
	Step = 'Step7'
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f" Checking account {fChildAccountId} for any SNS topics containing the 'controltower' string") if verbose < 50 else None
		SNSTopics2 = []
		logging.warning("Checking account %s in region %s for", fChildAccountId, f"{fRegion + Fore.RED} SNS Topics{Fore.RESET}")
		print(ERASE_LINE, f"Checking account {fChildAccountId} in region {fRegion} for SNS Topics", end='\r') if verbose < 50 else None
		SNSTopics = Inventory_Modules.find_sns_topics2(account_credentials, fRegion, ['controltower', 'ControlTower'])
		if len(SNSTopics) > 0:
			for x in range(len(SNSTopics)):
				logging.warning("SNS Topic: %s", str(SNSTopics[x]))
				logging.info("Unfortunately, we've found an SNS Topic  for account %s in the %s region, which means we'll have to delete it before this account can be adopted.", fChildAccountId, fRegion)
				ProcessStatus[Step]['Success'] = False
				ProcessStatus[Step]['IssuesFound'] += 1
				SNSTopics2.append({
					'AccountId': fChildAccountId,
					'TopicArn' : SNSTopics[x],
					'Region'   : fRegion
				})
				ProcessStatus[Step]['ProblemsFound'].extend(SNSTopics2)
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success'] = False

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issues, but we were able to remove the offending SNS Topics{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed, but there were {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} blockers found that wasn't fixed{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	# Step 8
	# Checking for Lambda functions
	Step = 'Step8'
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f" Checking account {fChildAccountId} for any Lambda functions containing the 'controltower' string") if verbose < 50 else None
		LambdaFunctions2 = []
		logging.warning(f"Checking account %s in region %s for {Fore.RED}Lambda functions{Fore.RESET}", fChildAccountId, fRegion)
		print(ERASE_LINE, f"Checking account {fChildAccountId} in region {fRegion} for Lambda Functions", end='\r') if verbose < 50 else None
		LambdaFunctions = Inventory_Modules.find_lambda_functions2(account_credentials, fRegion, ['controltower', 'ControlTower'])
		if len(LambdaFunctions) > 0:
			logging.info(f"Unfortunately, account {fChildAccountId} contains {len(LambdaFunctions)} functions with reserved names, which means we'll have to delete them before this account can be adopted.")
			for x in range(len(LambdaFunctions)):
				logging.warning(f"Found Lambda function {LambdaFunctions[x]['FunctionName']} in region {fRegion}")
				ProcessStatus[Step]['Success'] = False
				ProcessStatus[Step]['IssuesFound'] += 1
				LambdaFunctions2.append({
					'AccountId'   : fChildAccountId,
					'FunctionName': LambdaFunctions[x]['FunctionName'],
					'FunctionArn' : LambdaFunctions[x]['FunctionArn'],
					'Role'        : LambdaFunctions[x]['Role'],
					'Region'      : fRegion
				})
				ProcessStatus[Step]['ProblemsFound'].extend(LambdaFunctions2)
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success'] = False

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issues, but we were able to remove the offending Lambda Functions{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed, but there were {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} blockers found that wasn't fixed{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	# Step 9
	# Checking for Role names - unfortunately, this gets called for every region, even though the results will be the same in every region.
	# TODO: Need to find a way to only run this once, instead of for every region.
	Step = 'Step9'
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f" Checking account {fChildAccountId} for any Role names containing the 'controltower' string") if verbose < 50 else None
		RoleNames2 = []
		logging.warning(f"Checking account {Fore.RED}{fChildAccountId}{Fore.RESET} for Role names")
		RoleNames = Inventory_Modules.find_role_names2(account_credentials, 'us-east-1', ['controltower', 'ControlTower'])
		if len(RoleNames) > 0:
			logging.info(f"Unfortunately, account {fChildAccountId} contains {len(RoleNames)} roles with reserved names,"
			             f" which means we'll have to delete them before this account can be adopted.")
			for x in range(len(RoleNames)):
				logging.warning(f"Role Name: {str(RoleNames[x])}")
				ProcessStatus[Step]['Success'] = False
				ProcessStatus[Step]['IssuesFound'] += 1
				RoleNames2.append({
					'AccountId': fChildAccountId,
					'RoleName' : RoleNames[x]
				})
			ProcessStatus[Step]['ProblemsFound'].extend(RoleNames2)
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success'] = False

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issues, but we were able to remove the offending IAM roles{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed, but there were {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} blockers found that remain to be fixed{Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	# Step 10
	# 10. The existing account can not have any CloudWatch Log Groups named "controltower"
	# TODO: So we'll need to find and remove the CloudWatch Log Groups - if there are any.

	Step = 'Step10'
	try:
		print(f"{Fore.BLUE}{Step}:{Fore.RESET}") if verbose < 50 else None
		print(f"Checking account {fChildAccountId} to make sure there are no duplicate CloudWatch Log Groups") if verbose < 50 else None
		LogGroupNames2 = []
		logging.warning(f"Checking account {fChildAccountId} for {Fore.RED}duplicate CloudWatch Log Group names{Fore.RESET}")
		LogGroupNames = Inventory_Modules.find_cw_log_group_names2(account_credentials, fRegion, ['controltower', 'ControlTower'])
		if len(LogGroupNames) > 0:
			logging.info(f"Unfortunately, account {fChildAccountId} contains {len(LogGroupNames)} log groups with reserved names,"
			             f" which means we'll have to delete them before this account can be adopted.")
			for _ in range(len(LogGroupNames)):
				logging.warning(f"Log Group Name: {str(LogGroupNames[_])}")
				ProcessStatus[Step]['Success'] = False
				ProcessStatus[Step]['IssuesFound'] += 1
				LogGroupNames2.append({
					'AccountId'   : fChildAccountId,
					'LogGroupName': LogGroupNames[_]
				})
			ProcessStatus[Step]['ProblemsFound'].extend(LogGroupNames2)
	except ClientError as my_Error:
		print(my_Error)
		ProcessStatus[Step]['Success'] = False

	if ProcessStatus[Step]['Success']:
		print(f"{ERASE_LINE + Fore.GREEN}** {Step} completed with no issues{Fore.RESET}") if verbose < 50 else None
	elif ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed'] == 0:
		print(f"{ERASE_LINE}{Fore.GREEN}** {Step} found {ProcessStatus[Step]['IssuesFound']} issues, but we were able to remove the offending CW Log groups{Fore.RESET}") if verbose < 50 else None
		ProcessStatus[Step]['Success'] = True
	elif ProcessStatus[Step]['IssuesFound'] > ProcessStatus[Step]['IssuesFixed']:
		print(f"{ERASE_LINE}{Fore.RED}** {Step} completed, but there were {ProcessStatus[Step]['IssuesFound'] - ProcessStatus[Step]['IssuesFixed']} blockers found that remain to be fixed {Fore.RESET}") if verbose < 50 else None
	else:
		print(f"{ERASE_LINE + Fore.RED}** {Step} completed with blockers found{Fore.RESET}") if verbose < 50 else None
	print() if verbose < 50 else None

	""" Function Summary """
	TotalIssuesFound = 0
	TotalIssuesFixed = 0
	MemberReady = True
	for item in ProcessStatus:
		TotalIssuesFound = TotalIssuesFound + ProcessStatus[item]['IssuesFound']
		TotalIssuesFixed = TotalIssuesFixed + ProcessStatus[item]['IssuesFixed']
		MemberReady = MemberReady and ProcessStatus[item]['Success']

	ProcessStatus['AccountId'] = fChildAccountId
	ProcessStatus['Region'] = fRegion
	ProcessStatus['Ready'] = MemberReady
	ProcessStatus['IssuesFound'] = TotalIssuesFound
	ProcessStatus['IssuesFixed'] = TotalIssuesFixed
	return ProcessStatus


# The parameters passed to this function should be the dictionary of attributes that will be examined within the thread.
def DoThreadedAccountSteps(fChildAccountList, aws_account, fFixRun, fRegionList=None):
	"""
	Note that this function takes a list of account numbers and a list of regions and runs the CT_Checks within them
	"""

	class ThreadedAccountSteps(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_member_account, c_fixrun, c_region, c_PlaceCount = self.queue.get()
				logging.info(f"De-queued info for account {c_member_account} and region {c_region}")
				try:
					logging.info(f"Looking through {c_PlaceCount} of {len(fChildAccountList) * len(RegionList)} accounts in {RegionList} regions")
					SingleAccountandRegionResults = DoAccountSteps(c_member_account, aws_account, c_fixrun, c_region)
					logging.warning(f"Found {len(SingleAccountandRegionResults)} rows in Steps")
					AllOrgSteps.append(SingleAccountandRegionResults)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_member_account}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong")
					logging.warning(my_Error)
					continue
				except ClientError as my_Error:
					logging.error(f"Error: Likely throttling errors from too much activity")
					logging.warning(my_Error)
					continue
				finally:
					print(f"{ERASE_LINE}Finished looking through {c_member_account} in region {c_region} - {c_PlaceCount} / {len(fChildAccountList) * len(fRegionList)}", end='\r')
					self.queue.task_done()

	###########

	if fRegionList is None:
		fRegionList = ['us-east-1']
	checkqueue = Queue()

	AllOrgSteps = []
	PlaceCount = 1
	WorkerThreads = min(len(fChildAccountList) * len(fRegionList), 150)
	WorkerThreads = min(len(fChildAccountList) * len(fRegionList), 50)
	# WorkerThreads = 1

	for x in range(WorkerThreads):
		worker = ThreadedAccountSteps(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for member_account in fChildAccountList:
		print(f"Queuing data for {member_account} in each of the {len(fRegionList)} regions you specified...")
		for region in fRegionList:
			logging.debug(f"Beginning to queue data - starting with {member_account} and region {region}")
			try:
				# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
				checkqueue.put((member_account, fFixRun, region, PlaceCount))
				PlaceCount += 1
			except ClientError as my_Error:
				if "AuthFailure" in str(my_Error):
					logging.error(f"Authorization Failure accessing account {member_account} in {region} region")
					logging.warning(f"It's possible that the region {region} hasn't been opted-into")
					pass
	print(f"Threads are starting... Results coming in shortly... It takes around 1 second per account per region... ")
	checkqueue.join()
	return AllOrgSteps


def display_results():
	print()
	x = PrettyTable()
	y = PrettyTable()

	x.field_names = ['Account', '# of Regions', 'Issues Found', 'Issues Fixed', 'Ready?']
	y.field_names = ['Account', 'Region', 'Account Access', 'Org Config', 'Config', 'CloudTrail', 'GuardDuty', 'Org Member', 'CT OU', 'SNS Topics', 'Lambda', 'Roles', 'CW Log Groups', 'Ready?']
	for i in SummarizedOrgResults:
		x.add_row([SummarizedOrgResults[i]['AccountId'], len(SummarizedOrgResults[i]['Regions']), SummarizedOrgResults[i]['IssuesFound'], SummarizedOrgResults[i]['IssuesFixed'], SummarizedOrgResults[i]['Ready']])

	sorted_OrgResults = sorted(OrgResults, key=lambda k: (k['AccountId'], k['Region']))

	for i in sorted_OrgResults:
		if pSkipAccounts is not None and i['AccountId'] in pSkipAccounts:
			y.add_row([i['AccountId'], i['Region'],
			           'N/A', 'N/A', 'N/A', 'N/A',
			           'N/A', 'N/A', 'N/A', 'N/A',
			           'N/A', 'N/A', 'Skipped'])
		else:
			# x.add_row([i['AccountId'], i['Region'], i['IssuesFound'], i['IssuesFixed'], i['Ready']])
			y.add_row([
				i['AccountId'], i['Region'],
				i['Step0']['IssuesFound'] - i['Step0']['IssuesFixed'],
				i['Step1']['IssuesFound'] - i['Step1']['IssuesFixed'],
				i['Step2']['IssuesFound'] - i['Step2']['IssuesFixed'],
				i['Step3']['IssuesFound'] - i['Step3']['IssuesFixed'],
				i['Step4']['IssuesFound'] - i['Step4']['IssuesFixed'],
				i['Step5']['IssuesFound'] - i['Step5']['IssuesFixed'],
				i['Step6']['IssuesFound'] - i['Step6']['IssuesFixed'],
				i['Step7']['IssuesFound'] - i['Step7']['IssuesFixed'],
				i['Step8']['IssuesFound'] - i['Step8']['IssuesFixed'],
				i['Step9']['IssuesFound'] - i['Step9']['IssuesFixed'],
				i['Step10']['IssuesFound'] - i['Step10']['IssuesFixed'],
				i['Step0']['Success'] and i['Step1']['Success'] and i['Step2']['Success'] and
				i['Step3']['Success'] and i['Step4']['Success'] and i['Step5']['Success'] and
				i['Step6']['Success'] and i['Step7']['Success'] and i['Step8']['Success'] and
				i['Step9']['Success'] and i['Step10']['Success']
			])
	print("The following table represents the accounts looked at, and whether they are ready to be incorporated into a Control Tower environment.")
	print()
	if aws_acct.AccountType.lower() == 'root' and (pChildAccountList is None or aws_acct.acct_number in pChildAccountList):
		print(f"Please note that for the Org Root account {aws_acct.acct_number}, the number of issues found for 'Org Config' will mistakenly show as 1 per region, since these issues are checked on a per-region basis.")
		print(f"Additionally, issues found with 'Roles', though global, will show as regional as well. This will be remedied in future versions of this script.")
	print(x)
	print()
	print("The following table represents the accounts looked at, and gives details under each type of issue as to what might prevent a successful migration of this account into a Control Tower environment.")
	print(y)

	if verbose < 50:
		for account in OrgResults:
			print()
			FixesWorked = (account['IssuesFound'] - account['IssuesFixed'] == 0)
			if account['Ready'] and account['IssuesFound'] == 0:
				print(f"{Fore.GREEN}**** We've found NO issues that would hinder the adoption of account {account['AccountId']} ****{Fore.RESET}")
			elif account['Ready'] and FixesWorked:
				print(f"{Fore.GREEN}We've found and fixed{Fore.RED}", f"{account['IssuesFixed']}{Fore.RESET}", f"{Fore.GREEN}issues that would have otherwise blocked the adoption of account {account['AccountId']}{Fore.RESET}")
			else:
				print(f"{Fore.RED}Account # {account['AccountId']} has {account['IssuesFound'] - account['IssuesFixed']} issues that would hinder the adoption of this account{Fore.RESET}")
			for step in account:
				if step[:4] == 'Step' and len(account[step]['ProblemsFound']) > 0:
					print(f"{Fore.LIGHTRED_EX}Issues Found for {step} in account {account['AccountId']}:{Fore.RESET}")
					pprint(account[step]['ProblemsFound'])


def setup(fProfile, fRegions):

	f_aws_acct = aws_acct_access(fProfile)
	if not f_aws_acct.Success:
		logging.error(f"Error: {f_aws_acct.ErrorType}")
		print(f"{Fore.RED}\nThere was an error with profile {fProfile}. Unable to continue.\n{Fore.RESET}")
		sys.exit(9)

	if Quick:
		f_RegionList = ['us-east-1']
	else:
		# Control Tower now published its regions.
		GlobalRegionList = Inventory_Modules.get_service_regions('controltower', faws_acct=f_aws_acct)
		AllowedRegionList = Inventory_Modules.get_regions3(f_aws_acct, fRegions)
		f_RegionList = intersection(GlobalRegionList, AllowedRegionList)


	if pExplain:
		explain_script()
		sys.exit("Exiting after Script Explanation...")
	return f_aws_acct, f_RegionList


def CT_CheckAccount(faws_acct):
	logging.info(f"Confirming that this profile {pProfile} represents a Management Account")

	if faws_acct.AccountType.lower() == 'root' and pChildAccountList is None:
		# Creates a list of the account numbers in the Org.
		ChildAccountList = [d['AccountId'] for d in faws_acct.ChildAccounts]
		print(f"Since you didn't specify a specific account, we'll check all {len(faws_acct.ChildAccounts)} accounts in the Org.")
	elif aws_acct.AccountType.lower() == 'root' and pChildAccountList is not None:
		print(f"Account {faws_acct.acct_number} is a {faws_acct.AccountType} account.\n"
		      f"We're specifically checking to validate that account{'' if len(pChildAccountList) == 1 else 's'} {pChildAccountList} can be adopted into the Landing Zone")
		ChildAccountList = pChildAccountList
	else:
		sys.exit(f"Account {faws_acct.acct_number} is a {faws_acct.AccountType} account.\n"
		         f" This script should be run with Management Account credentials.")

	print()

	if pSkipAccounts is not None:
		for account_to_skip in pSkipAccounts:
			ChildAccountList.remove(account_to_skip)

	print(f"Beginning to evaluate the Org and Accounts to see if they're ready to deploy Control Tower")
	f_OrgResults = DoThreadedAccountSteps(ChildAccountList, faws_acct, FixRun, RegionList)

	if pSkipAccounts is not None:
		for MemberAccount in pSkipAccounts:
			f_OrgResults.append({'AccountId'  : MemberAccount, 'Region': 'None', 'IssuesFound': 'N/A',
			                   'IssuesFixed': 'N/A', 'Ready': 'Skipped'})

	####
	# Summary at the end
	####

	f_SummarizedOrgResults = summarizeOrgResults(f_OrgResults)

	return f_OrgResults, f_SummarizedOrgResults


###################
ExplainMessage = """

Objective: This script aims to identify issues and make it easier to "adopt" an existing account into a Control Tower environment.

0. The targeted account MUST allow the Management account access into the Child IAM role called "AWSControlTowerExecution" or another coded role, so that we have access to do read-only operations (by default).
0a. There must be an "AWSControlTowerExecution" role present in the account so that StackSets can assume it and deploy stack instances. This role must trust the Organizations Management account or at least the necessary Lambda functions.
** TODO ** - update the JSON to be able to update the role to ensure it trusts the least privileged roles from management account, instead of the whole account.
0b. STS must be active in all regions checked. You can check from the Account Settings page in IAM. Since we're using STS to connect to the account from the Management, this requirement is checked by successfully completing step 0.

1. We're using this step to check to see if your Org has Config Service enabled at the Org level.

2. There must be no active config channel and recorder in the account as “there can be only one” of each. 
	This must also be deleted via CLI, not console, switching config off in the console is NOT good enough and just disables it. To Delete the delivery channel and the configuration recorder (can be done via CLI and Python script only):
aws configservice describe-delivery-channels
aws configservice describe-delivery-channel-status
aws configservice describe-configuration-recorders
aws configservice stop-configuration-recorder --configuration-recorder-name <NAME-FROM-DESCRIBE-OUTPUT>
aws configservice delete-delivery-channel --delivery-channel-name <NAME-FROM-DESCRIBE-OUTPUT>
aws configservice delete-configuration-recorder --configuration-recorder-name <NAME-FROM-DESCRIBE-OUTPUT

3. The account must not have a Cloudtrail Trail name with 'ControlTower' in the name ("aws-controltower-BaselineCloudTrail")

4. The account must not have a pending guard duty invite. You can check from the Guard Duty Console

5. The account must be part of the Organization and the email address being entered into the CT parameters must match the account. 
	If you try to add an email from an account which is not part of the Org, you will get an error that you are not using a unique email address. If it’s part of the Org, CT just finds the account and uses the CFN roles.
** TODO ** - If the existing account will be a child account in the Organization, use the Account Factory and enter the appropriate email address.

6. The existing account can not be in any of the CT-managed Organizations OUs. By default, these OUs are Core and Applications, but the customer may have chosen different or additional OUs to manage by CT.
-- not yet implemented --

7. SNS topics name containing "ControlTower"
8. Lambda Functions name containing "ControlTower"
9. Role name containing "ControlTower"
Bucket created for AWS Config -- not yet implemented
SNS topic created for AWS Config -- not yet implemented
10. CloudWatch Log group containing "aws-controltower/CloudTrailLogs" -- not yet implemented --

"""

ERASE_LINE = '\x1b[2K'
begin_time = time()

if __name__ == '__main__':
	aws_acct, RegionList = setup(pProfile, pRegions)
	OrgResults, SummarizedOrgResults = CT_CheckAccount(aws_acct)
	display_results()

if pTiming:
	print(ERASE_LINE)
	print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
print("Thanks for using this script...")
print()
