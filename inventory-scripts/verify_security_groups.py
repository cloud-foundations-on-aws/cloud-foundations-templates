# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http://aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.

import csv, logging, jmespath, os
import boto3, botocore
from typing import Any, Dict, List
from pprint import pprint

__version__ = '2024.09.04'
# import time

# Global Variables
CSV_FILE = os.getenv("CSV_FILE", "./all.csv")
DRY_RUN = os.getenv("DRY_RUN", False)
# This is to use this script to VALIDATE the Security Group findings, instead of apply anything.
VALIDATION = os.getenv("VALIDATION", "False")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", logging.ERROR)


def main(CSV_FILE):
	"""
	Main Python function to attach security group to ENIs. Responsible for:
	1. Identifying current account id, region.
	2. Importing CSV file and loading into state.
	3. Comparing CSV ARN entry with AWS current ID and Region.
	4. Identifying Security Group ID and matching to contextual ARNs.
	5. Attaching valid Security Groups with valid ARNS.

	Args:
		CSV_FILE (str): CSV file path

	Returns:
		Pass or Failure [0/1]
	"""
	logging.basicConfig(level=LOGGING_LEVEL, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging_minimum = logging.ERROR
	logging.getLogger("boto3").setLevel(logging_minimum)
	logging.getLogger("botocore").setLevel(logging_minimum)
	logging.getLogger("csv").setLevel(logging_minimum)
	logging.getLogger("jmespath").setLevel(logging_minimum)
	logging.getLogger("typing").setLevel(logging_minimum)
	logging.getLogger("os").setLevel(logging_minimum)
	logging.getLogger("connectionpool").setLevel(logging_minimum)
	logging.info("Initializing Security Group attachment script.")

	try:
		csv_data = csv_import(CSV_FILE)
	except Exception as e:
		logging.error(f"ERROR: Unable to importing CSV file.\n"
		              f"Error Message: {e}")

	try:
		account_id, region = current_contextual_identity()
		if account_id is None or region is None:
			raise ValueError("Unable to determine current account id and region.")
		logging.info(f"Found that we're working in account {account_id} in region {region}")

	except:
		logging.error("ERROR: Unable to get AWS IAM contextual identity.")

	try:
		matching_entries = get_arns_for_current_account(csv_data, account_id, region)
		logging.info(f"Found {len(matching_entries)} matching entries")
	except:
		logging.error("ERROR: Unable to get matching CSV entries.")

	if VALIDATION in ['False', 'false']:
		logging.info("VALIDATION mode disabled. Attaching security groups.")
		try:
			attach_security_groups(matching_entries)
		except:
			logging.error("ERROR: Unable to attach security groups.")
	else:
		logging.info("Validation mode enabled. No changes will be made.")
		try:
			results = validate_security_groups(matching_entries)
			logging.debug(results)
			successful_results = 0
			compliant_results = 0
			for result in results:
				if result['Success']:
					successful_results += 1
					if result['Compliant']:
						compliant_results += 1
				pprint(result)
			print(f"Finished validation with {successful_results} successful checks and {compliant_results} compliant resources out of a total of {len(matching_entries)} requested resources.")
		except:
			logging.error("ERROR: Unable to validate security groups.")

	print("Finalized script. Exiting")


def current_contextual_identity():
	"""
	Identify the current account id and region using a Boto3 call.

	Args:
		None
	Returns:
		String : Account ID
		String : Region
	"""
	try:
		sts = boto3.client("sts")
		account_id = sts.get_caller_identity()["Account"]
		region = boto3.Session().region_name
		logging.info(f"Account: {account_id} | Region: {region}")
		return account_id, region

	except Exception as e:
		logging.error(f"ERROR: Unable to determine current account id and region: {e}")
		return None, None


def csv_import(csv_file_path: str) -> List[Dict[str, Any]]:
	"""
	Import a CSV file and return the data as a list of dictionaries.

	Args:
		csv_file_path (str): The path to the CSV file.
	Returns:
		List[Dict[str, Any]]: A list of dictionaries representing the CSV data.
	"""
	try:
		with open(csv_file_path, "r") as csv_file:
			reader = csv.DictReader(csv_file)
			data = list(reader)
		return data
	except Exception as e:
		logging.error(f"Error importing CSV file: {e}")
		return []


def get_arns_for_current_account(csv_data: List[Dict[str, Any]], account_id: str, region: str) -> List[Dict[str, Any]]:
	"""
	Compare the CSV ARN entries with the current account id and region, and return a list of matching entries.

	Args:
		csv_data (List[Dict[str, Any]]): The CSV data imported as a list of dictionaries.
		account_id (str): The current account id.
		region (str): The current region.
	Returns:
		List[Dict[str, Any]]: A list of dictionaries representing the matching CSV entries.
	"""
	matching_entries = []
	for entry in csv_data:
		# Test 1: Check to see if Account ID and Region match
		# Test 2: Check to see if the Security Group is valid
		# Test 3: Check to see if the Security Group name is unique (multiple sgs named "default" is possible given multiple VPCs)
		# If Test 1 and Test 2 pass - add to matching entries (after stripping all whitespace, tabs, etc.)

		target_account_id = entry["arn"].strip().split(":")[4]
		target_region = entry["arn"].strip().split(":")[3]
		security_group_name = entry["security_group"].strip()
		security_group_id = get_security_group_id_from_name(security_group_name)

		if (target_account_id == account_id and target_region == region) and security_group_id != '':
			clean_entry = {
				"arn"                : entry["arn"].strip(),
				"security_group_name": security_group_name,
				"security_group"     : get_security_group_id_from_name(security_group_name),
				}
			matching_entries.append(clean_entry)

	if matching_entries == []:
		logging.info("No matching entries found, returning empty list")

	return matching_entries


def check_security_group_validity(security_group_name: str) -> bool:
	"""
	Check the validity of the security group. Returns true if security exists, else false

	Args:
		security_group_name (str): The security group dictionary.
	Returns:
		bool: True if the security group is valid, False otherwise.
	"""
	try:
		security_group_response = boto3.client("ec2").describe_security_groups()
		if security_group_name in jmespath.search("SecurityGroups[].GroupName", security_group_response):
			return True
	except Exception as e:
		logging.error(f"Security Group is not valid: {e}")
		return False


def get_security_group_id_from_name(security_group_name: str) -> str:
	"""
	Get the Security Group ID from the Security Group Name. Returns sg-id or empty string

	Args:
		security_group_name (Dict[str, Any]): The security group name dictionary.
	Returns:
		str: Security Group ID
	"""
	try:
		security_group_response = boto3.client("ec2").describe_security_groups()
    # The problem here is that the result of the search can bring back multiple matching security group ids for the same named security group ("default")
		matching_security_group_ids = jmespath.search(f"SecurityGroups[?GroupName==`{security_group_name}`].GroupId", security_group_response)
		if len(matching_security_group_ids) == 1:
			return matching_security_group_ids[0]
		elif len(matching_security_group_ids) > 1:
			logging.error(f'Security Group name "{security_group_name}" represents more than one specific SG.\n'
			              f'This script can only validate uniquely named Security Groups.\n')
			return ''
		else:
			logging.error(f"Security Group name \"{security_group_name}\" wasn't found in account.")
			return ''
	except Exception as e:
		logging.error(f"Security Group doesn't exist: {e}")


def get_resource_type_from_arn(arn) -> str:
	"""
	Extracts the resource type from an Amazon Resource Name (ARN).

	Args:
		arn (str): The ARN string.

	Returns:
		str: The resource type extracted from the ARN.
	"""
	# Split the ARN string by the ':' delimiter
	arn_parts = arn.split(":")

	# The resource type is the sixth part of the ARN
	resource_type = arn_parts[2].split("/")[0]

	return resource_type


def attach_security_groups(matching_entries: List[Dict[str, Any]]) -> bool:
	"""
	Attach the valid security groups to the matching ARNs. Separates entries into resources types.
	Five supported resources types today are EC2, ELBv2, RDS, Lambda, ECS. Additional resource types can be added

	Args:
		matching_entries (List[Dict[str, Any]]): A list of dictionaries representing the matching CSV entries.
	Returns:
		True if successful, False otherwise.
	Raises:
		Exception: If an error occurs while attaching security groups.
	"""
	try:
		for entry in matching_entries:
			entry_type = get_resource_type_from_arn(entry["arn"])
			if entry_type == "ec2":
				attach_security_groups_to_ec2(entry)
			elif entry_type == "elasticloadbalancing":
				attach_security_groups_to_elasticloadbalancing(entry)
			elif entry_type == "ecs":
				attach_security_groups_to_ecs_task(entry)
			elif entry_type == "rds":
				attach_security_groups_to_rds(entry)
			elif entry_type == "lambda":
				attach_security_groups_to_lambda(entry)
			else:
				logging.info("Unsupported resource type: %s", entry_type)
		return True
	except Exception as e:
		logging.error(f"ERROR: Attaching security groups: {e}")
		logging.error(f"\tResource Type: {entry_type}")
		logging.error(f"\tARN: {entry['arn']}")
		logging.error(f"\tSecurity Group: {entry['security_group']}")

		return False


def attach_security_groups_to_elasticloadbalancing(matching_entry: Dict[str, Any]) -> None:
	"""
	Attach the valid security groups to the matching ELBv2 ARNs.

	Args:
		matching_entry (List[Dict[str, Any]]): A list of dictionaries representing the matching CSV entries.
	Returns:
		None
	"""
	try:
		elbv2_arn = matching_entry["arn"]
		elbv2_response = boto3.client("elbv2").describe_load_balancers(LoadBalancerArns=[elbv2_arn])
		elbv2_security_groups = jmespath.search("LoadBalancers[].SecurityGroups", elbv2_response)[0]

		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if elbv2_security_groups == []:
			new_elbv2_security_groups = []
			new_elbv2_security_groups.append(matching_entry["security_group"])
		elif not matching_entry["security_group"] in elbv2_security_groups:
			new_elbv2_security_groups = []
			new_elbv2_security_groups.append(elbv2_security_groups)
			new_elbv2_security_groups.append(matching_entry["security_group"])
			if DRY_RUN:
				logging.info(f"DRY_RUN: ELBv2 {elbv2_arn}: Would have added Security Groups: {new_elbv2_security_groups}")
			else:
				boto3.client("elbv2").set_security_groups(
					LoadBalancerArn=matching_entry["arn"],
					SecurityGroups=new_elbv2_security_groups,
					)
				logging.info(
					f"ELBv2 {elbv2_arn}. Added Security Groups: {new_elbv2_security_groups}"
					)

		# Secondary case: Security Group is the only Security Group attached.
		elif matching_entry["security_group"] in elbv2_security_groups:
			logging.debug(
				f"ELBv2 {elbv2_arn}. Already has security Group: {matching_entry['security_group']}. Skipping"
				)
		# Third Case: there are no ELBv2s to attach
		elif elbv2_response["LoadBalancers"] == []:
			logging.error(f"ELBv2 {elbv2_arn} not found")
		else:
			logging.debug("Provided ELBv2 did not meet use cases. Skipping")

	except botocore.exceptions.ClientError as e:
		logging.error(
			f"Error attaching security group {matching_entry['security_group']} to ELBv2 {matching_entry['arn']}: \nError: {e}"
			)


def attach_security_groups_to_ec2(matching_entry: Dict[str, Any]) -> None:
	"""
	Attach the valid security groups to the matching EC2 ARNs.

	Args:
		matching_entry (Dict[str, Any]): A list of dictionaries representing the matching CSV entries.
	Returns:
		None
	"""

	try:
		ec2_id = matching_entry["arn"].split("/")[1]
		ec2_response = boto3.client("ec2").describe_instances(InstanceIds=[ec2_id])
		ec2_security_groups = jmespath.search(
			"Reservations[].Instances[].SecurityGroups[].GroupId",
			ec2_response,
			)
		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if ec2_security_groups == []:
			new_ec2_security_groups = []
			new_ec2_security_groups.append(matching_entry["security_group"])

		elif not matching_entry["security_group"] in ec2_security_groups:
			new_ec2_security_groups = ec2_security_groups
			new_ec2_security_groups.append(matching_entry["security_group"])

			if DRY_RUN:
				logging.info(f"DRY_RUN: EC2 {ec2_id}: Would have added Security Groups: {new_ec2_security_groups}")
			else:
				boto3.client("ec2").modify_instance_attribute(
					InstanceId=ec2_id,
					Groups=new_ec2_security_groups,
					)
				logging.info(
					f"EC2 {ec2_id}. Added Security Groups: {new_ec2_security_groups}"
					)
		# Secondary case: Security Group is the only Security Group attached.
		elif matching_entry["security_group"] in ec2_security_groups:
			logging.debug(
				f"EC2 {ec2_id}. Already has security Group: {matching_entry['security_group']}. Skipping"
				)
		# Third Case: there are no EC2s to attach
		elif ec2_response["Reservations"] == []:
			logging.error(f"EC2 {ec2_id} not found")

		else:
			logging.debug("Provided EC2 Instances did not meet use cases. Skipping")

	except botocore.exceptions.ClientError as e:
		logging.error(
			f"Error attaching security group {matching_entry['security_group']} to EC2 {matching_entry['arn']}. \nError: {e}"
			)


def attach_security_groups_to_ecs_task(matching_entry: Dict[str, Any]) -> None:
	"""
	Attach the valid security groups to the matching EC2 ARNs.

	Args:
		matching_entry (Dict[str, Any]): A list of dictionaries representing the matching CSV entries.
	Returns:
		None
	"""
	try:

		cluster_name = matching_entry["arn"].split("/")[1]
		service_name = matching_entry["arn"].split("/")[2]
		ecs_service_response = boto3.client("ecs").describe_services(
			cluster=cluster_name, services=[service_name]
			)

		security_group_ids = []

		if ecs_service_response != []:
			ecs_security_group_ids = jmespath.search(
				"services[].networkConfiguration.awsvpcConfiguration.securityGroups",
				ecs_service_response,
				)[0]
			subnet_ids = jmespath.search(
				"services[].networkConfiguration.awsvpcConfiguration.subnets[]",
				ecs_service_response,
				)
			# Primary Case: Security Group not in security rules and there could be 0+ security groups.
			if ecs_security_group_ids == []:
				new_ecs_security_groups = []
				new_ecs_security_groups.append(matching_entry["security_group"])

			elif not matching_entry["security_group"] in security_group_ids:
				new_ecs_security_groups = ecs_security_group_ids
				new_ecs_security_groups.append(matching_entry["security_group"])

				if DRY_RUN:
					logging.info(f"DRY_RUN: ECS {service_name}: Would have added Security Groups: {new_ecs_security_groups}")
				else:
					boto3.client("ecs").update_service(
						cluster=cluster_name,
						service=service_name,
						networkConfiguration={
							"awsvpcConfiguration": {
								"securityGroups": new_ecs_security_groups,
								"subnets"       : subnet_ids,
								}
							},
						)

					logging.info(
						f"ECS {service_name}. Added Security Groups: {new_ecs_security_groups}"
						)
			# Secondary case: Security Group is the only Security Group attached.
			elif matching_entry["security_group"] in security_group_ids:
				logging.debug(
					f"ECS {service_name}. Already has security Group: {matching_entry['security_group']}. Skipping"
					)
			# Third Case: there are no ECS Services to attach
			elif ecs_service_response == []:
				logging.error(f"ECS {matching_entry['arn']} not found")
			else:
				logging.debug("Provided ECS Services did not meet use cases. Skipping")

		else:
			logging.error(f"Cluster '{cluster_name}' not found.")

	except botocore.exceptions.ClientError as e:
		logging.error(
			f"Error attaching security group {matching_entry['security_group']} to EC2 {matching_entry['arn']}: \nError: {e}"
			)


def attach_security_groups_to_rds(matching_entry: Dict[str, Any]) -> None:
	"""
	Attach the valid security groups to the matching RDS ARNs.

	Args:
		matching_entry (Dict[str, Any]): A list of dictionaries representing the matching CSV entries.
	Returns:
		None
	"""
	try:
		rds_response = boto3.client("rds").describe_db_instances(
			DBInstanceIdentifier=matching_entry["arn"]
			)
		rds_security_groups = jmespath.search(
			"DBInstances[].VpcSecurityGroups[].VpcSecurityGroupId", rds_response
			)
		rds_instance_id = jmespath.search(
			"DBInstances[].DBInstanceIdentifier", rds_response
			)[0]

		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if rds_security_groups == []:
			new_rds_security_groups = []
			new_rds_security_groups.append(matching_entry["security_group"])

		elif not matching_entry["security_group"] in rds_security_groups:
			new_rds_security_groups = rds_security_groups
			new_rds_security_groups.append(matching_entry["security_group"])

			if DRY_RUN:
				logging.info(f"DRY_RUN: RDS {matching_entry['arn']}: Would have added Security Groups: {new_rds_security_groups}")
			else:
				boto3.client("rds").modify_db_instance(
					DBInstanceIdentifier=rds_instance_id,
					VpcSecurityGroupIds=new_rds_security_groups,
					)
				logging.info(
					f"RDS {matching_entry['arn']}. Added Security Groups: {new_rds_security_groups}"
					)
		# Secondary case: Security Group is the only Security Group attached.
		elif matching_entry["security_group"] in rds_security_groups:
			logging.debug(
				f"RDS {matching_entry['arn']}. Already has security Group: {matching_entry['security_group']}. Skipping"
				)
		# Third Case: there are no RDS Instances to attach
		elif rds_response["DBInstances"] == []:
			logging.error(f"RDS {matching_entry['arn']} not found")
		else:
			logging.debug("Provided RDS Instances did not meet use cases. Skipping")

	except botocore.exceptions.ClientError as e:
		logging.error(
			f"Error attaching security group {matching_entry['security_group']} to RDS {matching_entry['arn']}: \nError: {e}"
			)


def attach_security_groups_to_lambda(matching_entry: Dict[str, Any]) -> None:
	"""
	Attach the valid security groups to the matching Lambda ARNs.

	Args:
		matching_entry (Dict[str, Any]): A list of dictionaries representing the matching CSV entries.
	Returns:
		None
	"""
	try:
		lambda_arn = matching_entry["arn"]
		lambda_response = boto3.client("lambda").get_function(FunctionName=lambda_arn)
		lambda_security_groups = jmespath.search(
			"Configuration.VpcConfig.SecurityGroupIds", lambda_response
			)
		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if lambda_security_groups == []:
			new_lambda_security_groups = []
			new_lambda_security_groups.append(matching_entry["security_group"])

		elif not matching_entry["security_group"] in lambda_security_groups:
			new_lambda_security_groups = lambda_security_groups
			new_lambda_security_groups.append(matching_entry["security_group"])

			if DRY_RUN:
				logging.info(f"DRY_RUN: Lambda {lambda_arn}: Would have added Security Groups: {new_lambda_security_groups}")
			else:
				boto3.client("lambda").update_function_configuration(
					FunctionName=lambda_arn,
					VpcConfig={"SecurityGroupIds": new_lambda_security_groups},
					)
				logging.info(
					f"Lambda {lambda_arn}. Added Security Groups: {new_lambda_security_groups}"
					)
		# Secondary case: Security Group is the only Security Group attached.
		elif matching_entry["security_group"] in lambda_security_groups:
			logging.debug(
				f"Lambda {lambda_arn}. Already has security Group: {matching_entry['security_group']}. Skipping"
				)
		# Third Case: there are no Lambda Functions to attach
		elif lambda_response == []:
			logging.error(f"Lambda {matching_entry['arn']} not found")
		else:
			logging.debug("Provided Lambda Functions did not meet use cases. Skipping")

	except botocore.exceptions.ClientError as e:
		logging.error(
			f"Error attaching security group {matching_entry['security_group']} to Lambda {matching_entry['arn']}: \nError: {e}"
			)


def validate_security_groups(matching_entries: List[Dict[str, Any]]) -> list:
	"""
	Validate the security groups by printing them out.

	Args:
		matching_entries (List[Dict[str, Any]]): A list of dictionaries representing the matching CSV entries.
	Returns:
		List of everything we validated
	Raises:
		Exception: If an error occurs while attaching security groups.
	"""
	try:
		multiple_responses = []
		for entry in matching_entries:
			entry_type = get_resource_type_from_arn(entry["arn"])
			logging.info(f"*********** ARN: {entry['arn']}")
			logging.info(f"Security Group Name: {entry['security_group_name']}")
			logging.info(f"Security Group ID: {entry['security_group']}")
			if entry_type == "ec2":
				single_response = validate_security_groups_to_ec2(entry)
			elif entry_type == "elasticloadbalancing":
				single_response = validate_security_groups_to_elasticloadbalancing(entry)
			elif entry_type == "ecs":
				single_response = validate_security_groups_to_ecs_task(entry)
			elif entry_type == "rds":
				single_response = validate_security_groups_to_rds(entry)
			elif entry_type == "lambda":
				single_response = validate_security_groups_to_lambda(entry)
			else:
				error_message = f"Unsupported resource type: {entry_type}"
				logging.info(error_message)
				single_response = {"Success": False, "ErrorMessage": error_message}
			multiple_responses.append(single_response)
	except Exception as e:
		error_message = (f"ERROR: Validating security groups: {e}\n"
		                 f"\tResource Type: {entry_type}\n"
		                 f"\tARN: {entry['arn']}\n"
		                 f"\tSecurity Group: {entry['security_group']}")
		single_response = {"Success": False, "ErrorMessage": error_message}
		return [single_response]

	return multiple_responses


def validate_security_groups_to_elasticloadbalancing(matching_entry: Dict[str, Any]) -> dict:
	"""
	Attach the valid security groups to the matching ELBv2 ARNs.

	Args:
		matching_entry (Dict[str, Any]): A dictionary representing the matching CSV entry.
	Returns:
		Compliance Status (Dict[str, Any): The submitted dictionary, along with whether the security group specified is attached or not.
	"""
	return_response = matching_entry.copy()
	return_response.update({"Compliant": False, "Success": False, "SecurityGroupsAttached": None, "ErrorMessage": ""})
	try:
		elbv2_arn = matching_entry["arn"]
		elbv2_response = boto3.client("elbv2").describe_load_balancers(LoadBalancerArns=[elbv2_arn])
		elbv2_security_groups = jmespath.search("LoadBalancers[].SecurityGroups", elbv2_response)[0]

		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if elbv2_security_groups == []:
			error_message = f'No security groups applied to resource: {matching_entry["arn"]}'
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": elbv2_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		elif not matching_entry["security_group"] in elbv2_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} is not attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": elbv2_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		elif matching_entry["security_group"] in elbv2_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} found attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": elbv2_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : True})

		# Secondary Case: there are no ELBv2s to attach
		elif elbv2_response["LoadBalancers"] == []:
			error_message = f"ELBv2 {elbv2_arn} not found"
			logging.error(error_message)
			return_response.update({"ErrorMessage": error_message,
			                        "Success"     : False,
			                        "Compliant"   : False})
		else:
			error_message = "Provided ELBv2 did not meet use cases. Skipping"
			logging.info(error_message)
			return_response.update({"ErrorMessage": error_message,
			                        "Success"     : False,
			                        "Compliant"   : False})

	except botocore.exceptions.ClientError as e:
		error_message = (f"Error validating security group {matching_entry['security_group']} to ELBv2 {matching_entry['arn']}: \n"
		                 f"Error: {e}")
		logging.error(error_message)
		return_response.update({"ErrorMessage": error_message,
		                        "Success"     : False,
		                        "Compliant"   : False})
	return return_response


def validate_security_groups_to_ec2(matching_entry: Dict[str, Any]) -> dict:
	# def validate_security_groups_to_ec2(matching_entry: Dict[str, Any]):
	"""
	Validate that the valid security groups to the matching EC2 ARNs.

	Args:
		matching_entry (Dict[str, Any]): A dictionary representing the matching CSV entry.
	Returns:
		Compliance Status (Dict[str, Any, bool, bool, List, str]): The submitted dictionary, along with whether the security group specified is attached or not.
	"""
	return_response = matching_entry.copy()
	return_response.update({"Compliant": False, "Success": False, "ErrorMessage": ""})
	try:
		ec2_id = matching_entry["arn"].split("/")[1]
		ec2_response = boto3.client("ec2").describe_instances(InstanceIds=[ec2_id])
		ec2_security_groups = jmespath.search(
			"Reservations[].Instances[].SecurityGroups[].GroupId",
			ec2_response,
			)

		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if ec2_security_groups == []:
			error_message = f'No security groups applied to resource: {matching_entry["arn"]}'
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": ec2_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		elif not matching_entry["security_group"] in ec2_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} is not attached to {matching_entry["arn"]}'
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": ec2_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		elif matching_entry["security_group"] in ec2_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} found attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": ec2_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : True})

		# Secondary Case: there are no EC2s to attach
		elif ec2_response["Reservations"] == []:
			error_message = f"EC2 {ec2_id} not found"
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})

		else:
			error_message = f"Provided EC2 Instances {ec2_id} did not meet use cases. Skipping"
			logging.debug(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})

	except botocore.exceptions.ClientError as e:
		error_message = (f"Error attaching security group {matching_entry['security_group']} to EC2 {matching_entry['arn']}. \n"
		                 f"Error: {e}")
		logging.debug(error_message)
		return_response.update({"ErrorMessage"          : error_message,
		                        "SecurityGroupsAttached": None,
		                        "Success"               : True,
		                        "Compliant"             : True})
	return return_response


def validate_security_groups_to_ecs_task(matching_entry: Dict[str, Any]) -> dict:
	"""
	Validate that the valid security groups to the matching EC2 ARNs.

	Args:
		matching_entry (Dict[str, Any]): A dictionary representing the matching CSV entry.
	Returns:
		Compliance Status (Dict[str, Any, bool, bool, List, str]): The submitted dictionary, along with whether the security group specified is attached or not.
	"""
	return_response = matching_entry.copy()
	return_response.update({"Compliant": False, "Success": False, "SecurityGroupsAttached": None, "ErrorMessage": ""})
	try:
		cluster_name = matching_entry["arn"].split("/")[1]
		service_name = matching_entry["arn"].split("/")[2]
		ecs_service_response = boto3.client("ecs").describe_services(
			cluster=cluster_name, services=[service_name])

		if ecs_service_response != []:
			ecs_security_group_ids = jmespath.search(
				"services[].networkConfiguration.awsvpcConfiguration.securityGroups",
				ecs_service_response)[0]
			# Primary Case: Security Group not in security rules and there could be 0+ security groups.
			if not ecs_security_group_ids:
				error_message = f'No security groups applied to resource: {matching_entry["arn"]}'
				logging.info(error_message)
				return_response.update({"ErrorMessage"          : error_message,
				                        "SecurityGroupsAttached": ecs_security_group_ids,
				                        "Success"               : True,
				                        "Compliant"             : False})
			elif matching_entry["security_group"] in ecs_security_group_ids:
				error_message = f'Security group {matching_entry["security_group"]} found attached to {matching_entry["arn"]}'
				logging.info(error_message)
				return_response.update({"ErrorMessage"          : error_message,
				                        "SecurityGroupsAttached": ecs_security_group_ids,
				                        "Success"               : True,
				                        "Compliant"             : True})
			elif not matching_entry["security_group"] in ecs_security_group_ids:
				error_message = f'Security group {matching_entry["security_group"]} is not attached to {matching_entry["arn"]}'
				logging.info(error_message)
				return_response.update({"ErrorMessage"          : error_message,
				                        "SecurityGroupsAttached": ecs_security_group_ids,
				                        "Success"               : True,
				                        "Compliant"             : False})
			# Secondary Case: there are no ECS Services to attach
			elif ecs_service_response == []:
				error_message = f"ECS {matching_entry['arn']} not found"
				logging.info(error_message)
				return_response.update({"ErrorMessage"          : error_message,
				                        "SecurityGroupsAttached": None,
				                        "Success"               : False,
				                        "Compliant"             : False})
			else:
				error_message = "Provided ECS Services did not meet use cases. Skipping"
				logging.debug(error_message)
				return_response.update({"ErrorMessage"          : error_message,
				                        "SecurityGroupsAttached": None,
				                        "Success"               : False,
				                        "Compliant"             : False})

		else:
			error_message = f"Cluster '{cluster_name}' not found."
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})

	except botocore.exceptions.ClientError as e:
		error_message = (f"Error validating security group {matching_entry['security_group']} to EC2 {matching_entry['arn']}. \n"
		                 f"Error: {e}")
		logging.info(error_message)
		return_response.update({"ErrorMessage"          : error_message,
		                        "SecurityGroupsAttached": None,
		                        "Success"               : False,
		                        "Compliant"             : False})
	return return_response


def validate_security_groups_to_rds(matching_entry: Dict[str, Any]) -> dict:
	"""
	Attach the valid security groups to the matching RDS ARNs.

	Args:
		matching_entry (Dict[str, Any]): A dictionary representing the matching CSV entry.
	Returns:
		Compliance Status (Dict[str, Any, bool, bool, list | None, str]): The submitted dictionary, along with whether the security group specified is attached or not.

	"""
	return_response = matching_entry.copy()
	return_response.update({"Compliant": False, "Success": False, "SecurityGroupsAttached": None, "ErrorMessage": ""})
	try:
		rds_response = boto3.client("rds").describe_db_instances(
			DBInstanceIdentifier=matching_entry["arn"])
		rds_security_groups = jmespath.search(
			"DBInstances[].VpcSecurityGroups[].VpcSecurityGroupId", rds_response)
		rds_instance_id = jmespath.search("DBInstances[].DBInstanceIdentifier", rds_response)[0]

		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if not rds_security_groups:
			error_message = f'No security groups applied to resource: {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": rds_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		elif matching_entry["security_group"] in rds_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} found attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": rds_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : True})

		elif not matching_entry["security_group"] in rds_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} not found attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": rds_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})

		# Secondary Case: there are no RDS Instances to attach
		elif not rds_response["DBInstances"]:
			error_message = f"RDS {matching_entry['arn']} not found"
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})
		else:
			error_message = "Provided RDS Instances did not meet use cases. Skipping"
			logging.debug(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})

	except botocore.exceptions.ClientError as e:
		error_message = (f"Error attaching security group {matching_entry['security_group']} to RDS {matching_entry['arn']}: \n"
		                 f"Error: {e}")
		logging.debug(error_message)
		return_response.update({"ErrorMessage"          : error_message,
		                        "SecurityGroupsAttached": None,
		                        "Success"               : False,
		                        "Compliant"             : False})
	return return_response


def validate_security_groups_to_lambda(matching_entry: Dict[str, Any]) -> dict:
	"""
	Attach the valid security groups to the matching Lambda ARNs.

	Args:
		matching_entry (Dict[str, Any]): A dictionary representing the matching CSV entry.
	Returns:
		Compliance Status (Dict[str, Any, bool, bool, list | None, str]): The submitted dictionary, along with whether the security group specified is attached or not.

	"""
	return_response = matching_entry.copy()
	return_response.update({"Compliant": False, "Success": False, "SecurityGroupsAttached": None, "ErrorMessage": ""})
	try:
		lambda_arn = matching_entry["arn"]
		lambda_response = boto3.client("lambda").get_function(FunctionName=lambda_arn)
		lambda_security_groups = jmespath.search("Configuration.VpcConfig.SecurityGroupIds", lambda_response)

		# Primary Case: Security Group not in security rules and there could be 0+ security groups.
		if not lambda_security_groups:
			error_message = f'No security groups applied to resource: {matching_entry["arn"]}'
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": lambda_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		elif matching_entry["security_group"] in lambda_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} found attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": lambda_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : True})
		elif not matching_entry["security_group"] in lambda_security_groups:
			error_message = f'Security group {matching_entry["security_group"]} is not attached to {matching_entry["arn"]}'
			logging.info(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": lambda_security_groups,
			                        "Success"               : True,
			                        "Compliant"             : False})
		# Second Case: there are no Lambda Functions to attach
		elif not lambda_response:
			error_message = f"Lambda {matching_entry['arn']} not found"
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})
		else:
			error_message = f"Provided Lambda Function {matching_entry['arn']} did not meet use cases. Skipping"
			logging.error(error_message)
			return_response.update({"ErrorMessage"          : error_message,
			                        "SecurityGroupsAttached": None,
			                        "Success"               : False,
			                        "Compliant"             : False})

	except botocore.exceptions.ClientError as e:
		error_message = (f"Error attaching security group {matching_entry['security_group']} to EC2 {matching_entry['arn']}. \n"
		                 f"Error: {e}")
		logging.error(error_message)
		return_response.update({"ErrorMessage"          : error_message,
		                        "SecurityGroupsAttached": None,
		                        "Success"               : False,
		                        "Compliant"             : False})
	return return_response


if __name__ == "__main__":
	main(CSV_FILE)
