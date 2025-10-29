from botocore import client
from botocore import session
# import pytest

ERASE_LINE = '\x1b[2K'


def AWSAccount_from_AWSKeyID(AWSKeyID):
	"""
	Determines the AWS Account number from the AWS Key ID.
	The original idea here: https://hackingthe.cloud/aws/enumeration/get-account-id-from-keys/
	@param AWSKeyID: This is a *fake* AWS Key in the format of "xxxx" (four characters)
	 and then should be the account number. We'll toss out the rest of the data as irrelevant
	@return: Returns the account number as a string
	"""
	trimmed_AWSKeyID = AWSKeyID[4:16]  # remove KeyID prefix
	return str(trimmed_AWSKeyID)


def AWSKeyID_from_AWSAccount(AWSAccountNumber):
	"""
	Makes up an AWS Key ID from the AWS Account number.
	@param AWSAccountNumber: This is the AWS Account number as a string
	@return: Returns the AWS Key ID as a string
	"""
	# An AWS Key looks like this: "AIDAJ74HIVAJJXOVUHYO6" (21 characters)
	AWSKey = f"xxxx{str(AWSAccountNumber)}xxxxx"
	return AWSKey


def _amend_create_boto3_session(test_data, verbosity, mocker):
	import logging
	logging.basicConfig(level=verbosity, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

	orig = session.Session.create_client

	def amend_create_client(
			self,
			service_name,
			region_name=None,
			api_version=None,
			use_ssl=True,
			verify=None,
			endpoint_url=None,
			aws_access_key_id=None,
			aws_secret_access_key=None,
			aws_session_token=None,
			config=None,
			):
		# Intercept boto3 Session, in hopes of sending back a client that includes the Account Number
		# if aws_access_key_id == '*****AccessKeyHere*****':
		logging.info(test_data['FunctionName'])
		if aws_access_key_id == 'MeantToFail':
			logging.info(f"Failed Access Key: {aws_access_key_id}")
			return ()
		else:
			logging.info(f"Not Failed Access Key: {aws_access_key_id}")
			return_response = orig(self,
			                       service_name,
			                       region_name,
			                       api_version,
			                       use_ssl,
			                       verify,
			                       endpoint_url,
			                       aws_access_key_id,
			                       aws_secret_access_key,
			                       aws_session_token,
			                       config)
			return return_response

	mocker.patch('botocore.session.Session.create_client', new=amend_create_client)
	print()


def _amend_make_api_call_orig(test_key, test_value, verbosity, mocker):
	import logging
	logging.basicConfig(level=verbosity, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

	orig = client.BaseClient._make_api_call

	def amend_make_api_call(self, operation_name, kwargs):
		# Intercept boto3 operations for <secretsmanager.get_secret_value>. Optionally, you can also
		# check on the argument <SecretId> and control how you want the response would be. This is
		# a very flexible solution as you have full control over the whole process of fetching a
		# secret.
		if operation_name == 'ListAccounts':
			if isinstance(test_value, Exception):
				raise test_value
			# Implied break and exit of the function here...
			logging.info(f"Operation Name mocked: {operation_name}\n"
			             f"Key Name: {test_key}\n"
			             f"kwargs: {kwargs}\n"
			             f"mocked return_response: {test_value}")
			return test_value

		return_response = orig(self, operation_name, kwargs)
		logging.info(f"Operation Name passed through: {operation_name}\n"
		             f"Key name: {test_key}\n"
		             f"kwargs: {kwargs}\n"
		             f"Actual return response: {return_response}")
		return return_response

	mocker.patch('botocore.client.BaseClient._make_api_call', new=amend_make_api_call)


def _amend_make_api_call(meta_key_dict, test_dict, verbosity, mocker):
	import logging
	logging.basicConfig(level=verbosity, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

	orig = client.BaseClient._make_api_call

	def amend_make_api_call(self, operation_name, kwargs):
		# Intercept boto3 operations for <secretsmanager.get_secret_value>. Optionally, you can also
		# check on the argument <SecretId> and control how you want the response would be. This is
		# a very flexible solution as you have full control over the whole process of fetching a
		# secret.
		for op_name in test_dict:
			test_value = op_name['test_result']
			region = self.meta.region_name
			if operation_name == op_name['operation_name']:
				if isinstance(test_value, Exception):
					# Implied break and exit of the function here...
					raise test_value
				logging.info(f"Operation Name mocked: {operation_name}\n"
				             f"Function Name: {meta_key_dict['FunctionName']}\n"
				             f"kwargs: {kwargs}\n"
				             f"mocked return_response: {op_name['test_result']}")
				return op_name['test_result']
		try:
			logging.info(f"Trying: Operation Name passed through: {operation_name}\n"
			             f"Key Name: {meta_key_dict['FunctionName']}\n"
			             f"kwargs: {kwargs}\n")
			return_response = orig(self, operation_name, kwargs)
			logging.info(f"Actual return_response: {return_response}")
		except Exception as my_Error:
			raise ConnectionError("Operation Failed")
		return return_response

	mocker.patch('botocore.client.BaseClient._make_api_call', new=amend_make_api_call)


def _amend_make_api_call_specific(meta_key_dict, test_dict, verbosity, mocker):
	import logging
	logging.basicConfig(level=verbosity, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

	orig = client.BaseClient._make_api_call

	def amend_make_api_call(self, operation_name, kwargs):
		# Intercept boto3 operations for <secretsmanager.get_secret_value>. Optionally, you can also
		# check on the argument <SecretId> and control how you want the response would be. This is
		# a very flexible solution as you have full control over the whole process of fetching a
		# secret.
		# This goes through the operations in the dictionary and checks for each operation, whether it matches the operation we're patching right now.
		for op_name in test_dict:
			if operation_name == op_name['operation_name']:
				# We are able to capture the region from the API call, and use that to differentiate data to return
				region = self.meta.region_name
				# For the various sets of return data that we have...
				test_value = None
				for set_of_result_data in op_name['test_result']:
					# Check to see which set of return data matches the region we're calling for now...
					if set_of_result_data['Region'] == region:
						test_value = set_of_result_data['mocked_response']
						break
				if test_value is not None and isinstance(test_value, Exception):
					# Implied break and exit of the function here...
					logging.info("Expected Error...")
					raise test_value
				elif test_value is None:
					logging.info(f"No test data offered for this credentials in region {region}")
					continue
				logging.info(f"Operation Name mocked: {operation_name}\n"
				             f"Function Name: {meta_key_dict['FunctionName']}\n"
				             f"kwargs: {kwargs}\n"
				             f"mocked return_response: {test_value}")
				return test_value

		logging.info(f"Operation Name passed through: {operation_name}\n"
		             f"Function Name: {meta_key_dict['FunctionName']}\n"
		             f"kwargs: {kwargs}\n")
		return_response = orig(self, operation_name, kwargs)
		logging.info(f"Actual return_response: {return_response}")
		return return_response

	mocker.patch('botocore.client.BaseClient._make_api_call', new=amend_make_api_call)


# mocker.patch('botocore.session', new=amend_make_api_call)


def mock_find_all_instances2(creds: dict, region: str):
	"""
	This is a mock function that will return a list of all the instances in the region that we're looking for.
	:param creds: Credentials object, where 'AccountNumber' is the account number of the account that we're looking for.
	:param region: string for region we're checking
	:return: The output from the EC2 API for "list_instances"
	"""
	from Tests.common_test_data import All_Instances_Response_Data

	for mock_data_set in All_Instances_Response_Data:
		if mock_data_set['Region'] == region and mock_data_set['AccountNumber'] == creds['AccountNumber']:
			return mock_data_set['instance_data']
	raise KeyError(f"No data for {creds['AccountNumber']} found for region {region}")
