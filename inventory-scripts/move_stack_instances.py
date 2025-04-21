#!/usr/bin/env python3

# import pprint
# import Inventory_Modules
import logging
import sys
from os import remove
from os.path import exists, split
from time import sleep, time
from datetime import datetime

from botocore.exceptions import ClientError, WaiterError
from colorama import Fore, Style, init

from ArgumentsClass import CommonArguments
from account_class import aws_acct_access

init()
__version__ = "2025.04.14"

"""
This script attempts to move stack-instances from one stack-set to another without any impact to the ultimate resources.
Here's what's needed:
		0. Either Create or be provided with the new stackset... 
	
	If we have to CREATE the NewStackSet:
		1. Determine the template body of the existing stackset. The body will need to be cleaned up, since the JSON is escaped all over.
		2. Determine the parameters from the existing stackset
			2.5 Determine whether you need to specify "--capabilities CAPABILITIES_NAMED_IAM" when creating the new stackset 
		3. Create a new stackset with the template body of the existing stackset.
	
	If NewStackSet is PROVIDED:
		1. Accept the parameters of the stackset name - assuming the template body and parameters have been applied already.  
		
	COMMON to both cases:
		4. Determine the stack-ids of the existing stack-instances you want to move from the existing stackset
	**** At this point it's important to write the recovery file, so you have the stack_ids saved, 
	before you begin removing them from the old stackset (during the import)
		5. Run the import to the new stackset, specifying the stack-ids of the existing stack-instances, no more than 10 at a time. 
			Ideally, you would aggregate accounts into a single run, so you could parallelize the regional deployments
		6. Verify that the operation returned a success for all stack-instances
		7. Loop through the stack-ids until complete - verifying after each one
			7.5 Remember the script will have to continuously poll the stack-set to determine when it's complete 
		8. Report on status at the end.
"""


##################
# Functions
##################
def parse_args(args):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.singleregion()
	parser.singleprofile()
	parser.confirm()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--old",
		dest="pOldStackSet",
		metavar="The name of the old stackset",
		help="This is the name of the old stackset, which manages the existing stack instances in the legacy accounts.")
	local.add_argument(
		"--new",
		dest="pNewStackSet",
		metavar="The name of the new stackset",
		help="This is the name of the new stackset, which will manage the existing stack instances going forward.")
	local.add_argument(
		"-A", "--Account",
		dest="pAccountsToMove",
		default=None,
		nargs='*',
		metavar="Account Numbers",
		help="The account(s) to be moved from one stackset to another")
	local.add_argument(
		"--Empty", "--empty",
		dest="pEmpty",
		action="store_true",
		help="Whether to simply create an empty (but copied) new stackset from the 'old' stackset")
	local.add_argument(
		"--recovery",
		dest="pRecoveryFlag",
		action="store_true",
		help="Whether we should use the recovery file.")
	local.add_argument(
		"--drift-check",
		dest="pDriftCheckFlag",
		action="store_true",
		help="Whether we should check for drift before moving instances")
	return parser.my_parser.parse_args(args)


def check_stack_set_drift_status(faws_acct: aws_acct_access, fStack_set_name: str, fOperation_id=None) -> dict:
	"""
	response = client.detect_stack_set_drift(
	StackSetName='string',
	OperationPreferences={
		'RegionConcurrencyType': 'SEQUENTIAL'|'PARALLEL',
		'RegionOrder': [
			'string',
		],
		'FailureToleranceCount': 123,
		'FailureTolerancePercentage': 123,
		'MaxConcurrentCount': 123,
		'MaxConcurrentPercentage': 123
	},
	OperationId='string',
	CallAs='SELF'|'DELEGATED_ADMIN'
	)
	"""

	import logging

	client_cfn = faws_acct.session.client('cloudformation')
	return_response = dict()
	Sync_Has_Started = False
	time_waited = 0
	if fOperation_id is None:
		# Do the initial stack_set_drift_detection
		try:
			response = client_cfn.detect_stack_set_drift(StackSetName=fStack_set_name,
			                                             OperationPreferences={
				                                             'RegionConcurrencyType'     : 'PARALLEL',
				                                             'FailureTolerancePercentage': 10,
				                                             'MaxConcurrentPercentage'   : 100
				                                             },
			                                             )
			fOperation_id = response['OperationId']
			return_response = {'OperationId': fOperation_id, 'Success': True}
		except client_cfn.exceptions.InvalidOperationException as myError:
			logging.error(f"There's been an error: {myError}")
			return_response = {'ErrorMessage': myError, 'Success': False}
		except client_cfn.exceptions.StackSetNotFoundException as myError:
			logging.error(f"There's been an error: {myError}")
			return_response = {'ErrorMessage': myError, 'Success': False}
		except client_cfn.exceptions.OperationInProgressException as myError:
			logging.error(f"There's a drift-detection process already running: {myError}")
			OperationId = myError.response['Error']['Message'][myError.response['Error']['Message'].rfind(":") + 2:]
			return_response = {'OperationId': OperationId, 'Success': True}
		return return_response
	else:
		# Do the describe_stack_set_operation with the operation_id, and determine how close we are to done...
		"""
		The response we're going to get from this "describe" operation looks like this:
		{
		"StackSetOperation": {
			"OperationId": "4e23045a-xxxx-xxxx-xxxx-bad01ed6902a",
			"StackSetId": "Test4-IOT6:735b8599-xxxx-xxxx-xxxx-7bc78fe8b817",
			"Action": "DETECT_DRIFT",
			"Status": "SUCCEEDED",
			"OperationPreferences": {
				"RegionConcurrencyType": "PARALLEL",
				"RegionOrder": [],
				"FailureTolerancePercentage": 10,
				"MaxConcurrentPercentage": 100
			},
			"AdministrationRoleARN": "arn:aws:iam::517713657778:role/AWSCloudFormationStackSetAdministrationRole",
			"ExecutionRoleName": "AWSCloudFormationStackSetExecutionRole",
			"CreationTimestamp": "2022-09-19T16:55:44.358000+00:00",
			"EndTimestamp": "2022-09-19T16:59:32.138000+00:00",
			"StackSetDriftDetectionDetails": {
				"DriftStatus": "IN_SYNC",
				"DriftDetectionStatus": "COMPLETED",
				"LastDriftCheckTimestamp": "2022-09-19T16:59:00.324000+00:00",
				"TotalStackInstancesCount": 39,
				"DriftedStackInstancesCount": 0,
				"InSyncStackInstancesCount": 39,
				"InProgressStackInstancesCount": 0,
				"FailedStackInstancesCount": 0
				}
			}
		}
		"""
		Finished = False
		while Finished is False:
			try:
				response = client_cfn.describe_stack_set_operation(
					StackSetName=fStack_set_name,
					OperationId=fOperation_id,
					)
				Start_Time = response['StackSetOperation']['CreationTimestamp']
				Operation_Status = response['StackSetOperation']['Status']
				if 'StackSetDriftDetectionDetails' in response['StackSetOperation'].keys():
					Drift_Detection_Status = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'DriftDetectionStatus']
					if 'LastDriftCheckTimestamp' in response['StackSetOperation'][
						'StackSetDriftDetectionDetails'].keys():
						Sync_Has_Started = True
					else:
						Sync_Has_Started = False
				if Operation_Status == 'RUNNING' and Sync_Has_Started:
					# TODO: Give a decent status, Wait a little longer, and try again
					Last_Instances_Finished = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'LastDriftCheckTimestamp']
					Check_Failed = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'FailedStackInstancesCount']
					Total_Stack_Instances = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'TotalStackInstancesCount']
					Drifted_Instances = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'DriftedStackInstancesCount']
					In_Sync_Instances = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'InSyncStackInstancesCount']
					Currently_Checking = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'InProgressStackInstancesCount']
					Time_Taken = Last_Instances_Finished - Start_Time
					Checked_Instances = In_Sync_Instances + Drifted_Instances + Check_Failed
					Time_Left = (Time_Taken / Checked_Instances) * Currently_Checking
					print(f"{ERASE_LINE} It's taken {Time_Taken} to detect on {Checked_Instances} "
					      f"instances, which means we probably have {Time_Left} left to go for {Currently_Checking} more stack instances",
					      end='\r')
					logging.info(f"{response}")
					return_response = {'OperationStatus'      : Operation_Status,
					                   'StartTime'            : Start_Time,
					                   'EndTime'              : None,
					                   'DriftedInstances'     : Drifted_Instances,
					                   'FailedInstances'      : Check_Failed,
					                   'StackInstancesChecked': Total_Stack_Instances,
					                   'Success'              : False,
					                   }
					Finished = False
				elif Operation_Status == 'RUNNING' and not Sync_Has_Started:
					# TODO: Give a decent status, Wait a little longer, and try again
					time_waited += sleep_interval
					print(
						f"{ERASE_LINE} We're still waiting for the Sync to start... Sleeping for {time_waited} seconds",
						end='\r')
					Finished = False
				elif Operation_Status == 'SUCCEEDED':
					End_Time = response['StackSetOperation']['EndTimestamp']
					Total_Stack_Instances = response['StackSetOperation']['StackSetDriftDetectionDetails'][
						'TotalStackInstancesCount']
					return_response.update({'OperationStatus'      : Operation_Status,
					                        'StartTime'            : Start_Time,
					                        'EndTime'              : End_Time,
					                        'StackInstancesChecked': Total_Stack_Instances,
					                        'Success'              : True})
					Finished = True
			except client_cfn.exceptions.StackSetNotFoundException as myError:
				logging.error(f"There's been an error: {myError}")
				return_response = {'ErrorMessage': myError, 'Success': False}
				Finished = True
			except client_cfn.exceptions.OperationNotFoundException as myError:
				logging.error(f"There's been an error: {myError}")
				return_response = {'ErrorMessage': myError, 'Success': False}
				Finished = True
			logging.info(f"Sleeping for {sleep_interval} seconds")
			sleep(sleep_interval)
		return return_response


def check_stack_set_status(faws_acct: aws_acct_access, fStack_set_name: str, fOperationId: str = None) -> dict:
	"""
	response = client.describe_stack_set_operation(
		StackSetName='string',
		OperationId='string',
		CallAs='SELF'|'DELEGATED_ADMIN'
	)
	"""
	import logging

	client_cfn = faws_acct.session.client('cloudformation')
	return_response = dict()
	# If the calling process couldn't supply the OpId, then we have to find it, based on the name of the stackset
	if fOperationId is None:
		# If there is no OperationId, they've called us after creating the stack-set itself,
		# so we need to check the status of the stack-set creation, and not the operations that happen to the stackset
		try:
			response = client_cfn.describe_stack_set(StackSetName=fStack_set_name,
			                                         CallAs='SELF')['StackSet']
			return_response['StackSetStatus'] = response['Status']
			return_response['Success'] = True
			logging.info(f"Stackset: {fStack_set_name} | Status: {return_response['StackSetStatus']}")
			return return_response
		except client_cfn.exceptions.StackSetNotFoundException as myError:
			logging.error(f"Stack Set {fStack_set_name} Not Found: {myError}")
			return_response['Success'] = False
			return return_response
	try:
		response = client_cfn.describe_stack_set_operation(StackSetName=fStack_set_name,
		                                                   OperationId=fOperationId,
		                                                   CallAs='SELF')['StackSetOperation']
		return_response['StackSetStatus'] = response['Status']
		return_response['Success'] = True
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		print(f"StackSet Not Found: {myError}")
		return_response['Success'] = False
	except client_cfn.exceptions.OperationNotFoundException as myError:
		print(f"Operation Not Found: {myError}")
		return_response['Success'] = False
	return return_response


def find_if_stack_set_exists(faws_acct: aws_acct_access, fStack_set_name: str) -> dict:
	"""
	response = client.describe_stack_set(
		StackSetName='string',
		CallAs='SELF'|'DELEGATED_ADMIN'
	)
	"""
	import logging

	logging.info(f"Verifying whether the stackset {fStack_set_name} in account {faws_acct.acct_number} exists")
	client_cfn = faws_acct.session.client('cloudformation')
	return_response = dict()
	try:
		response = client_cfn.describe_stack_set(StackSetName=fStack_set_name, CallAs='SELF')['StackSet']
		return_response = {'Payload': response, 'Success': True}
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		logging.info(f"StackSet {fStack_set_name} not found in this account.")
		logging.debug(f"{myError}")
		return_response['Success'] = False
	return return_response


def get_template_body_and_parameters(faws_acct: aws_acct_access, fExisting_stack_set_name: str) -> dict:
	"""
	@param faws_acct: object
	@param fExisting_stack_set_name: The existing stackset name
	@return: return_response:
		'stack_set_info' = stack_set_info
		'Success' = True | False

	describe_stack_set output:
	{
		"StackSet": {
			"StackSetName": "AWS-Landing-Zone-Baseline-DemoRoles",
			"StackSetId": "AWS-Landing-Zone-Baseline-DemoRoles:872bab58-25b9-4785-8973-e7920cbe46d3",
			"Status": "ACTIVE",
			"TemplateBody":
				"AWSTemplateFormatVersion: "2010-09-09"
				"Description": Sample of a new role with the use of a managed policy, and a parameterized trust policy.
					Parameters:
						AdministratorAccountId:
							Type: String
							Default: "287201118218"
							Description: AWS Account Id of the administrator account.
							Resources:
								SampleRole:
									Type: "AWS::IAM::Role"
									Properties:
										RoleName: DemoRole
										Path: /
										AssumeRolePolicyDocument:
										Version: "2012-10-17"
										Statement:
											- Effect: "Allow"
												Principal:
													AWS:
														- !Sub 'arn:aws:iam::${AdministratorAccountId}:role/Owner'
														- !Sub 'arn:aws:iam::${AdministratorAccountId}:user/Paul'
											  Action:
												- "sts:AssumeRole"
										ManagedPolicyArns:
											- arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
			"Parameters": [
				{
					"ParameterKey": "AdministratorAccountId",
					"ParameterValue": "517713657778",
					"UsePreviousValue": false
				}
			],
			"Capabilities": [
				"CAPABILITY_NAMED_IAM"
			],
			"Tags": [
				{
					"Key": "AWS_Solutions",
					"Value": "LandingZoneStackSet"
				}
			],
			"StackSetARN": "arn:aws:cloudformation:us-east-1:517713657778:stackset/AWS-Landing-Zone-Baseline-DemoRoles:872bab58-25b9-4785-8973-e7920cbe46d3",
			"AdministrationRoleARN": "arn:aws:iam::517713657778:role/AWSCloudFormationStackSetAdministrationRole",
			"ExecutionRoleName": "AWSCloudFormationStackSetExecutionRole",
			"StackSetDriftDetectionDetails": {
				"DriftStatus": "NOT_CHECKED",
				"TotalStackInstancesCount": 0,
				"DriftedStackInstancesCount": 0,
				"InSyncStackInstancesCount": 0,
				"InProgressStackInstancesCount": 0,
				"FailedStackInstancesCount": 0
			},
			"OrganizationalUnitIds": []
		}
	}
	"""
	import logging

	logging.info(f"Connecting to account {faws_acct.acct_number} to get info about stackset {fExisting_stack_set_name}")
	client_cfn = faws_acct.session.client('cloudformation')
	return_response = {'Success': False}
	try:
		stack_set_info = client_cfn.describe_stack_set(StackSetName=fExisting_stack_set_name)['StackSet']
		return_response['stack_set_info'] = stack_set_info
		return_response['Success'] = True
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		ErrorMessage = f"{fExisting_stack_set_name} doesn't seem to exist. Please check the spelling"
		print(f"{ErrorMessage}: {myError}")
		return_response['Success'] = False
	return return_response


def compare_stacksets(faws_acct: aws_acct_access, fExisting_stack_set_name: str, fNew_stack_set_name: str) -> dict:
	"""
	The idea here is to compare the templates and parameters of the stacksets, to ensure that the import will succeed.
	"""

	return_response = {'Success'                : False,
	                   'TemplateComparison'     : False,
	                   'CapabilitiesComparison' : False,
	                   'ParametersComparison'   : False,
	                   'TagsComparison'         : False,
	                   'DescriptionComparison'  : False,
	                   'ExecutionRoleComparison': False}
	Stack_Set_Info_old = get_template_body_and_parameters(faws_acct, fExisting_stack_set_name)
	Stack_Set_Info_new = get_template_body_and_parameters(faws_acct, fNew_stack_set_name)
	# Time to compare - only the Template Body, Parameters, and Capabilities are critical to making sure the stackset works.
	return_response['TemplateComparison'] = (
			Stack_Set_Info_old['stack_set_info']['TemplateBody'] == Stack_Set_Info_new['stack_set_info'][
		'TemplateBody'])
	return_response['CapabilitiesComparison'] = (
			Stack_Set_Info_old['stack_set_info']['Capabilities'] == Stack_Set_Info_new['stack_set_info'][
		'Capabilities'])
	return_response['ParametersComparison'] = (
			Stack_Set_Info_old['stack_set_info']['Parameters'] == Stack_Set_Info_new['stack_set_info'][
		'Parameters'])
	return_response['TagsComparison'] = (
			Stack_Set_Info_old['stack_set_info']['Tags'] == Stack_Set_Info_new['stack_set_info']['Tags'])
	try:
		return_response['DescriptionComparison'] = (
				Stack_Set_Info_old['stack_set_info']['Description'] == Stack_Set_Info_new['stack_set_info'][
			'Description'])
	except KeyError as myError:
		# This checks for the presence of the Description key before using it as a key for checking, to resolve an error when it's not there.
		if 'Description' in Stack_Set_Info_new['stack_set_info'].keys() and Stack_Set_Info_new['stack_set_info'][
			'Description'] == Default_Description_Text:
			print(
				f"There was no description in the old StackSet, and creating a new one in this way requires one, so we've populated it with a default Description -- '{Default_Description_Text}'\n"
				f"This won't cause a problem with the migration, just something to note...")
			return_response['DescriptionComparison'] = True
		else:
			logging.error(f"Description key isn't available... continuing anyway...")
			return_response['DescriptionComparison'] = True
	return_response['ExecutionRoleComparison'] = (
			Stack_Set_Info_old['stack_set_info']['ExecutionRoleName'] == Stack_Set_Info_new['stack_set_info'][
		'ExecutionRoleName'])

	if (return_response['TemplateComparison'] and return_response['CapabilitiesComparison'] and return_response[
		'ParametersComparison']):
		return_response['Success'] = True
	return return_response


def get_stack_ids_from_existing_stack_set(faws_acct: aws_acct_access, fExisting_stack_set_name: str,
                                          fAccountsToMove: list = None) -> dict:
	"""
	response = client.list_stack_instances(
		StackSetName='string',
		NextToken='string',
		MaxResults=123,
		Filters=[
			{
				'Name': 'DETAILED_STATUS',
				'Values': 'string'
			},
		],
		StackInstanceAccount='string',
		StackInstanceRegion='string',
		CallAs='SELF'|'DELEGATED_ADMIN'
	)
	"""
	import logging

	client_cfn = faws_acct.session.client('cloudformation')
	return_response = dict()
	try:
		response = client_cfn.list_stack_instances(StackSetName=fExisting_stack_set_name, CallAs='SELF')
		return_response['Stack_instances'] = response['Summaries']
		while 'NextToken' in response.keys():
			response = client_cfn.list_stack_instances(StackSetName=fExisting_stack_set_name, CallAs='SELF',
			                                           NextToken=response['NextToken'])
			return_response['Stack_instances'].extend(response['Summaries'])
		return_response['Success'] = True
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		print(myError)
		return_response['Success'] = False
	if fAccountsToMove is None:
		logging.debug(f"No Account was specified, so all stack-instance-ids are being returned")
		pass
	else:
		# TODO: Replace this below with a "filter(lambda)" syntax
		return_response['Stack_instances'] = [stacksetinfo for stacksetinfo in return_response['Stack_instances'] if
		                                      stacksetinfo['Account'] in fAccountsToMove]
		logging.debug(f"Account {fAccountsToMove} was specified, so only the {len(return_response['Stack_instances'])} "
		              f"stack-instance-ids matching th{'ose accounts' if len(fAccountsToMove) == 1 else 'at account'} are being returned")
	return return_response


def write_info_to_file(faws_acct: aws_acct_access, fstack_ids) -> dict:
	"""
	Docs go here
	"""
	import logging
	import simplejson as json

	# Create a dictionary that will represent everything we're trying to do
	try:
		StackSetsInfo = {
			'ProfileUsed'      : pProfile,
			'ManagementAccount': faws_acct.MgmtAccount,
			'Region'           : pRegion,
			'AccountNumber'    : faws_acct.acct_number,
			'AccountsToMove'   : pAccountsToMove,
			'OldStackSetName'  : pOldStackSet,
			'NewStackSetName'  : pNewStackSet,
			'stack_ids'        : fstack_ids
			}
		logging.info(f"Writing data to the file {InfoFilename}")
		logging.debug(f"Here's the data we're writing: {StackSetsInfo}")
		file_data = json.dumps(StackSetsInfo, sort_keys=True, indent=4 * ' ', default=str)
		with open(InfoFilename, 'w', encoding="utf-8") as out:
			print(file_data, file=out)
		return_response = {'Success': True}
		return return_response
	except Exception as myError:
		error_message = "There was a problem. Not sure... "
		logging.error(error_message)
		return_response = {'Success': False, 'ErrorMessage': myError}
		return return_response


def read_stack_info_from_file() -> dict:
	"""
	Docs go here
	"""
	import logging
	import simplejson as json

	try:
		with open(InfoFilename, 'r', encoding="utf-8") as input_file:
			my_input_file = json.load(input_file)
		return_response = {'Success': True, 'Payload': my_input_file}
		return return_response
	except Exception as myError:
		error_message = "There was a problem. Not sure... "
		logging.error(error_message)
		return_response = {'Success': False, 'ErrorMessage': myError}
		return return_response


def create_stack_set_with_body_and_parameters(faws_acct: aws_acct_access, fNew_stack_set_name: str,
                                              fStack_set_info: dict) -> dict:
	"""
	response = client.create_stack_set(
		StackSetName='string',
		Description='string',
		TemplateBody='string',
		TemplateURL='string',
		StackId='string',
		Parameters=[
			{
				'ParameterKey': 'string',
				'ParameterValue': 'string',
				'UsePreviousValue': True|False,
				'ResolvedValue': 'string'
			},
		],
		Capabilities=[
			'CAPABILITY_IAM'|'CAPABILITY_NAMED_IAM'|'CAPABILITY_AUTO_EXPAND',
		],
		Tags=[
			{
				'Key': 'string',
				'Value': 'string'
			},
		],
		AdministrationRoleARN='string',
		ExecutionRoleName='string',
		PermissionModel='SERVICE_MANAGED'|'SELF_MANAGED',
		AutoDeployment={
			'Enabled': True|False,
			'RetainStacksOnAccountRemoval': True|False
		},
		CallAs='SELF'|'DELEGATED_ADMIN',
		ClientRequestToken='string'
	)
	"""
	import logging

	logging.info(
		f"Creating a new stackset name {fNew_stack_set_name} in account {faws_acct.acct_number} with a template body, parameters, capabilities and tagging from this:")
	logging.info(f"{fStack_set_info}")
	client_cfn = faws_acct.session.client('cloudformation')
	return_response = dict()
	# TODO: We should consider changing the template body to a template url to accommodate really big templates,
	#  That would mean we need to have an S3 bucket to put the template, which we don't necessarily have at this point, so it's a bigger deal than you might immediately think.
	#  However, this script doesn't check the size of the template ahead of time, so what happens if we try to create a new stackset template when the old one is too big?

	# TODO: This only creates a new stackset as a "Self-Managed" stackset.
	#  We need to catch the scenario, when the old stackset was "Service-Managed" and decide whether we create the new one that way (which may be difficult, with automatic deployments, etc),
	#  Or tell the user that we cannot create a new service-managed stackset, and do they want to create it as a self-managed instead?
	try:
		response = client_cfn.create_stack_set(StackSetName=fNew_stack_set_name,
		                                       TemplateBody=fStack_set_info['TemplateBody'],
		                                       Description=fStack_set_info[
			                                       'Description'] if 'Description' in fStack_set_info.keys() else Default_Description_Text,
		                                       Parameters=fStack_set_info['Parameters'],
		                                       Capabilities=fStack_set_info['Capabilities'],
		                                       Tags=fStack_set_info['Tags'])
		return_response['StackSetId'] = response['StackSetId']
		return_response['Success'] = True
	# There is currently no waiter to use for this operation...
	except (client_cfn.exceptions.NameAlreadyExistsException,
	        client_cfn.exceptions.CreatedButModifiedException,
	        client_cfn.exceptions.LimitExceededException) as myError:
		logging.error(f"Operation Failed: {myError}")
		return_response['Success'] = False
		return_response['Error_Message'] = myError.response['Error']['Message']
	return return_response


def disconnect_stack_instances(faws_acct: aws_acct_access, fStack_instances: dict, fOldStackSet: str) -> dict:
	"""
	response = client.delete_stack_instances(
		StackSetName='string',
		Accounts=[
			'string',
		],
		DeploymentTargets={
			'Accounts': [
				'string',
			],
			'AccountsUrl': 'string',
			'OrganizationalUnitIds': [
				'string',
			]
		},
		Regions=[
			'string',
		],
		OperationPreferences={
			'RegionConcurrencyType': 'SEQUENTIAL'|'PARALLEL',
			'RegionOrder': [
				'string',
			],
			'FailureToleranceCount': 123,
			'FailureTolerancePercentage': 123,
			'MaxConcurrentCount': 123,
			'MaxConcurrentPercentage': 123
		},
		RetainStacks=True|False,
		OperationId='string',
		CallAs='SELF'|'DELEGATED_ADMIN'
	)

	"""
	import logging

	logging.info(f"Disassociating stacks from {fOldStackSet}")
	return_response = dict()
	if len(fStack_instances['Stack_instances']) == 0:
		return_response = {'Success'     : False,
		                   'ErrorMessage': f"Stackset {fOldStackSet} has no matching instances",
		                   'OperationId' : None}
		return return_response
	client_cfn = faws_acct.session.client('cloudformation')
	regions = set()
	accounts = set()
	for item in fStack_instances['Stack_instances']:
		regions.add(item['Region'])
		accounts.add(item['Account'])
	try:
		response = client_cfn.delete_stack_instances(
			StackSetName=fOldStackSet,
			Accounts=list(accounts),
			Regions=list(regions),
			OperationPreferences={
				'RegionConcurrencyType'     : 'PARALLEL',
				'FailureTolerancePercentage': 10,
				'MaxConcurrentPercentage'   : 100},
			RetainStacks=True,
			CallAs='SELF')
		return_response['OperationId'] = response['OperationId']
		return_response['Success'] = True
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		logging.error(f"Operation Failed: {myError}")
		return_response['Success'] = False
	except client_cfn.exceptions.OperationInProgressException as myError:
		logging.error(f"Operation Failed: {myError}")
		return_response['Success'] = False
	except client_cfn.exceptions.OperationIdAlreadyExistsException as myError:
		logging.error(f"Operation Failed: {myError}")
		return_response['Success'] = False
	except client_cfn.exceptions.StaleRequestException as myError:
		logging.error(f"Operation Failed: {myError}")
		return_response['Success'] = False
	except client_cfn.exceptions.InvalidOperationException as myError:
		logging.error(f"Operation Failed: {myError}")
		return_response['Success'] = False
	stack_instance_operation_waiter = client_cfn.get_waiter('stack_delete_complete')
	try:
		stack_instance_operation_waiter.wait(StackName=fOldStackSet)
		return_response['Success'] = True
	except WaiterError as myError:
		if "Max attempts exceeded" in myError:
			logging.error(f"Import didn't complete within 600 seconds")
		logging.error(myError)
		return_response['Success'] = False
	return return_response


def create_change_set_for_new_stack():
	"""
	Do we need to do this?
	"""


def populate_new_stack_with_existing_stack_instances(faws_acct: aws_acct_access, fStack_instance_info: list,
                                                     fNew_stack_name: str) -> dict:
	"""
	response = client.import_stacks_to_stack_set(
		StackSetName='string',
		StackIds=[
			'string',
		],
		OperationPreferences={
			'RegionConcurrencyType': 'SEQUENTIAL'|'PARALLEL',
			'RegionOrder': [
				'string',
			],
			'FailureToleranceCount': 123,
			'FailureTolerancePercentage': 123,
			'MaxConcurrentCount': 123,
			'MaxConcurrentPercentage': 123
		},
		OperationId='string',
		CallAs='SELF'|'DELEGATED_ADMIN'
	)

	The Operation Id as the response is really important, because that's how we determine whether teh operation is done (or a success),
	so that we can add 10 more stacks... This can take a long time for a lot of instances...
	"""
	import logging

	stack_instance_ids = [stack_instance['StackId'] for stack_instance in fStack_instance_info
	                      if stack_instance['Status'] in ['CURRENT', 'OUTDATED', 'CREATE_COMPLETE', 'UPDATE_COMPLETE']]
	logging.info(
		f"Populating new stackset {fNew_stack_name} in account {faws_acct.acct_number} with stack_ids: {stack_instance_ids}")
	client_cfn = faws_acct.session.client('cloudformation')
	return_response = dict()
	try:
		response = client_cfn.import_stacks_to_stack_set(StackSetName=fNew_stack_name,
		                                                 StackIds=stack_instance_ids,
		                                                 OperationPreferences={
			                                                 'RegionConcurrencyType'     : 'PARALLEL',
			                                                 'FailureTolerancePercentage': 0,
			                                                 'MaxConcurrentPercentage'   : 100},
		                                                 CallAs='SELF')
		return_response['OperationId'] = response['OperationId']
		return_response['Success'] = True
	except client_cfn.exceptions.LimitExceededException as myError:
		logging.error(f"Limit Exceeded: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		logging.error(f"Stack Set Not Found: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except client_cfn.exceptions.InvalidOperationException as myError:
		logging.error(f"Invalid Operation: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except client_cfn.exceptions.OperationInProgressException as myError:
		logging.error(f"Operation is already in progress: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except client_cfn.exceptions.StackNotFoundException as myError:
		logging.error(f"Stack Not Found: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except client_cfn.exceptions.StaleRequestException as myError:
		logging.error(f"Stale Request: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except ClientError as myError:
		logging.error(f"Client Error: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	return return_response


##################
# Main
##################
if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfile = args.Profile
	pRegion = args.Region
	pForce = args.Confirm
	pTiming = args.Time
	verbose = args.loglevel
	pRecoveryFlag = args.pRecoveryFlag
	pDriftCheck = args.pDriftCheckFlag
	# version = args.Version
	pOldStackSet = args.pOldStackSet
	pNewStackSet = args.pNewStackSet
	pAccountsToMove = args.pAccountsToMove
	pEmpty = args.pEmpty
	# Logging Settings
	# Set Log Level
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	ERASE_LINE = '\x1b[2K'
	# The time between checks to see if the stackset instances have been created, or imported...
	sleep_interval = 5
	begin_time = time()
	Default_Description_Text = "This is a default description"
	# Currently, this is a hard-stop at 10, but I made it a variable in case they up the limit
	StackInstancesImportedAtOnce = 10
	stack_ids = dict()

	aws_acct = aws_acct_access(pProfile)
	datetime_extension = datetime.now().strftime("%Y%m%d-%H%M")
	InfoFilename = f"{pOldStackSet}-{pNewStackSet}-{aws_acct.acct_number}-{pRegion}.{datetime_extension}"
	Use_recovery_file = False

	if pDriftCheck:
		drift_check_response = check_stack_set_drift_status(aws_acct, pOldStackSet)
		print(drift_check_response)
		print(f"Kicked off Drift Sync... now we'll wait {sleep_interval} seconds before checking on the process...")
		sleep(sleep_interval)
		if drift_check_response['Success']:
			drift_check_response2 = check_stack_set_drift_status(aws_acct, pOldStackSet,
			                                                     drift_check_response['OperationId'])
			Total_Stacksets = drift_check_response2['StackInstancesChecked']
			Drifted_Stacksets = drift_check_response2[
				'DriftedInstances'] if 'DriftedInstances' in drift_check_response2.keys() else None
			Failed_Stacksets = drift_check_response2['FailedInstances']
			Duration = drift_check_response2['EndTime'] - drift_check_response2['StartTime']
			print()
			print(f"We're done checking the drift status of the old StackSet\n"
			      f"We found {Total_Stacksets} Total Stacksets\n"
			      f"{Drifted_Stacksets} have drifted, while\n"
			      f"{Failed_Stacksets} failed to be checked\n"
			      f"This process took {Duration} seconds to run")
			logging.info(drift_check_response2)
			print()
		sys.exit("Exiting...")

	if exists(InfoFilename) and pRecoveryFlag:
		print(
			f"You requested to use the recovery file {InfoFilename}, so we'll use that to pick up from where we left off")
		Use_recovery_file = True
	elif pRecoveryFlag:
		print(
			f"You requested to use the Recovery file, but we couldn't find one named {InfoFilename}, so we're exiting\n"
			f"Please supply the proper StackSet, Region and Profile parameters so we can find the recovery file.",
			file=sys.stderr)
		sys.exit(5)
	elif exists(InfoFilename):
		print(f"There exists a recovery file for the parameters you've supplied, named {InfoFilename}\n")
		Use_recovery_file = (input(f"Do you want to use this file? (y/n): ") in ['y', 'Y'])
		if not Use_recovery_file:
			print(
				f"If you don't want to use that file, please change the filename, and re-run this script, to avoid over-writing it.",
				file=sys.stderr)
			sys.exit(6)

	if Use_recovery_file:
		fileinput = read_stack_info_from_file()
		AccountNumber = fileinput['Payload']['AccountNumber']
		if not AccountNumber == aws_acct.acct_number:
			print(
				f"You're running this script referencing a different account than the one used last when the recovery file {InfoFilename} was created.\n"
				f"Please make sure you finish that last task before starting a new one.\n", file=sys.stderr)
			sys.exit(4)
		pAccountsToMove = fileinput['Payload']['AccountsToMove']
		pOldStackSet = fileinput['Payload']['OldStackSetName']
		pNewStackSet = fileinput['Payload']['NewStackSetName']
		pRegion = fileinput['Payload']['Region']
		stack_ids = fileinput['Payload']['stack_ids']

	# The following is just letting the user know what we're going to do in this script.
	# Since this script is by nature intrusive, we want the user to confirm everything before they continue.
	if pAccountsToMove is None:
		logging.info(f"Successfully connected to account {aws_acct.acct_number} to move stack instances "
		             f"from {pOldStackSet} to {pNewStackSet}")
	else:
		logging.info(f"Connecting to account {aws_acct.acct_number} to move instances for accounts {pAccountsToMove}"
		             f" from {pOldStackSet} to {pNewStackSet}")
	# Check to see if the new StackSet already exists, or we need to create it.
	if find_if_stack_set_exists(aws_acct, pNewStackSet)['Success']:
		print(
			f"{Fore.GREEN}The 'New' Stackset {pNewStackSet} exists within the account {aws_acct.acct_number}{Fore.RESET}")
		NewStackSetExists = True
	else:
		print(
			f"{Fore.RED}The 'New' Stackset {pNewStackSet} does not exist within the account {aws_acct.acct_number}{Fore.RESET}")
		NewStackSetExists = False
	# Check to see if the old StackSet exists, as they may have typed something wrong - or the recovery file was never deleted.
	if find_if_stack_set_exists(aws_acct, pOldStackSet)['Success']:
		print(
			f"{Fore.GREEN}The 'Old' Stackset {pOldStackSet} exists within the account {aws_acct.acct_number}{Fore.RESET}")
		OldStackSetExists = True
	else:
		print(
			f"{Fore.RED}The 'Old' Stackset {pOldStackSet} does not exist within the account {aws_acct.acct_number}{Fore.RESET}")
		OldStackSetExists = False

	CompareTemplates = {'Success': False}
	if OldStackSetExists and NewStackSetExists:
		CompareTemplates = compare_stacksets(aws_acct, pOldStackSet, pNewStackSet)
	if OldStackSetExists and not NewStackSetExists:
		print()
		print(f"It looks like the new stack-set doesn't yet have a template assigned to it.\n"
		      f"We can simply copy over the template from the source stackset and copy to the new stackset.\n"
		      f"Please answer Y to the prompt below, if you're ok with that.")
		print()
	elif not CompareTemplates['Success']:
		print()
		print(
			f"{Fore.RED}Ok - there's a problem here. The templates or parameters or capabilities in the two stacksets you provided don't match{Fore.RESET}\n"
			f"It might be a very bad idea to try to import these stacksets, if the templates or other critical components don't match.\n"
			f"I'd suggest strongly that you answer 'N' to the next prompt... ")
		print()
	elif (CompareTemplates['Success'] and
	      not (CompareTemplates['TagsComparison']
	           and CompareTemplates['DescriptionComparison']
	           and CompareTemplates['ExecutionRoleComparison'])):
		print()
		print(
			f"{Fore.CYAN}Ok - there {Style.BRIGHT}might{Style.NORMAL} be a problem here. While the templates, parameters and capabilities in the two stacksets you provided match\n"
			f"Either the Description, the Tags, or the ExecutionRole is different between the two stacksets.\n"
			f"I'd suggest that you answer 'N' to the next prompt, and then investigate the differences\n"
			f"No changes were made yet - so you can always run this script again.{Fore.RESET}")
		print()

	# Ignore whether or not the recovery file exists, since if it does - it's just updating the variables needed for this run.
	# We shouldn't be doing much of anything differently, based on whether the recovery file exists.
	if OldStackSetExists and pEmpty:
		print(
			f"You've asked to create an empty stackset called {pNewStackSet} from the existing stackset {pOldStackSet}")
		print(
			f"You specified accounts to move, but we're not doing that, since you asked for this stackset to be created empty.") if pAccountsToMove is not None else ""
		""" Create new stackset from old stackset """
		Stack_Set_Info = get_template_body_and_parameters(aws_acct, pOldStackSet)
		# Creates the new stack
		NewStackSetId = create_stack_set_with_body_and_parameters(aws_acct, pNewStackSet,
		                                                          Stack_Set_Info['stack_set_info'])
		logging.warning(f"Waiting for new stackset {pNewStackSet} to be created")
		sleep(sleep_interval)
		# Checks on the new stack creation
		NewStackSetStatus = check_stack_set_status(aws_acct, pNewStackSet)
		intervals_waited = 1
		# If the creation effort (async) and the creation checking both succeeded...
		if NewStackSetStatus['Success'] and NewStackSetId['Success']:
			# TODO: Fix message about length of time waiting...
			while NewStackSetStatus['Success'] and not NewStackSetStatus['StackSetStatus'] in ['ACTIVE']:
				print(f"Waiting for StackSet {pNewStackSet} to be ready." * intervals_waited, end='\r')
				sleep(sleep_interval)
				intervals_waited += 1
				NewStackSetStatus = check_stack_set_status(aws_acct, pNewStackSet)
			print(f"{ERASE_LINE}Stackset {pNewStackSet} has been successfully created")
			# TODO: Use the NewStackSetId Operation Id, to check if the empty new stackset has successfully been created
			pass
		# If only the creation effort (async) succeeded, but checking on that operation showed a failure...
		elif NewStackSetStatus['Success']:
			print(
				f"{Fore.RED}{pNewStackSet} appears to already exist. New stack set failed to be created. Exiting...{Fore.RESET}")
			Failure_GoToEnd = True
			sys.exit(98)
		# Any other failure scenario
		else:
			print(f"{pNewStackSet} failed to be created. Exiting...")
			Failure_GoToEnd = True
			sys.exit(99)

	elif OldStackSetExists and not pEmpty:
		print()
		if not pForce:  # Checking to see if they've specified no confirmations
			User_Confirmation = (input(f"Do you want to proceed with the migration? (y/n): ") in ['y', 'Y'])
		else:
			User_Confirmation = True
		if not User_Confirmation:
			print(f"User cancelled script", file=sys.stderr)
			Failure_GoToEnd = True
			sys.exit(10)
		# We would only get to this point if (for some reason) the script dies before a new stackset could be made.
		# In that case, we may not have even written a recovery file yet.
		if not NewStackSetExists:  # We need to create the new stacksets
			"""
			1. Determine the template body of the existing stackset.
			2. Determine the parameters from the existing stackset
				2.5 Determine whether you need to specify "--capabilities CAPABILITIES_NAMED_IAM" when creating the new stackset 
			3. Create a new stackset with the template body of the existing stackset.
			"""
			print()
			print(f"You've asked for us to move stacksets from the existing stackset {pOldStackSet}"
			      f" and create a new stackset called: {pNewStackSet}\n"
			      f"Please note that we can only move {StackInstancesImportedAtOnce} stack instances at a time, so we may to loop a few times to do this.")
			if pAccountsToMove is not None:
				print(f"But only for account {pAccountsToMove}")
			print()
			Stack_Set_Info = get_template_body_and_parameters(aws_acct, pOldStackSet)
			NewStackSetId = create_stack_set_with_body_and_parameters(aws_acct, pNewStackSet,
			                                                          Stack_Set_Info['stack_set_info'])
			logging.warning(f"Waiting for new stackset {pNewStackSet} to be created")
			sleep(sleep_interval)
			NewStackSetStatus = check_stack_set_status(aws_acct, pNewStackSet)
			intervals_waited = 1
			if NewStackSetStatus['Success']:
				while NewStackSetStatus['Success'] and not NewStackSetStatus['StackSetStatus'] in ['ACTIVE']:
					print(f"Waiting for StackSet {pNewStackSet} to be ready", f"." * intervals_waited, end='\r')
					sleep(sleep_interval)
					intervals_waited += 1
					NewStackSetStatus = check_stack_set_status(aws_acct, pNewStackSet)
				print(f"{ERASE_LINE}Stackset {pNewStackSet} has been successfully created")
				# TODO: Use the NewStackSetId Operation Id, to check if the empty new stackset has successfully been created
				pass
			else:
				print(f"{pNewStackSet} failed to be created. Exiting...")
				Failure_GoToEnd = True
				sys.exit(99)

		else:  # PNewStackSet *does* exist
			# First time this script has run...
			print("New Stack Set already exists...")

		""" ######## This code is common across both use-cases ################## """
		logging.debug(f"Getting Stack Ids from existing stack set {pOldStackSet}")
		# **** 1. Get the stack-ids from the old stack-set ****
		if Use_recovery_file:
			pass
		else:
			"""
			1. Get the stack-ids from the old stack-set - write them to a file (in case we need to recover the process)
			"""
			stack_ids = get_stack_ids_from_existing_stack_set(aws_acct, pOldStackSet, pAccountsToMove)
		logging.debug(f"Found {len(stack_ids)} stack ids from stackset {pOldStackSet}")
		# Write the stack_ids info to a file, so we don't lose this info if the script fails
		fileresult = write_info_to_file(aws_acct, stack_ids)
		if not fileresult['Success']:
			print(f"Something went wrong.\n"
			      f"Error Message: {fileresult['ErrorMessage']}")
			Failure_GoToEnd = True
			sys.exit(9)
		# For every 10 stack-ids, use the OpId below to verify that the Operation has finished:
		# **** 2. Remove the stack-instances from the old stack-set ****
		logging.debug(f"Removing stack instances from stackset {pOldStackSet}")
		DisconnectStackInstances = disconnect_stack_instances(aws_acct, stack_ids, pOldStackSet)
		if not DisconnectStackInstances['Success']:
			if DisconnectStackInstances['ErrorMessage'].find('has no matching instances') > 0 and Use_recovery_file:
				pass  # This could be because the Old Stackset already had the instances disconnected when the script failed
			else:
				print(f"Failure... exiting due to: {DisconnectStackInstances['ErrorMessage']}")
				Failure_GoToEnd = True
				sys.exit(7)
		logging.debug(f"Removed stack instances from {pOldStackSet}")
		if DisconnectStackInstances['OperationId'] is not None:
			StackInstancesAreGone = check_stack_set_status(aws_acct, pOldStackSet,
			                                               DisconnectStackInstances['OperationId'])
			if not StackInstancesAreGone['Success']:
				Failure_GoToEnd = True
				sys.exit(
					f"There was a problem with removing the stack instances from stackset {pOldStackSet}. Exiting...")
			logging.debug(
				f"The operation id {DisconnectStackInstances['OperationId']} is {StackInstancesAreGone['StackSetStatus']}")
			intervals_waited = 1
			while StackInstancesAreGone['StackSetStatus'] in ['RUNNING']:
				print(f"Waiting for stack instances to be disconnected from stackset {pOldStackSet} -",
				      # f"." * intervals_waited,
				      f"{sleep_interval * intervals_waited} seconds waited so far", end='\r')
				sleep(sleep_interval)
				intervals_waited += 1
				StackInstancesAreGone = check_stack_set_status(aws_acct, pOldStackSet,
				                                               DisconnectStackInstances['OperationId'])
			if not StackInstancesAreGone['Success']:
				print(f"There was a problem with removing the stack instances from stackset {pOldStackSet}. Exiting...")
				Failure_GoToEnd = True
				sys.exit(8)
		# For every 10 stack-ids:
		# **** 3. Import those stack-ids into the new stack-set, 10 at a time ****
		x = 0
		limit = StackInstancesImportedAtOnce
		intervals_waited = 1
		while x < len(stack_ids['Stack_instances']):
			stack_ids_subset = [stack_ids['Stack_instances'][x + i] for i in range(limit) if
			                    x + i < len(stack_ids['Stack_instances'])]
			x += limit
			print(
				f"{ERASE_LINE}Importing {len(stack_ids_subset)} of {len(stack_ids['Stack_instances'])} stacks into the new stackset now...",
				end='\r')
			ReconnectStackInstances = populate_new_stack_with_existing_stack_instances(aws_acct, stack_ids_subset,
			                                                                           pNewStackSet)
			if not ReconnectStackInstances['Success']:
				print(f"Re-attaching the stack-instance to the new stackset seems to have failed."
				      f"The error received was: {ReconnectStackInstances['ErrorMessage']}")
				print(
					f"You'll have to resolve the issue that caused this problem, and then re-run this script using the recovery file.")
				Failure_GoToEnd = True
				sys.exit(9)
			StackReadyToImport = check_stack_set_status(aws_acct, pNewStackSet, ReconnectStackInstances['OperationId'])
			if not StackReadyToImport['Success']:
				Failure_GoToEnd = True
				sys.exit(f"There was a problem with importing the stack"
				         f" instances into stackset {pNewStackSet}. Exiting...")
			while StackReadyToImport['StackSetStatus'] in ['RUNNING', 'QUEUED']:
				print(
					f"{ERASE_LINE}Waiting for {len(stack_ids_subset)} more instances of StackSet {pNewStackSet} to finish importing -",
					f"{sleep_interval * intervals_waited} seconds waited so far", end='\r')
				sleep(sleep_interval)
				intervals_waited += 1
				StackReadyToImport = check_stack_set_status(aws_acct, pNewStackSet,
				                                            ReconnectStackInstances['OperationId'])
				if not StackReadyToImport['Success']:
					Failure_GoToEnd = True
					sys.exit(
						f"There was a problem with importing the stack instances into stackset {pNewStackSet}. Exiting...")
			logging.info(f"{ERASE_LINE}That import took {intervals_waited * sleep_interval} seconds to complete")

	else:  # Old Stackset doesn't exist - so there was a typo somewhere. Tell the user and exit
		print(f"It appears that the legacy stackset you provided {pOldStackSet} doesn't exist.\n"
		      f"Please check the spelling, or the account, and try again.\n\n"
		      f"{Fore.LIGHTBLUE_EX}Perhaps the recovery file was never deleted?{Fore.RESET}")

	# Delete the recovery file, if it exists
	# TODO: Insert a check to make sure the recovery file isn't deleted, if we failed something above...
	if exists(InfoFilename):
		try:
			FileDeleted = remove(InfoFilename)
		except OSError as myError:
			print(myError)

	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

	print()
	print("Thank you for using this script")
	print()
