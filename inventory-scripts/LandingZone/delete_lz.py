#!/usr/bin/env python
import boto3
from botocore.exceptions import ClientError
# from botocore.errorfactory import StackSetNotFoundException
import time
import sys

""" 
Script for cleanup of deployed AWS Landing Zone, as per flow from https://w.amazon.com/bin/view/AWS/Teams/SA/AWS_Solutions_Builder/Working_Backwards/AWS_Solutions-Foundations-Landing-Zone/deletion/
    To use it:
    1. Create a user within your Master account with Administrator Access and key pair or a session token
    2. run the script
Usage: python delete_lz.py REGION AWS_ACCESS_KEY AWS_SECRET_ACCESS_KEY [AWS_SESSION_TOKEN] [debug:true]
"""

__author__ = "Lech Migdal and many more"
__email__ = "lmigdal@amazon.com"
__status__ = "Use at your own risk"

# make sure we are running with python 3
if sys.version_info < (3, 0):
	print("Sorry, this script requires Python 3 to run")
	sys.exit(1)


def wait_with_progress_bar(Message="", Seconds=30):
	"""
	Wait for given number of seconds, displaying provided message and moving progress bar in the meantime
	"""
	iteration = 0
	for _ in range(Seconds):
		iteration += 1
		progress_string = "." * (iteration % 10)
		print(f'{Message}, please wait {progress_string}', end=' ')
		time.sleep(1)


def print_debug(message):
	"""Print message if debug is turned on"""
	if DEBUG:
		print(message)


if __name__ == "__main__":
	# This handles when they don't specify enough parameters - or too many.
	if len(sys.argv) < 4 or (len(sys.argv) == 6 and sys.argv[5] != 'debug:true'):
		print("Usage: python delete_lz REGION AWS_ACCESS_KEY AWS_SECRET_ACCESS_KEY [AWS_SESSION_TOKEN] [debug:true]")
		exit()

	# credentials for the root org account, note that this better have the super awesome role
	# if you are using Isengard or SSO, enter the access key, secret key and session token
	# if you are using hardcoded IAM credentials, then the session token should be left out (not recommended)
	AWS_REGION = sys.argv[1]
	AWS_ACCESS_KEY = sys.argv[2]
	AWS_SECRET_ACCESS_KEY = sys.argv[3]
	AWS_SESSION_TOKEN = ""
	AWS_SESSION_TOKEN_PASSED = False

	DEBUG = False
	if len(sys.argv) == 5 and sys.argv[4] == 'debug:true':
		DEBUG = True
		print("Debugging enabled and No Session Token passed")

	if len(sys.argv) == 5 and sys.argv[4] != 'debug:true':
		print("Debugging is NOT enabled and Session Token passed")
		AWS_SESSION_TOKEN = sys.argv[4]
		AWS_SESSION_TOKEN_PASSED = True

	if len(sys.argv) == 6 and sys.argv[5] == 'debug:true':
		DEBUG = True
		AWS_SESSION_TOKEN = sys.argv[4]
		AWS_SESSION_TOKEN_PASSED = True
		print("Debugging enabled and Session Token passed")

	start_time = time.time()
	SECURITY_ACCOUNT_NAME = "security"
	LOGGING_ACCOUNT_NAME = "log-archive"
	SHARED_SERVICES_ACCOUNT_NAME = "shared-services"
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	accounts = client.list_accounts()
	print('List of accounts in this organization:')
	for account in accounts['Accounts']:
		print(f"Account Name: {account['Name']} Email: {account['Email']}")
		if account['Name'].lower().find('logging') >= 0:
			LOGGING_ACCOUNT_NAME = account['Name']
		if account['Name'].lower().find('shared') >= 0:
			SHARED_SERVICES_ACCOUNT_NAME = account['Name']
		if account['Name'].lower().find('security') >= 0:
			SECURITY_ACCOUNT_NAME = account['Name']
	# Step 1 - disconnect directory from SSO - MUST be done manually
	user_input = input(
			"\nStep 1 (disconnect directory from SSO) isn't automated, you MUST do it manually BEFORE moving forward, do you want to proceed? [y/n]:")
	if user_input == 'n':
		exit()

	# Step 1a - Get the create event from the LandingZoneLaunchAVMStateMachine and change it to a delete event, then run the LandingZoneLaunchAVMStateMachine
	user_input = input(
			"\nStep 1a - Do you want to try using the LandingZoneLaunchAVMStateMachine Delete event method? [y/n]:"
			)
	if user_input == 'y':
		# iterate through current step functions to find the ARN for the LandingZoneLaunchAVMStateMachine
		if AWS_SESSION_TOKEN_PASSED:
			client = boto3.client('stepfunctions', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
		else:
			client = boto3.client('stepfunctions', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
		state_machines = client.list_state_machines()
		for state_machine in state_machines['stateMachines']:
			if state_machine['name'] == 'LandingZoneLaunchAVMStateMachine':
				arn = state_machine['stateMachineArn']

		# find the latest execution which should have all of the accounts reflected in the create event
		executions = client.list_executions(stateMachineArn=arn, statusFilter='SUCCEEDED')
		execution_arn = executions['executions'][0]['executionArn']
		execution = client.describe_execution(executionArn=execution_arn)

		# change the event from CREATE to DELETE and execute the DELETE event
		data_input = execution['input'].replace("Create", "Delete")
		execution_arn = client.start_execution(stateMachineArn=arn, input=data_input)
		execution_status = client.describe_execution(executionArn=execution_arn['executionArn'])

		# wait for a while - the LandingZoneLaunchAVMStateMachine will reverse the SC-0045 launches and terminate all of the stack instances from the baseline in each account
		while execution_status['status'] == 'RUNNING':
			wait_with_progress_bar(Message="Waiting for LandingZoneLaunchAVMStateMachine Delete event to complete",
			                       Seconds=30)
			execution_status = client.describe_execution(executionArn=execution_arn['executionArn'])

	# exit()

	# Step 2 - Remove products provisioned through Service Catalog
	print("\nStep 2 - Remove products provisioned through Service Catalog (it may take couple of minutes)")
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('servicecatalog', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('servicecatalog', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	provisioned_products = client.search_provisioned_products()['ProvisionedProducts']

	# if product wasnt created by StateMachineLambdaRole - delete it
	list_of_termination_records = []
	for provisioned_product in provisioned_products:
		if "StateMachineLambdaRole" not in provisioned_product['UserArn']:
			print(f"Terminating provisioned product {provisioned_product['Name']}", end=' ')
			response = client.terminate_provisioned_product(ProvisionedProductId=provisioned_product['Id'],
			                                                IgnoreErrors=True, TerminateToken=provisioned_product['Id'])
			list_of_termination_records.append(response['RecordDetail']['RecordId'])
			print("[DONE]")

	if len(list_of_termination_records) > 0:
		if DEBUG:
			print(list_of_termination_records)

		while len(list_of_termination_records) > 0:
			for termination_record in list(list_of_termination_records):
				response = client.describe_record(Id=termination_record)
				if response['RecordDetail']['Status'] == 'SUCCEEDED':
					list_of_termination_records.remove(termination_record)
				elif response['RecordDetail']['Status'] == 'FAILED':
					list_of_termination_records.remove(termination_record)
					print("Failed deletion of provisioned product {}        ".format(
							response['RecordDetail']['ProvisionedProductName']))
					input("Please perform manual cleanup and press ENTER when done")

			# we're doing delay in a while loop to display a nice progress bar :D
			if len(list_of_termination_records) > 0:
				wait_with_progress_bar(Message="Service Catalog products termination in progress", Seconds=30)
	else:
		print("No Service Catalog provisioned products to terminate")

	# Step 3 - content of portfolio from Service Catalog
	print("\nStep 3 - delete content of portfolio from Service Catalog ")
	portfolios = client.list_portfolios()['PortfolioDetails']
	if len(portfolios) > 0:
		for portfolio in portfolios:
			# delete constrains from portfolio
			constraints = client.list_constraints_for_portfolio(PortfolioId=portfolio['Id'])['ConstraintDetails']
			for constraint in constraints:
				client.delete_constraint(Id=constraint['ConstraintId'])
			# delete users and groups from portfolio
			principals = client.list_principals_for_portfolio(PortfolioId=portfolio['Id'])['Principals']
			for principal in principals:
				client.disassociate_principal_from_portfolio(PortfolioId=portfolio['Id'],
				                                             PrincipalARN=principal['PrincipalARN'])

		# to delete products from portfolios we need to go through products
		products = client.search_products_as_admin()['ProductViewDetails']
		for product in products:
			portfolios_for_product = client.list_portfolios_for_product(
					ProductId=product['ProductViewSummary']['ProductId'])
			for portfolio in portfolios_for_product['PortfolioDetails']:
				client.disassociate_product_from_portfolio(ProductId=product['ProductViewSummary']['ProductId'],
				                                           PortfolioId=portfolio['Id'])

		# delete the portfolio (finally)
		for portfolio in portfolios:
			print(f"Deleting portfolio {portfolio['Id']}", end=' ')
			client.delete_portfolio(Id=portfolio['Id'])
			print('[DONE]')
	else:
		print("No portfolios to delete")

	# Step 4 - delete Service Catalog products
	print("\nStep 4 - delete Service Catalog products")
	products = client.search_products_as_admin()['ProductViewDetails']
	if len(products) > 0:
		for product in products:
			print(f"Deleting product {product['ProductViewSummary']['ProductId']}", end=' ')
			client.delete_product(Id=product['ProductViewSummary']['ProductId'])
			print('[DONE]')
	else:
		print('No products to delete')

	# Step 5 - delete cloud formation baseline stacks
	print("\nStep 5 - delete cloud formation baseline stacks")
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('cloudformation', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('cloudformation', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	stacks = client.list_stacks(
			StackStatusFilter=['CREATE_COMPLETE', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_FAILED',
			                   'UPDATE_COMPLETE'])
	deleted_something = False
	for stack in stacks['StackSummaries']:
		desc = stack.get('TemplateDescription', '')
		if "(SO0045)" in desc and stack['StackStatus'] != 'DELETE_COMPLETE':
			print(f"Deleting stack {stack['StackName']} - {stack['TemplateDescription']}", end=' ')
			client.delete_stack(StackName=stack['StackName'])
			print("[DONE]")
			deleted_something = True

	if not deleted_something:
		print("No stacks with SO0045 in name to delete")

	# wait for stacks to be deleted
	delete_in_progress = True
	while delete_in_progress:
		delete_in_progress = False
		stacks = client.list_stacks(
				StackStatusFilter=['CREATE_COMPLETE', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_FAILED',
				                   'UPDATE_COMPLETE'])
		for stack in stacks['StackSummaries']:
			desc = stack.get('TemplateDescription', '')
			if "(SO0045)" in desc and stack['StackStatus'] != 'DELETE_COMPLETE':
				delete_in_progress = True
		if delete_in_progress:
			wait_with_progress_bar(Message="Stacks are still being deleted", Seconds=30)

	# Step 6 - Delete the Security Baseline for each account via StackSets in the Master Account
	print("\n\nStep 6 - Delete the Security Baseline for each account via StackSets in the Master Account")
	stack_sets_to_delete = []

	stack_sets = client.list_stack_sets(Status='ACTIVE')
	deleted_stack_sets = False
	for stack_set in stack_sets['Summaries']:
		deleted_stack_sets = False
		print(f"Checking whether {stack_set['StackSetName']} is a stackset we need to delete")
		print('Verbose Output:')
		print(f"     Stack Set Name: {stack_set['StackSetName']}")
		print(f"     Stack Set Status: {stack_set['Status']}")
		print(f'     Delete In Progress: {delete_in_progress}')

		if stack_set['StackSetName'] in stack_sets_to_delete and stack_set[
			'Status'] == 'ACTIVE' and not delete_in_progress:
			print(f"Deleting stack set {stack_set['StackSetName']}", end='')
			client.delete_stack_set(StackSetName=stack_set['StackSetName'])
			deleted_stack_sets = True
			delete_in_progress = True
		elif stack_set['StackSetName'] in stack_sets_to_delete and stack_set[
			'Status'] == 'FAILED' and not delete_in_progress:
			print(
					f"Even though the stack set {stack_set['StackSetName']} is in a FAILED state, we're going to delete it anyway...")
			print(f"Deleting stack set {stack_set['StackSetName']}", end='')
			client.delete_stack_set(StackSetName=stack_set['StackSetName'])
			print('[DONE]')
			deleted_stack_sets = True
			delete_in_progress = True
		elif not stack_set['StackSetName'] in stack_sets_to_delete:
			print(f"It appears that {stack_set['StackSetName']} isn't a stackset we need to delete", end='')

		# wait for those stacks sets to be deleted
		while deleted_stack_sets and delete_in_progress:
			delete_in_progress = False
			stack_set_status = {'Status': 'None'}
			try:
				stack_set_status = client.describe_stack_set(StackSetName=stack_set['StackSetName'])['StackSet'][
					'Status']
			except:
				# This means the deletion beat us.
				pass
				print(f"\nError deleting stack set {stack_set['StackSetName']}. The deletion probably beat us")
			# for stack_set in stack_sets['Summaries']:
			if stack_set_status['Status'] == 'ACTIVE':
				delete_in_progress = True
				print(f"Status of {stack_set['StackSetName']} stackset is currently {stack_set_status['Status']}")
				wait_with_progress_bar(Message="\nSecurity Baseline stack sets delete in progress", Seconds=30)
		print('[DONE]')
	# TODO: If the Stackset is in status "Failed" - this will go into a race condition, and never complete.
	if not deleted_stack_sets:
		print("No more stack sets to delete")

	# Step 7 - For the remaining StackSets which will still have stack instances, you will need to Manage Stacksets, enter the account numbers and regions,
	# and delete all stack instances. Once the stack instances have been deleted, delete the StackSets.
	# Note - I have added 3 stack sets, since they are not mentioned in the official doc - AWS-Landing-Zone-Baseline-PrimaryVPC, AWS-Landing-Zone-Baseline-SecurityRoles,
	# AWS-Landing-Zone-Centralized-Logging-Primary
	# added two more stacks based on contributed customizations - AWS-Landing-Zone-Baseline-ConfigAggregator and AWS-Landing-Zone-Baseline-ConfigAggregator
	# added the centralized logging primary and spoke stacks - AWS-Landing-Zone-Baseline-CentralizedLoggingSpoke and AWS-Landing-Zone-Centralized-Logging-Primary

	print("\nStep 7 - getting rid of multiple stack sets")

	stack_set_names = ["AWS-Landing-Zone-Baseline-EnableCloudTrail",
	                   "AWS-Landing-Zone-Baseline-EnableConfig",
	                   "AWS-Landing-Zone-Baseline-EnableConfigRules",
	                   "AWS-Landing-Zone-Baseline-EnableNotifications",
	                   "AWS-Landing-Zone-Baseline-IamPasswordPolicy",
	                   "AWS-Landing-Zone-SharedTopic",
	                   "AWS-Landing-Zone-SharedBucket",
	                   "AWS-Landing-Zone-SecurityRoles",
	                   "AWS-Landing-Zone-Baseline-SecurityRoles",
	                   "AWS-Landing-Zone-Baseline-CentralizedLoggingSpoke",
	                   "AWS-Landing-Zone-Centralized-Logging-Primary",
	                   "AWS-Landing-Zone-Baseline-ConfigAggregator",
	                   "AWS-Landing-Zone-ConfigAggregatorService",
	                   "AWS-Landing-Zone-PrimaryADConnector",
	                   "AWS-Landing-Zone-PrimaryAccountVPC",
	                   "AWS-Landing-Zone-SharedServicesRDGW",
	                   "AWS-Landing-Zone-SharedServicesActiveDirectory",
	                   "AWS-Landing-Zone-SharedServicesAccountVPC",
	                   "AWS-Landing-Zone-Baseline-PrimaryVPC",
	                   "AWS-Landing-Zone-GuardDutyMaster",
	                   "AWS-Landing-Zone-Baseline-ConfigRole",
	                   "AWS-Landing-Zone-Baseline-EnableConfigRulesGlobal"]

	for stack_set_name in stack_set_names:
		# first check if stack set exists at all
		stack_set_exists = False
		active_stack_sets = client.list_stack_sets(Status='ACTIVE')
		for active_stack_set in active_stack_sets['Summaries']:
			if active_stack_set['StackSetName'] == stack_set_name:
				stack_set_exists = True
				print(f"StackSet {active_stack_set['StackSetName']} exists, is ACTIVE and needs to be deleted.")

		if stack_set_exists:
			instances = client.list_stack_instances(StackSetName=stack_set_name)
			deleted_instances = False
			for instance in instances['Summaries']:
				if instance['Status'] == 'CURRENT' or instance['Status'] == 'OUTDATED' or instance[
					'Status'] == 'INOPERABLE':
					print("Deleting stack instance in account {}, region {} from {}".format(instance['Account'],
					                                                                        instance['Region'],
					                                                                        stack_set_name), end=" ")
					response = client.delete_stack_instances(StackSetName=stack_set_name,
					                                         Accounts=[instance['Account']],
					                                         Regions=[instance['Region']], RetainStacks=False)
					print_debug(response)
					delete_in_progress = True
					while delete_in_progress:
						operation_status = client.describe_stack_set_operation(StackSetName=stack_set_name,
						                                                       OperationId=response['OperationId'])
						if operation_status['StackSetOperation']['Status'] == 'SUCCEEDED':
							delete_in_progress = False
						if operation_status['StackSetOperation']['Status'] == 'FAILED':
							print('Stack Instance delete failed - fix the problem and try again')
							exit()
						print(".", end="")
						time.sleep(5)
						print_debug(
								f"Still deleting stackset {stack_set_name} in region {instance['Region']} in account {instance['Account']}")
					deleted_instances = True

				if not deleted_instances:
					print(f"No instances to delete for {stack_set_name}")

				# wait for delete operations on this stack set to finish
				# operations = client.list_stack_set_operations(StackSetName=stack_set_name)
				delete_in_progress = True
				while delete_in_progress:
					delete_in_progress = False
					operations = client.list_stack_set_operations(StackSetName=stack_set_name)
					for operation in operations['Summaries']:
						if operation['Action'] == "DELETE" and (
								operation['Status'] != 'SUCCEEDED' and operation[
							'Status'] != 'FAILED'):  # In other words - the status is "Running"
							delete_in_progress = True
							wait_with_progress_bar(Message="Instance deletion in progress", Seconds=10)
				print("[DONE]")

			# delete the stack set
			print(f"Deleting stack set {stack_set_name}", end=" ")
			try:
				client.delete_stack_set(StackSetName=stack_set_name)
				deleted_stack_set = True
				print('[DONE]')
			except ClientError as e:
				print(f"\nError deleting stack set {stack_set_name} - {e}")
				input("Please investigate it, delete all relevant resources and press ENTER to continue")
		else:
			print(f"Stack set {stack_set_name} not found, skipping it")

	# Step 8 - Unlock the member accounts (Skip this step: if the flag 'lock_down_stack_sets_role' is already set to 'No')
	print(
			"\nStep 8 - skipping it, assuming lock_down_stacks_set_role is set to 'No'. Following steps will fail otherwise!")

	# Step 9 - Delete the Logging Bucket in the Logging Account. Note - I delete all buckets that include 'aws-landing-zone' string in name
	print(
			"\nStep 9 - cleaning up logging account, since we are emptying S3 buckets one-by-one, this step will take some time. ")
	provided_account_name = input(f"Please provide logging account name or press ENTER if it's {LOGGING_ACCOUNT_NAME} ")
	if provided_account_name == "":
		provided_account_name = LOGGING_ACCOUNT_NAME

	deleted_logging_bucket = False
	# get the ID of the logging account
	account_found = False
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	accounts = client.list_accounts()
	for account in accounts['Accounts']:
		if (account['Name'] == provided_account_name) and not (account['Id'] == '614019996801'):
			account_found = True
			if AWS_SESSION_TOKEN_PASSED:
				sts_client = boto3.client('sts', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
				                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
				                          aws_session_token=AWS_SESSION_TOKEN)
			else:
				sts_client = boto3.client('sts', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
				                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
			# generate temporary session for the log-archive account
			role_arn = f"arn:aws:iam::{account['Id']}:role/AWSCloudFormationStackSetExecutionRole"
			print(f"Account ID for the log-archive account: {account['Id']}")
			account_credentials = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="ALZAddIsengardUserScript")[
				'Credentials']

			# create client with temporary credentials
			s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=account_credentials['AccessKeyId'],
			                         aws_secret_access_key=account_credentials['SecretAccessKey'],
			                         aws_session_token=account_credentials['SessionToken'])

			# delete bucket
			buckets = s3_client.list_buckets()['Buckets']
			for bucket in buckets:
				if 'aws-landing-zone' in bucket['Name']:
					# empty the bucket and delete it
					s3 = boto3.resource('s3', region_name=AWS_REGION,
					                    aws_access_key_id=account_credentials['AccessKeyId'],
					                    aws_secret_access_key=account_credentials['SecretAccessKey'],
					                    aws_session_token=account_credentials['SessionToken'])
					s3_bucket = s3.Bucket(bucket['Name'])
					if s3_bucket in s3.buckets.all():
						print(
								f"Emptying bucket (this may take a while, restart script if it crashes here) {bucket['Name']}",
								end=" ")
						try:
							s3_bucket.object_versions.all().delete()
							print('[DONE]')
							print(f"Deleting bucket {bucket['Name']}", end=" ")
							s3_bucket.delete()
							print('[DONE]')
							deleted_logging_bucket = True
						except ClientError as e:
							print(
									"Error while trying to delete S3 bucket {}, it should be empty by now so if you see BucketNotEmpty check the bucket in AWS console and delete it manually")
							input("Press ENTER, to continue, when you have deleted the S3 bucket")
							deleted_logging_bucket = True
	if not deleted_logging_bucket:
		print("No S3 buckets to delete")

	if not account_found:
		input_response = input(
				'Logging account WAS NOT FOUND. Unless you are certain this is ok, you should STOP and DEBUG this. Do you want to proceed with deletion? [y/n]')
		if input_response == 'n':
			exit()

	# Step 10 - Delete the auto-generated EC2 key-pairs in the Shared Services Account
	print("\nStep 10 - deleting auto-generated EC2 key-pairs")
	provided_account_name = input(
			f"Please provide shared-services account name or press ENTER if it's {SHARED_SERVICES_ACCOUNT_NAME}")
	if provided_account_name == "":
		provided_account_name = SHARED_SERVICES_ACCOUNT_NAME

	deleted_key_pair = False
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	accounts = client.list_accounts()
	account_found = False
	for account in accounts['Accounts']:
		if account['Name'] == provided_account_name:
			account_found = True
			if AWS_SESSION_TOKEN_PASSED:
				sts_client = boto3.client('sts', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
				                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
				                          aws_session_token=AWS_SESSION_TOKEN)
			else:
				sts_client = boto3.client('sts', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
				                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
			# generate temporary session for the logging account
			role_arn = f"arn:aws:iam::{account['Id']}:role/AWSCloudFormationStackSetExecutionRole"
			print(f"Account ID for the shared services account: {account['Id']}")
			account_credentials = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="ALZAddIsengardUserScript")[
				'Credentials']

			# create client with temporary credentials
			ec2_client = boto3.client('ec2', region_name=AWS_REGION,
			                          aws_access_key_id=account_credentials['AccessKeyId'],
			                          aws_secret_access_key=account_credentials['SecretAccessKey'],
			                          aws_session_token=account_credentials['SessionToken'])
			key_pairs = ec2_client.describe_key_pairs()['KeyPairs']
			for key_pair in key_pairs:
				if key_pair['KeyName'].startswith('lz'):
					print(f"Deleting key pair {key_pair['KeyName']}", end=" ")
					ec2_client.delete_key_pair(KeyName=key_pair['KeyName'])
					print("[DONE]")
					deleted_key_pair = True

	if not deleted_key_pair:
		print("Key pair not found for deletion")

	if not account_found:
		input_response = input(
				'Shared services account WAS NOT FOUND. Unless you are certain this is ok, you should STOP and DEBUG this. Do you want to proceed with deletion? [y/n]')
		if input_response == 'n':
			exit()

	# Step 11 - Delete the following S3 buckets in the Master Account
	print("\nStep 11 - delete S3 buckets for config and pipeline artifacts in the master account")
	if AWS_SESSION_TOKEN_PASSED:
		s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	# delete buckets
	deleted_a_bucket = False
	buckets = s3_client.list_buckets()['Buckets']
	for bucket in buckets:
		if ('aws-landing-zone-configuration' in bucket['Name']) or ('landingzonepipelineartifacts' in bucket['Name']):
			# empty the bucket and delete it
			if AWS_SESSION_TOKEN_PASSED:
				s3 = boto3.resource('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
				                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
			else:
				s3 = boto3.resource('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
				                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
			bucket_to_delete = s3.Bucket(bucket['Name'])
			print_debug(f"Bucket to delete: {bucket_to_delete}")
			try:
				print(f"Emptying bucket (this may take a while) {bucket['Name']}", end=" ")
				bucket_to_delete.object_versions.all().delete()
				print('[DONE]')
			except ClientError as e:
				print(f"An error occured - {e}")
				input(
						"This _may_ mean that not all objects were deleted from the bucket, please investigate, empty bucket manually and press ENTER to continue")

			try:
				print(f"Deleting bucket {bucket['Name']}", end=" ")
				bucket_to_delete.delete()
				print('[DONE]')
				deleted_a_bucket = True
			except ClientError as e:
				print(f"An error occured - {e}")
				input("Please delete the bucket manually and press ENTER to continue")

	if not deleted_a_bucket:
		print("Buckets with matching names not found")

	# Step 12 - Delete the config recorder and delivery channel from any account you wish to reuse
	'''
    print("\nStep 12 - Delete the config recorder and delivery channel from any account you wish to reuse")
    if AWS_SESSION_TOKEN_PASSED:
        config = boto3.client(
            'config',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN
        )
    else:
        config = boto3.client(
            'config',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    DeliveryChannelName = config.describe_delivery_channels()
    DeliveryChannelDeletion = config.delete_delivery_channel(
        DeliveryChannelName=DeliveryChannelName
    )
    ConfigRecorderName = config.describe_configuration_recorders()
    ConfigRecorderNameDeletion = config.delete_configuration_recorder(
        ConfigurationRecorderName=ConfigRecorderName
    )
    '''
	'''
    print("\nStep 12 - Delete the config recorder and delivery channel from any account you wish to reuse")
    user_input = input("This step is MANUAL (if you need it) and must be done with CLI. Do you want to continue? [y/n]")
    if user_input == 'n':
        exit()
    '''

	# Step 12.5 - delete stacks that are not mentioned in the deletion manual, but are hanging
	print("\nStep 12.5 - Delete anything that is left with 'AWS-Landing-Zone' in name")
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('cloudformation', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('cloudformation', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	stacks = client.list_stacks()
	deleted_something = False
	for stack in stacks['StackSummaries']:
		if "AWS-Landing-Zone" in stack['StackName'] and stack['StackStatus'] != 'DELETE_COMPLETE':
			print(f"Deleting stack {stack['StackName']} - {stack['TemplateDescription']}", end=' ')
			client.delete_stack(StackName=stack['StackName'])
			print("[DONE]")
			deleted_something = True

	if not deleted_something:
		print("No stacks with AWS-Landing-Zone in name to delete")

	# we are not waiting for those deletion to finish

	# Step 12.6 - remove GuardDuty detectors
	user_input = input(
			"\nStep 12.6 - Do you want to remove GuardDuty detectors? [y/n]:"
			)
	if user_input == 'y':
		print('Deleting detectors in master account')
		if AWS_SESSION_TOKEN_PASSED:
			session = boto3.session.Session(region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
			                                aws_session_token=AWS_SESSION_TOKEN)
		else:
			session = boto3.session.Session(region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
		# iterate through current step functions to find the ARN for the LandingZoneLaunchAVMStateMachine
		guardduty_regions = session.get_available_regions('guardduty')
		guardduty_regions.remove('ap-east-1')  # Removes HongKong
		guardduty_regions.remove('me-south-1')  # Removes Bahrain
		for region in guardduty_regions:
			if AWS_SESSION_TOKEN_PASSED:
				client = boto3.client('guardduty', region_name=region, aws_access_key_id=AWS_ACCESS_KEY,
				                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
			else:
				client = boto3.client('guardduty', region_name=region, aws_access_key_id=AWS_ACCESS_KEY,
				                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
			detectors = client.list_detectors()
			for detector in detectors['DetectorIds']:
				response = client.delete_detector(DetectorId=detector)
				print(f"Deleted GuardDuty detector {detector} in region {region}")
				print_debug(response)
		print("\nAssuming security account is called 'security', edit the script otherwise")
		provided_account_name = input(
				f"Please provide security account name or press ENTER if it's {SECURITY_ACCOUNT_NAME}")
		if provided_account_name == "":
			provided_account_name = SECURITY_ACCOUNT_NAME

		deleted_key_pair = False
		if AWS_SESSION_TOKEN_PASSED:
			client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
		else:
			client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
		accounts = client.list_accounts()
		account_found = False
		for account in accounts['Accounts']:
			if account['Name'] == provided_account_name:
				account_found = True
				if AWS_SESSION_TOKEN_PASSED:
					sts_client = boto3.client('sts', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
					                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
					                          aws_session_token=AWS_SESSION_TOKEN)
				else:
					sts_client = boto3.client('sts', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
					                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
				# generate temporary session for the security account
				role_arn = f"arn:aws:iam::{account['Id']}:role/AWSCloudFormationStackSetExecutionRole"
				print(f"Account ID for the security account: {account['Id']}")
				account_credentials = \
					sts_client.assume_role(RoleArn=role_arn, RoleSessionName="ALZAddIsengardUserScript")[
						'Credentials']

				# create client with temporary credentials
				session = boto3.session.Session(region_name=AWS_REGION,
				                                aws_access_key_id=account_credentials['AccessKeyId'],
				                                aws_secret_access_key=account_credentials['SecretAccessKey'],
				                                aws_session_token=account_credentials['SessionToken'])

				# iterate through current step functions to find the ARN for the LandingZoneLaunchAVMStateMachine
				# guardduty_regions = session.get_available_regions('guardduty')
				for region in guardduty_regions:
					client = boto3.client('guardduty', region_name=region,
					                      aws_access_key_id=account_credentials['AccessKeyId'],
					                      aws_secret_access_key=account_credentials['SecretAccessKey'],
					                      aws_session_token=account_credentials['SessionToken'])
					detectors = client.list_detectors()
					for detector in detectors['DetectorIds']:
						response = client.delete_detector(DetectorId=detector)
						print(f"Deleted GuardDuty detector {detector} in region {region}")
						print_debug(response)

	# Step 13
	print("\nStep 13 - Delete the Landing Zone initiation template")
	user_input = input(
			"\nStep 13 - Do you want to remove the landing zone initiation template? [y/n]:"
			)
	if user_input == 'y':
		if AWS_SESSION_TOKEN_PASSED:
			client = boto3.client('cloudformation', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
		else:
			client = boto3.client('cloudformation', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
			                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
		stacks = client.list_stacks()
		deleted_something = False
		for stack in stacks['StackSummaries']:
			desc = stack.get('TemplateDescription', '')
			if "(SO0044)" in desc and stack['StackStatus'] != 'DELETE_COMPLETE':
				print(f"Updating termination protection in case it's set on stack {stack['StackName']}")
				client.update_termination_protection(EnableTerminationProtection=False, StackName=stack['StackName'])
				print(f"Triggering delete of stack {stack['StackName']} - {stack['TemplateDescription']}", end=' ')
				client.delete_stack(StackName=stack['StackName'])
				print("[DONE]")
				deleted_something = True

		if not deleted_something:
			print("No stacks with SO0044 in name to delete")

		# wait for stacks to be deleted
		delete_in_progress = True
		while delete_in_progress:
			delete_in_progress = False
			stacks = client.list_stacks()
			for stack in stacks['StackSummaries']:
				desc = stack.get('TemplateDescription', '')
				if "(SO0044)" in desc and stack['StackStatus'] != 'DELETE_COMPLETE':
					# print(stack)
					delete_in_progress = True
			if delete_in_progress:
				wait_with_progress_bar(
						Message="Stack(s) are still being deleted (if it takes more than 1 hour, restart the process)",
						Seconds=30)

	# Step 14 - Clean up Organizations
	print("\n\nStep 14 - Clean up Organizations.")
	print(
			"If you've got any errors above, this is the best time to manually review ALZ accounts and remove all resources that are left behind")
	input_response = input('Do you want to continue? [y/n]')
	if input_response == 'n':
		exit()

	deleted_something = False
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('organizations', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	# move accounts out of the org
	roots = client.list_roots()['Roots']
	for root in roots:
		ous = client.list_organizational_units_for_parent(ParentId=root['Id'])['OrganizationalUnits']
		for ou in ous:
			accounts = client.list_accounts_for_parent(ParentId=ou['Id'])['Accounts']
			for account in accounts:
				print(f"Moving account {account['Id']} to root", end=" ")
				client.move_account(AccountId=account['Id'], SourceParentId=ou['Id'], DestinationParentId=root['Id'])
				print("[DONE]")

	# delete ous
	roots = client.list_roots()['Roots']
	for root in roots:
		ous = client.list_organizational_units_for_parent(ParentId=root['Id'])['OrganizationalUnits']
		for ou in ous:
			print(f"Deleting OU {ou['Name']}", end=" ")
			client.delete_organizational_unit(OrganizationalUnitId=ou['Id'])
			print('[DONE]')
			deleted_something = True

	if not deleted_something:
		print("Found nothing to delete")

	# Step 15 - Delete all the Landing Zone SSM Parameters
	print("\nStep 15 - Delete all the Landing Zone SSM Parameters")
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('ssm', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('ssm', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	deleted_any_ssm_params = False
	# because the API for delete is able to accept max 10 params in one shot, we need to run it multiple times
	while True:
		ssm_parameters = client.describe_parameters(MaxResults=10)
		print_debug(ssm_parameters)

		list_of_params = []
		for ssm_parameter in ssm_parameters['Parameters']:
			list_of_params.append(ssm_parameter['Name'])

		if len(list_of_params) > 0:
			print("Deleting SSM Parameters", end=" ")
			client.delete_parameters(Names=list_of_params)
			deleted_any_ssm_params = True
			print("[DONE]")
		else:
			break

	if not deleted_any_ssm_params:
		print("No SSM Parameters found to delete")

	# Step 16 - Ensure the Landing Zone KMS Keys have been deleted
	print("\nStep 16 - Ensure the Landing Zone KMS Keys have been deleted")
	if AWS_SESSION_TOKEN_PASSED:
		client = boto3.client('kms', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
	else:
		client = boto3.client('kms', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
		                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	deleted_alias = False
	ALIAS_NAME = "alias/AwsLandingZoneKMSKey"
	for alias in client.list_aliases()['Aliases']:
		if alias['AliasName'] == ALIAS_NAME:
			print(f"Deleting alias {alias['AliasName']}", end=" ")
			client.delete_alias(AliasName=ALIAS_NAME)
			deleted_alias = True
			print("[DONE]")

	if not deleted_alias:
		print(f"Alias {ALIAS_NAME} not found")

	print("\nWe're done! All resources from your ALZ accounts are removed!")
	print(f"Total removal time {time.time() - start_time} seconds")
