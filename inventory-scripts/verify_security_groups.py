# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http://aws.amazon.com/agreement or other written agreement between Customer and either
# Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.

import csv, logging, jmespath, os
import boto3, botocore
from Inventory_Modules import find_account_instances2
from typing import Any, Dict, List

__version__ = '2024.09.04'
# import time

# Global Variables
CSV_FILE = os.getenv("CSV_FILE", "./all.csv")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", logging.ERROR)
FILENAME_TO_SAVE_TO = os.getenv("VERIFY_FILENAME", "results.csv")
FIND_EVERYTHING = os.getenv("FIND_EVERYTHING", True)


##################
# Functions
##################


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

	display_dict = {'arn'                   : {'DisplayOrder': 1, 'Heading': 'ARN'},
	                'Success'               : {'DisplayOrder': 2, 'Heading': 'Success', 'Condition': ['False', 'false', False]},
	                'Compliant'             : {'DisplayOrder': 3, 'Heading': 'Compliance', 'Condition': ['False', 'false', False]},
	                'SecurityGroupsAttached': {'DisplayOrder': 4, 'Heading': 'SecGrps Attached'},
	                'security_group_name'   : {'DisplayOrder': 5, 'Heading': 'Requested Sec Grp Name'},
	                'security_group'        : {'DisplayOrder': 6, 'Heading': 'Requested Sec Grp ID'},
	                'ErrorMessage'          : {'DisplayOrder': 7, 'Heading': 'Error Message'}}
	# Script only supports validation, and not attachment.
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
		display_results(results, display_dict, None, FILENAME_TO_SAVE_TO)
		print(f"Finished validation with {successful_results} successful checks and {compliant_results} compliant resources out of a total of {len(matching_entries)} requested resources.")
	except Exception as e:
		logging.error(f"ERROR: Unable to validate security groups. Error Message: {e}")

	if FIND_EVERYTHING in ['True', True]:
		all_arns = find_all_arns(matching_entries, account_id, region)

	print("Finalized script. Exiting")


def current_contextual_identity():
	"""
	Identify the current account id and region using a Boto3 call.

	Args:
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
			reader = csv.DictReader(csv_file, delimiter=',')
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
	all_security_groups = get_security_groups()
	for entry in csv_data:
		# Test 1: Check to see if Account ID and Region match
		# Test 2: Check to see if the Security Group is valid
		# Test 3: Check to see if the Security Group name is unique (multiple sgs named "default" is possible given multiple VPCs)
		# If Test 1 and Test 2 pass - add to matching entries (after stripping all whitespace, tabs, etc.)
		logging.info(f"Entry: {entry}")
		try:
			target_account_id = entry["arn"].strip().split(":")[4]
			target_region = entry["arn"].strip().split(":")[3]
			security_group_name = str(entry["security_group"].strip()).lower()
			security_group_id = get_security_group_id_from_name(security_group_name, all_security_groups)

			if (target_account_id == account_id and target_region == region) and security_group_id != '':
				clean_entry = {
					"arn"                : entry["arn"].strip(),
					"security_group_name": security_group_name,
					"security_group"     : security_group_id,
					}
				matching_entries.append(clean_entry)

			if matching_entries == []:
				logging.info("No matching entries found, returning empty list")
		except Exception as e:
			logging.error(f"Error processing entry: {e}")
			
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


def get_security_groups() -> List[str]:
	"""
	Get the Security Group ID from the Security Group Name. Returns a list of matching security group IDs.

	Args:
	Returns:
		List[str]: A list of matching security group IDs.
	"""
	try:
		security_group_response = boto3.client("ec2").describe_security_groups()
		security_group_response2 = dict_lower(security_group_response.copy())
		return security_group_response2
	except Exception as e:
		logging.error(f"Had a problem retrieving security groups: {e}")

def get_security_group_id_from_name(security_group_name: str, security_group_response:dict) -> str:
	"""
	Get the Security Group ID from the Security Group Name. Returns sg-id or empty string

	Args:
		security_group_name (Dict[str, Any]): The security group name dictionary.
		security_group_response (Dict[str, Any]): The security group response dictionary (lowercased).
	Returns:
		str: Security Group ID
	"""
	try:
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


def dict_lower(dict_object:dict) -> dict:
	"""
	Convert all keys and values in a dictionary to lowercase.

	Args:
		dict_object (dict): The dictionary to convert.
	Returns:
		dict: The dictionary with all keys and values converted to lowercase.
	"""
	def handle_int(item:int)->int:
		return item

	def handle_string(item:str)->str:
		return item.lower()

	def handle_list(item:list)->list:
		for i in item:
			if type(i) == int:
				item[item.index(i)] = handle_int(i)
			elif type(i) == str:
				item[item.index(i)] = handle_string(i)
			elif type(i) == dict:
				item[item.index(i)] = dict_lower(i)
		return item

	for k,v in dict_object.items():
		logging.info(f"Pre change - Key: {k}, Value: {v}")
		value_type = type(dict_object[k])
		if type(dict_object[k]) == int:
			dict_object[k] = handle_int(dict_object[k])
		elif type(dict_object[k]) == str:
			dict_object[k] = handle_string(dict_object[k])
		elif type(dict_object[k]) == dict:
			logging.info(f"Recursive dict - {dict_object[k]}")
			dict_object[k] = dict_lower(dict_object[k].copy())
		elif type(dict_object[k]) == list:
			logging.info(f"List - {dict_object[k]}")
			dict_object[k] = handle_list(dict_object[k])
		logging.info(f"Post change {value_type} - Value: {dict_object[k]}")
	return dict_object


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
		if not elbv2_security_groups:
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
		error_message = (f"Error validating security group {matching_entry['security_group']} to ELBv2 {matching_entry['arn']}:"
		                 f"Error: {e}")
		logging.error(error_message)
		return_response.update({"ErrorMessage": error_message,
		                        "Success"     : False,
		                        "Compliant"   : False})
	except Exception as e:
		error_message = (f"Problem finding security groups attached to {matching_entry['arn']}"
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
		elif not ec2_response["Reservations"]:
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

		# Simplified way of saying "Not a null response"
		if ecs_service_response:
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
			elif not ecs_service_response:
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


def find_all_arns(matching_entries: List[Dict[str, Any]], account_id, region) -> list:
	"""
	@Description: This function will find the arns in the account (and region) so that QA can validate they've covered all resources expected.
		Resource Types covered thus far:
			- EC2
			- Lambda
			- ECS
			- Load Balancers
			- RDS
	@matching_entries: a list of the arns that *are* known, so these can be either filtered out, or something...
	@return: list of dicts, with arns and types
	"""
	try:
		multiple_responses = []
		supported_resource_types = ['ec2', 'ecs', 'rds', 'elasticloadbalancing', 'lambda']
		for resource_type in supported_resource_types:
			if resource_type == 'ec2':
				list_of_ec2_arns = find_all_ec2_arns(account_id, region)
				single_response = {'Success': True, 'Account': account_id, 'Region': region, 'ResourceType': resource_type, 'ARNs': list_of_ec2_arns, 'ErrorMessage': None}
			# elif resource_type == 'ecs':
			# 	single_response = find_all_ecs_arns()
			# elif resource_type == 'rds':
			# 	single_response = find_all_rds_arns()
			# elif resource_type == 'elasticloadbalancing':
			# 	single_response = find_all_elasticloadbalancing_arns()
			# elif resource_type == 'lambda':
			# 	single_response = find_all_lambda_arns()
			else:
				error_message = f"Unsupported resource type: {resource_type}"
				logging.error(error_message)
				single_response = {'Success': False, 'Account': account_id, 'Region': region, 'ResourceType': resource_type, 'ARNs': None, 'ErrorMessage': error_message}
			multiple_responses.append(single_response)
	except Exception as e:
		error_message = (f"ERROR: Finding all arns: {e}"
		                 f"Resource Type: {resource_type}")
		single_response = {'Success': False, 'Account': account_id, 'Region': region, 'ResourceType': resource_type, 'ARNs': None, 'ErrorMessage': error_message}

		return [single_response]

	return multiple_responses


def find_all_ec2_arns(account_id: str, region: str) -> list:
	"""
	@Description: This function will find all EC2 ARNs in the account (and region)
	@account_id: The account ID to search for instances in
	@region: The region to search for instances in
	@return: list of the ec2_arns found in the account/region
	"""

	try:
		ec2_response = find_account_instances2()
		ec2_instances = jmespath.search("Reservations[].Instances[].InstanceId", ec2_response)
		ec2_arns = []
		for instance in ec2_instances:
			instance_arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance}"
			ec2_arns.append(instance_arn)
		return ec2_arns
	except Exception as e:
		logging.error(f"Failed to get instances from account {account_id} and region {region} | {e}")
		return None
def find_all_ecs_arns(account_id: str, region: str) -> list:
	"""
	@Description: This function will find all ECS ARNs in the account (and region)
	@account_id: The account ID to search for instances in
	@region: The region to search for instances in
	@return: list of the ecs_arns found in the account/region
	"""

	try:
		ec2_response = find_account_instances2()
		ec2_instances = jmespath.search("Reservations[].Instances[].InstanceId", ec2_response)
		ec2_arns = []
		for instance in ec2_instances:
			instance_arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance}"
			ec2_arns.append(instance_arn)
		return ec2_arns
	except Exception as e:
		logging.error(f"Failed to get instances from account {account_id} and region {region} | {e}")
		return None


def display_results(results_list, fdisplay_dict: dict, defaultAction=None, file_to_save: str = None, subdisplay: bool = False):
	from colorama import init, Fore
	from datetime import datetime

	init()
	"""
	Note that this function simply formats the output of the data within the list provided
	@param: results_list: This should be a list of dictionaries, matching to the fields in fdisplay_dict
	@param: fdisplay_dict: Should look like the below. It's simply a list of fields and formats
	@param: defaultAction: this is a default string or type to assign to fields that (for some reason) don't exist within the results_list.
	@param: file_to_save: If you want to save the output to a file, specify the filename here.
	display_dict = {'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'},
	                'MgmtAccount'  : {'DisplayOrder': 2, 'Heading': 'Mgmt Acct'},
	                'AccountId'    : {'DisplayOrder': 3, 'Heading': 'Acct Number'},
	                'Region'       : {'DisplayOrder': 4, 'Heading': 'Region', 'Condition': ['us-east-2']},
	                'Retention'    : {'DisplayOrder': 5, 'Heading': 'Days Retention', 'Condition': ['Never']},
	                'Name'         : {'DisplayOrder': 7, 'Heading': 'CW Log Name'},
                    'Size'         : {'DisplayOrder': 6, 'Heading': 'Size (Bytes)'}}
		- The first field ("MgmtAccount") should match the field name within the list of dictionaries you're passing in (results_list)
		- The first field within the nested dictionary is the SortOrder you want the results to show up in
		- The second field within the nested dictionary is the heading you want to display at the top of the column (which allows spaces)
		- The third field ('Condition') is new, and allows to highlight a special value within the output. This can be used multiple times. 
		The dictionary doesn't have to be ordered, as long as the 'SortOrder' field is correct.

		Enhancements:
			- How to create a break between rows, like after every account, or Management Org, or region, or whatever...
			- How to do sub-sections, where there is more data to show per row...  
	"""

	def handle_list():
		# If no results were passed, print nothing and just return
		if len(results_list) == 0:
			logging.warning("There were no results passed in to display")
			return

		# TODO:
		# 	Probably have to do a pre-emptive error-check to ensure the SortOrder is unique within the Dictionary
		# 	Also need to enclose this whole thing in a try...except to trap errors.
		# 	Decided not to try to order the data passed in, as that should be done within the original function

		sorted_display_dict = dict(sorted(fdisplay_dict.items(), key=lambda x: x[1]['DisplayOrder']))

		# This is an effort to find the right size spaces for the dictionary to properly show the results
		print()
		needed_space = {}
		for field, value in sorted_display_dict.items():
			needed_space[field] = 0
		try:
			for result in results_list:
				for field, value in sorted_display_dict.items():
					if field not in result:
						needed_space[field] = max(len(value['Heading']), needed_space[field])
						continue
					elif isinstance(result[field], bool):
						# Recognizes the field as a Boolean, and finds the necessary amount of space to show that data, and assigns the length to "needed_space"
						# I use "5" as the minimum space, to show that displaying "False" would take up 5 spaces...
						needed_space[field] = max(5, len(value['Heading']), needed_space[field])
					elif isinstance(result[field], int):
						# This section is to compensate for the fact that the len of numbers in string format doesn't include the commas.
						# I know - I've been very US-centric here, since I haven't figured out how to achieve this in a locale-agnostic way
						num_width = len(str(result[field]))
						if len(str(result[field])) % 3 == 0:
							num_width += (len(str(result[field])) // 3) - 1
						else:
							num_width += len(str(result[field])) // 3
						needed_space[field] = max(num_width, len(value['Heading']), needed_space[field])
					elif isinstance(result[field], float):
						# This section is to compensate for the fact that the len of numbers in string format doesn't include the commas.
						# I know - I've been very US-centric here, since I haven't figured out how to achieve this in a locale-agnostic way
						num_width = len(str(result[field]))
						if len(str(result[field])) % 3 == 0:
							num_width += (len(str(result[field])) // 3) - 1
						else:
							num_width += len(str(result[field])) // 3
						needed_space[field] = max(num_width, len(value['Heading']), needed_space[field])
					elif isinstance(result[field], str):
						# Recognizes the field as a string, and finds the necessary amount of space to show that data, and assigns the length to "needed_space"
						needed_space[field] = max(len(result[field]), len(value['Heading']), needed_space[field])
					elif isinstance(result[field], datetime):
						# Recognizes the field as a date, and finds the necessary amount of string space to show that date, and assigns the length to "needed_space"
						needed_space[field] = max(len(datetime.now().strftime('%x %X')), len(value['Heading']))
					else:
						# In case the field is a list or dict - for a subdisplay...
						needed_space[field] = max(len(value['Heading']), needed_space[field])
		except KeyError as my_Error:
			logging.error(f"Error: {my_Error}")

		# This writes out the headings
		print("\t", end='') if subdisplay else None
		for field, value in sorted_display_dict.items():
			# If this is a sub-display field, there's no need to write out the heading above
			if 'SubDisplay' in value.keys():
				continue
			header_format = needed_space[field]
			print(f"{value['Heading']:{header_format}s} ", end='')
		# Newline at the end of the headings
		print()
		# This writes out the dashes (separators)
		print("\t", end='') if subdisplay else None
		for field, value in sorted_display_dict.items():
			# If this is a sub-display field, there's no need to write out the heading above
			if 'SubDisplay' in value.keys():
				continue
			repeatvalue = needed_space[field]
			print(f"{'-' * repeatvalue} ", end='')
		# Newline after the dashes
		print()

		# This writes out the data
		for result in results_list:
			print("\t", end='') if subdisplay else None
			for field, value in sorted_display_dict.items():
				# This determines whether ths row provided is supposed to be displayed as a sub-report of the main row
				if 'SubDisplay' in value.keys():
					SubDisplay = True
				else:
					SubDisplay = False
				# This assigns the proper space for the output
				data_format = needed_space[field]
				if field not in result.keys():
					result[field] = defaultAction
				# This allows for a condition to highlight a specific value
				highlight = False
				if 'Condition' in value and result[field] in value['Condition']:
					highlight = True
				if result[field] is None:
					print(f"{'':{data_format}} ", end='')
				elif isinstance(result[field], str):
					print(f"{Fore.RED if highlight else ''}{result[field]:{data_format}s}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(result[field], bool):
					# This is needed, otherwise it prints "0" for False and "1" for True... Essentially treating the bool like an integer.
					if result[field]:
						display_text = 'True'
					else:
						display_text = 'False'
					print(f"{Fore.RED if highlight else ''}{display_text:{data_format}s}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(result[field], int):
					print(f"{Fore.RED if highlight else ''}{result[field]:<{data_format}{',' if 'Delimiter' in value.keys() and value['Delimiter'] else ''}}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(result[field], float):
					print(f"{Fore.RED if highlight else ''}{result[field]:{data_format}f}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(result[field], datetime):
					print(f"{Fore.RED if highlight else ''}{result[field].strftime('%x %X')}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(result[field], list) and SubDisplay:
					# Re-use this same function - but with the sub-data used for display, while passing in that this is a "sub-display" to indent the new records.
					display_results(result[field], value['SubDisplay'], None, subdisplay=SubDisplay)
				elif isinstance(result[field], list):
					# This is a cheat, since I'm using this function for a specific use for the "find_security_groups.py" script
					for item in result[field]:
						if isinstance(item, dict):
							logging.debug(f"Item is a dictionary - {item}")
							if 'CidrIp' in item.keys() and 'Description' in item.keys():
								print(f"{Fore.RED if highlight else ''}{item['CidrIp']} ({item['Description']}){Fore.RESET if highlight else ''}, ", end='')
							elif 'CidrIp' in item.keys():
								print(f"{Fore.RED if highlight else ''}{item['CidrIp']}{Fore.RESET if highlight else ''}, ", end='')
							elif 'GroupId' in item.keys() and 'Description' in item.keys():
								print(f"{Fore.RED if highlight else ''}{item['GroupId']} ({item['Description']}){Fore.RESET if highlight else ''}, ", end='')
							elif 'GroupId' in item.keys():
								print(f"{Fore.RED if highlight else ''}{item['GroupId']}{Fore.RESET if highlight else ''}, ", end='')
							elif 'PrefixListId' in item.keys() and 'Description' in item.keys():
								print(f"{Fore.RED if highlight else ''}{item['PrefixListId']} ({item['Description']}){Fore.RESET if highlight else ''}, ", end='')
							elif 'PrefixListId' in item.keys():
								print(f"{Fore.RED if highlight else ''}{item['PrefixListId']}{Fore.RESET if highlight else ''}, ", end='')
						else:
							print(f"{Fore.RED if highlight else ''}{item}{Fore.RESET if highlight else ''}, ", end='')
			print()  # This is the end of line character needed at the end of every line
		print()  # This is the new line needed at the end of the script.
		# TODO: We need to add some analytics here... Trying to come up with what would make sense across all displays.
		#   Possibly we can have a setting where this data is written to a csv locally. We could create separate analytics once the data was saved.

		# This is where the data is written to a file
		if file_to_save is not None:
			Heading = ''
			my_filename = f'{file_to_save.split(".")[0]}-{datetime.now().strftime("%y-%m-%d--%H-%M-%S")}.csv'
			logging.info(f"Writing your data to: {my_filename}")
			try:
				with open(my_filename, 'w') as savefile:
					for field, value in sorted_display_dict.items():
						Heading += f"{value['Heading']}|"
					Heading += '\n'
					savefile.write(Heading)
					logging.debug(f"Writing {len(results_list)} rows of the result to the savefile")
					for result in results_list:
						row = ''
						for field, value in sorted_display_dict.items():
							data_format = 0
							if field not in result.keys():
								result[field] = defaultAction
							if result[field] is None:
								row += "|"
							elif isinstance(result[field], str):
								# row += f"{result[field]:{data_format}s}|"
								row += f"{result[field]:s}|"
							elif isinstance(result[field], bool):
								if result[field]:
									row += f"True|"
								else:
									row += f"False|"
							elif isinstance(result[field], int):
								row += f"{result[field]:<{data_format},}|"
							elif isinstance(result[field], float):
								row += f"{result[field]:{data_format}f}|"
							elif isinstance(result[field], datetime):
								row += f"{result[field].strftime('%c')}|"
						row += '\n'
						savefile.write(row)
				print(f"Data written to {my_filename}")
			except Exception as e:
				logging.error(f"Error writing to file: {e}")

	def handle_dict():
		# If no results were passed, print nothing and just return
		if len(results_list) == 0:
			logging.warning("There were no results passed in to display")
			return

		# TODO:
		# 	Probably have to do a pre-emptive error-check to ensure the SortOrder is unique within the Dictionary
		# 	Also need to enclose this whole thing in a try...except to trap errors.
		# 	Also need to find a way to order the data within this function.

		sorted_display_dict = dict(sorted(fdisplay_dict.items(), key=lambda x: x[1]['DisplayOrder']))

		# This is an effort to find the right size spaces for the dictionary to properly show the results
		print()
		needed_space = {}
		for field, value in sorted_display_dict.items():
			needed_space[field] = 0
		try:
			for row, row_data in results_list.items():
				for field, value in sorted_display_dict.items():
					if field == row:
						needed_space[field] = max(len(value['Heading']), needed_space[field])
						continue
					elif field not in row_data.keys():
						needed_space[field] = max(len(value['Heading']), needed_space[field])
						continue
					elif isinstance(row_data[field], bool):
						# Recognizes the field as a Boolean, and finds the necessary amount of space to show that data, and assigns the length to "needed_space"
						# I use "5" as the minimum space, to show that displaying "False" would take up 5 spaces...
						needed_space[field] = max(5, len(value['Heading']), needed_space[field])
					elif isinstance(row_data[field], int):
						# This section is to compensate for the fact that the len of numbers in string format doesn't include the commas.
						# I know - I've been very US-centric here, since I haven't figured out how to achieve this in a locale-agnostic way
						num_width = len(str(row_data[field]))
						if len(str(row_data[field])) % 3 == 0:
							num_width += (len(str(row_data[field])) // 3) - 1
						else:
							num_width += len(str(row_data[field])) // 3
						needed_space[field] = max(num_width, len(value['Heading']), needed_space[field])
					elif isinstance(row_data[field], str):
						# Recognizes the field as a string, and finds the necessary amount of space to show that data, and assigns the length to "needed_space"
						needed_space[field] = max(len(row_data[field]), len(value['Heading']), needed_space[field])
					elif isinstance(row_data[field], datetime):
						# Recognizes the field as a date, and finds the necessary amount of string space to show that date, and assigns the length to "needed_space"
						# needed_space[field] = max(len(result[field]), len(datetime.now().strftime('%x %X')))
						needed_space[field] = max(len(datetime.now().strftime('%x %X')), len(value['Heading']))
		except KeyError as my_Error:
			logging.error(f"Error: {my_Error}")

		# This writes out the headings
		for field, value in sorted_display_dict.items():
			header_format = needed_space[field]
			print(f"{value['Heading']:{header_format}s} ", end='')
		print()
		# This writes out the dashes (separators)
		for field, value in sorted_display_dict.items():
			repeatvalue = needed_space[field]
			print(f"{'-' * repeatvalue} ", end='')
		print()

		# This writes out the data
		for row, row_data in results_list.items():
			for field, value in sorted_display_dict.items():
				# This assigns the proper space for the output
				data_format = needed_space[field]
				if field not in row_data.keys():
					row_data[field] = defaultAction
				# This allows for a condition to highlight a specific value
				highlight = False
				if 'Condition' in value and row_data[field] in value['Condition']:
					highlight = True
				if row_data[field] is None:
					print(f"{'':{data_format}} ", end='')
				elif isinstance(row_data[field], str):
					print(f"{Fore.RED if highlight else ''}{row_data[field]:{data_format}s}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(row_data[field], bool):
					# This is needed, otherwise it prints "0" for False and "1" for True... Essentially treating the bool like an integer.
					if row_data[field]:
						display_text = 'True'
					else:
						display_text = 'False'
					print(f"{Fore.RED if highlight else ''}{display_text:{data_format}s}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(row_data[field], int):
					print(f"{Fore.RED if highlight else ''}{row_data[field]:<{data_format},}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(row_data[field], float):
					print(f"{Fore.RED if highlight else ''}{row_data[field]:{data_format}f}{Fore.RESET if highlight else ''} ", end='')
				elif isinstance(row_data[field], datetime):
					print(f"{Fore.RED if highlight else ''}{row_data[field].strftime('%x %X')}{Fore.RESET if highlight else ''} ", end='')
			print()  # This is the end of line character needed at the end of every line
		print()  # This is the new line needed at the end of the script.
		# TODO: We need to add some analytics here... Trying to come up with what would make sense across all displays.
		#   Possibly we can have a setting where this data is written to a csv locally. We could create separate analytics once the data was saved.
		if file_to_save is not None:
			Heading = ''
			my_filename = f'{file_to_save}-{datetime.now().strftime("%y-%m-%d--%H-%M-%S")}'
			logging.info(f"Writing your data to: {my_filename}")
			with open(my_filename, 'w') as savefile:
				for field, value in sorted_display_dict.items():
					Heading += f"{value['Heading']}|"
				Heading += '\n'
				savefile.write(Heading)
				for row, row_data in results_list.items():
					row = ''
					for field, value in sorted_display_dict.items():
						data_format = 0
						if field not in row_data.keys():
							row_data[field] = defaultAction
						if row_data[field] is None:
							row += "|"
						elif isinstance(row_data[field], str):
							row += f"{row_data[field]:{data_format}s}|"
						elif isinstance(row_data[field], int):
							row += f"{row_data[field]:<{data_format},}|"
						elif isinstance(row_data[field], float):
							row += f"{row_data[field]:{data_format}f}|"
					row += '\n'
					savefile.write(row)
			print(f"\nData written to {my_filename}\n")

	if isinstance(results_list, list):
		handle_list()
	elif isinstance(results_list, dict):
		# This doesn't work really yet, but it's a start
		handle_dict()


##################
# Main
##################

if __name__ == "__main__":
	main(CSV_FILE)
