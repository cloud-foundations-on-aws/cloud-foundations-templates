"""
1. Accept either a single profile or multiple profiles
2. Determine if a profile (or multiple profiles) was provided
3. If a single profile was provided - determine whether it's been provided as an org account, or as a single profile
4. If the profile is of a root account, and it's supposed to be for the whole Org - **note that**
	Otherwise - treat it like a standalone account (like anything else)
5. If it's a root account, we need to figure out how to find all the child accounts, and the proper roles to access them by
	5a. Find all the child accounts
	5b. Find out if any of those children are SUSPENDED and remove them from the list
	5c. Figure out the right roles to access the children by - which might be a config file, since there might be a mapping for this.
	5d. Once we have a way to access all the children, we can provide account-credentials to access the children by (but likely not the root account itself)
	5e. Call the actual target scripts - with the proper credentials (which might be a profile, or might be a session token)
6. If it's not a root account - then ... just use it as a profile

What does a script need to satisfy credentials? It needs a boto3 session. From the session, everything else can derive... yes?

So if we create a class object that represented the account:
	Attributes:
		AccountID: Its 12-digit account number
		botoClient: Access into the account (profile, or access via a root path)
		MgmntAccessRoles: The role that the root account uses to get access
		AccountStatus: Whether it's ACTIVE or SUSPENDED
		AccountType: Whether it's a root org account, a child account or a standalone account
		ParentProfile: What its parent profile name is, if available
		If it's an Org account:
			ALZ: Whether the Org is running an ALZ
			CT: Whether the Org is running CT
	Functions:
		Which regions and partitions it's enabled for
		(Could all my inventory items be an attribute of this class?)

"""
import logging
from json.decoder import JSONDecodeError

import boto3
from botocore.exceptions import ClientError, ConnectionError, CredentialRetrievalError, EndpointConnectionError, NoCredentialsError, ProfileNotFound, UnknownRegionError

__version__ = "2025.04.11"  # (again)


def _validate_region(faws_prelim_session, fRegion=None):
	# Why are you trying to validate a region, and then didn't supply a region?
	# Or - common case - you supplied 'us-east-1' which we know to be valid, so we can just immediately return Success
	if fRegion is None and faws_prelim_session.region_name is not None:
		fRegion = faws_prelim_session.region_name
	if fRegion is None or fRegion == 'us-east-1':
		message = f"Either no region supplied to check or region is 'us-east-1'. Defaulting to 'us-east-1'"
		logging.info(message)
		fRegion = 'us-east-1'
		result = {
			'Success': True,
			'Message': message,
			'Region' : fRegion}
		return result
	else:
		try:
			# Since we have to run this command to get a listing of the possible regions, we have to use a region we know will work today...
			client_region = faws_prelim_session.client('ec2', region_name=fRegion)
			# all_regions_list = [region_name['RegionName'] for region_name in client_region.describe_regions(AllRegions=True)['Regions']]
			matching_regions = client_region.describe_regions(Filters=[{'Name': 'region-name', 'Values': [fRegion]}])['Regions']
		except Exception as my_Error:
			message = (f"Problem happened.\n"
			           f"Error Message: {my_Error}")
			result = {
				'Success': False,
				'Message': message,
				'Region' : fRegion}
			return result
	if matching_regions:
		message = f"{fRegion} is a valid region within AWS"
		result = {
			'Success': True,
			'Message': message,
			'Region' : fRegion}
		if matching_regions[0]['OptInStatus'] == 'not-opted-in':
			message = f"{fRegion} is a valid region within AWS, but this account hasn't opted into this region"
			result = {
				'Success': False,
				'Message': message,
				'Region' : fRegion}
		logging.info(message)
	else:
		message = f"'{fRegion}' is not valid region within this AWS partition"
		logging.info(message)
		result = {
			'Success': False,
			'Message': message,
			'Region' : fRegion}
	return result


class aws_acct_access:
	"""
	Class takes a boto3 session object as input
	Multiple attributes and functions exist within this class to give you information about the account
	Attributes:
		AccountStatus: Whether the account is Active or Inactive
		acct_number: The account number of the account
		AccountType: Whether the account is a "Root", "Child" or "Standalone" account
		MgmtAccount: If the account is a child, this is its Management Account
		OrgID: The Organization the account belongs to, if it does
		MgmtEmail: The email address of the Management Account, if the account is a "Root" or "Child"
		creds: The credentials used to get into the account
		Region: The region used to authenticate into this account. Important to find out if certain regions are allowed (opted-in).
		ChildAccounts: If the account is a "Root", this is a listing of the child accounts
	"""

	def __init__(self, fProfile=None, fRegion=None, ocredentials=None):
		"""
		Description: Returns an object representing the AWS account
		@param fProfile:
		@param fRegion:
		@param ocredentials:
		@rtype: object
		"""
		global prelim_session
		import os
		# First thing's first: We need to validate that the region they sent us to use is valid for this account.
		# Otherwise, all hell will break if it's not.
		UsingKeys = False
		UsingSessionToken = False
		UsingEnvVars = False
		# if fRegion is None:
		# 	fRegion = 'us-east-1'
		account_access_successful = False
		account_and_region_access_successful = False
		# If they provided an ocredentials object - this is rare.
		if ocredentials is not None and ocredentials['Success']:
			# Trying to instantiate a class, based on passed in credentials
			UsingKeys = True
			UsingSessionToken = False
			if 'SessionToken' in ocredentials:
				# Using a token-based role
				UsingSessionToken = True
				prelim_session = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
				                               aws_secret_access_key=ocredentials['SecretAccessKey'],
				                               aws_session_token=ocredentials['SessionToken'],
				                               region_name='us-east-1')
			else:
				# Not using a token-based role
				prelim_session = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
				                               aws_secret_access_key=ocredentials['SecretAccessKey'],
				                               region_name='us-east-1')
			account_access_successful = True
		elif ocredentials is not None and not ocredentials['Success']:
			logging.error(f"credentials were supplied to this library, but the credentials don't work... Exiting")
			raise CredentialRetrievalError('Credentials supplied were not valid')
		# If they didn't provide a profile, which generally means they want to use environment variables,
		# but it can also mean that they want to use their default profile
		elif fProfile is None or fProfile == 'EnvVar':
			access_key = os.environ.get('AWS_ACCESS_KEY_ID', None)
			secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
			session_token = os.environ.get('AWS_SESSION_TOKEN', None)
			region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
			env_var_profile = os.environ.get('AWS_PROFILE', None)
			logging.debug(f"access key: {access_key}\n"
			             f"secret_access_key: {secret_access_key}\n"
			             f"session_token: {session_token}\n"
			             f"region: {region}\n"
			             f"profile referenced in env vars: {env_var_profile}")
			if env_var_profile is None:
				UsingEnvVars = True
				logging.debug(f"Using environment variables with no profile specified")
				if fRegion is None and region is not None:
					prelim_session = boto3.Session(region_name=region)
					logging.debug(f"Using region: {region}")
				elif fRegion is not None:
					prelim_session = boto3.Session(region_name=fRegion)
					logging.debug(f"Using region: {fRegion}")
			# elif env_var_profile is not None:
			# 	logging.info(f"Using profile {env_var_profile} from environment variables")
			# 	UsingEnvVars = True
			# 	fProfile = env_var_profile
			else:
				UsingEnvVars = True
				logging.debug(f"Using profile specified from environment variables")
				if fRegion is None and region is None:
					prelim_session = boto3.Session(profile_name=env_var_profile)
					logging.debug(f"Using profile: {env_var_profile} and no region specified")
				elif fRegion is None and region is not None:
					prelim_session = boto3.Session(profile_name=env_var_profile, region_name=region)
					logging.debug(f"Using profile: {env_var_profile} and region: {region}")
				elif fRegion is not None:
					prelim_session = boto3.Session(profile_name=env_var_profile, region_name=fRegion)
					logging.debug(f"Using profile: {env_var_profile} and region: {fRegion}")
				fProfile = env_var_profile
				self.profile = fProfile
			account_access_successful = True
		else:
			# Not trying to use account_key_credentials
			try:
				logging.debug("Credentials are using a profile")
				# Checking to see if a region was included in the profile, if it was, then use it, otherwise - pick a default.
				prelim_session = boto3.Session(profile_name=fProfile)
				if prelim_session.region_name is None:
					prelim_session = boto3.Session(profile_name=fProfile, region_name=fRegion)
				elif fRegion is None:
					fRegion = prelim_session.region_name
				self.session = prelim_session
				try:
					result = self.session.client('ec2').describe_regions()
					account_access_successful = True
					account_and_region_access_successful = True
				except JSONDecodeError as my_Error:
					error_message = f"Failed to authenticate to AWS using {fProfile}\n" \
					                f"Probably a profile that doesn't work...\n"
					logging.error(f"Error: {error_message}")
					account_access_successful = False
					account_and_region_access_successful = False
				except Exception as my_Error:
					error_message = f"Failed to authenticate to AWS using {fProfile}\n" \
					                f"{my_Error}"
					logging.error(f"Error: {error_message}")
					account_access_successful = False
					account_and_region_access_successful = False
			except ProfileNotFound as my_Error:
				ErrorMessage = f"The profile '{fProfile}' wasn't found. Perhaps there was a typo? Error Message: {my_Error}"
				account_access_successful = False
				account_and_region_access_successful = False

		# Now that we've established how we're authenticating to the session...
		if account_access_successful:
			logging.info(f"account_access_successful!")
			if fRegion is not None:
				pass
			else:
				fRegion = prelim_session.region_name
			result = _validate_region(prelim_session, fRegion)
			if result['Success'] is True:
				account_and_region_access_successful = True
				if UsingEnvVars:
					logging.debug("Using environment variables...")
					self.session = boto3.Session(region_name=region)
					self.AccountStatus = 'ACTIVE'
				elif UsingSessionToken:
					logging.debug("Credentials are using SessionToken")
					self.session = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
					                             aws_secret_access_key=ocredentials['SecretAccessKey'],
					                             aws_session_token=ocredentials['SessionToken'],
					                             region_name=result['Region'])
					self.AccountStatus = 'ACTIVE'
				elif UsingKeys:
					logging.debug("Credentials are using Keys, but no SessionToken")
					self.session = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
					                             aws_secret_access_key=ocredentials['SecretAccessKey'],
					                             region_name=result['Region'])
					self.AccountStatus = 'ACTIVE'
				else:
					self.AccountStatus = 'ACTIVE'
					logging.info(f"They're using a profile, which was checked above...")
			else:
				logging.error(result['Message'])
				# account_access_successful = False
				account_and_region_access_successful = False
		elif account_and_region_access_successful:
			self.AccountStatus = 'ACTIVE'
			pass
		else:
			logging.info(f"account access was not successful")
			
		logging.info(f"Capturing Account Information for profile {fProfile}...")
		if account_and_region_access_successful:
			logging.info(f"Successfully validated access to account in region {fRegion}")
			self.Success = True
			self.acct_number = self.acct_num()
			self._AccountAttributes = self.find_account_attr()
			logging.info(f"Found {len(self._AccountAttributes)} attributes in this account")
			self.AccountType = self._AccountAttributes['AccountType']
			self.MgmtAccount = self._AccountAttributes['MasterAccountId']
			self.OrgID = self._AccountAttributes['OrgId']
			self.MgmtEmail = self._AccountAttributes['ManagementEmail']
			logging.info(f"Account {self.acct_number} is a {self.AccountType} account")
			self.Region = fRegion
			self.ErrorType = None
			self.creds = self.session._session._credentials.get_frozen_credentials()
			self.credentials = dict()
			self.Profile = fProfile if fProfile is not None else (self.session.profile_name if hasattr(self, 'session') else 'Default')
			self.credentials.update({'AccessKeyId'    : self.creds[0],
			                         'SecretAccessKey': self.creds[1],
			                         'SessionToken'   : self.creds[2],
			                         'AccountNumber'  : self.acct_number,
			                         'AccountId'      : self.acct_number,
			                         'MgmtAccount'    : self.MgmtAccount,
			                         'Region'         : fRegion,
			                         'Profile'        : self.Profile})
			if self.AccountType.lower() == 'root':
				logging.info("Enumerating all of the child accounts")
				self.ChildAccounts = self.find_child_accounts()
				logging.debug(f"As acct {self.acct_number} is the root account, we found {len(self.ChildAccounts)} accounts in the Org")

			else:
				logging.warning("Account isn't a root account, but we're looking for children anyway...")
				self.ChildAccounts = self.find_child_accounts()
		elif fProfile is not None and not account_access_successful:  # Likely the problem was the profile passed in
			logging.error(f"Profile {fProfile} failed to successfully access an account")
			self.AccountType = 'Unknown'
			self.MgmtAccount = 'Unknown'
			self.OrgID = 'Unknown'
			self.MgmtEmail = 'Unknown'
			self.Region = fRegion
			self.ChildAccounts = [{'AccountEmail' : 'ProfileFailed@doesnt.work',
			                       'AccountId'    : '012345678912',
			                       'AccountStatus': None,
			                       'MgmtAccount'  : '012345678912'}]
			self.Profile = fProfile if fProfile is not None else (self.session.profile_name if 'session' in self else 'None')
			self.creds = 'Unknown'
			self.credentials = 'Unknown'
			self.ErrorType = 'Invalid profile'
			self.Success = False
			logging.critical(f"Profile {fProfile} doesn't seem to work...")
		# raise NoCredentialsError
		elif fProfile is not None and account_access_successful:  # Likely the problem was the region passed in
			logging.error(f"Region '{fRegion}' wasn't valid. Please specify a valid region.")
			self.AccountType = 'Unknown'
			self.MgmtAccount = 'Unknown'
			self.OrgID = 'Unknown'
			self.MgmtEmail = 'Unknown'
			self.Region = fRegion
			self.creds = 'Unknown'
			self.credentials = 'Unknown'
			self.ErrorType = 'Invalid region'
			self.Success = False
		# raise UnknownRegionError(region_name=fRegion)
		elif ocredentials is not None:
			logging.critical(f"Credentials for account {ocredentials['AccountNum']} failed to successfully access an account")
			self.AccountType = 'Unknown'
			self.MgmtAccount = 'Unknown'
			self.OrgID = 'Unknown'
			self.MgmtEmail = 'Unknown'
			self.Region = fRegion
			self.creds = 'Unknown'
			self.credentials = 'Unknown'
			self.ErrorType = 'Invalid credentials'
			self.Success = False
		# raise CredentialRetrievalError
		else:
			logging.error(f"Not sure how we got here... Call your admin for help?")
			self.AccountType = 'Unknown'
			self.MgmtAccount = 'Unknown'
			self.OrgID = 'Unknown'
			self.MgmtEmail = 'Unknown'
			self.Region = fRegion
			self.creds = 'Unknown'
			self.credentials = 'Unknown'
			self.ErrorType = 'Unknown'
			self.Success = False

	def acct_num(self):
		"""
		This function returns a string of the account's 12-digit account number
		"""
		import logging
		from botocore.exceptions import ClientError, CredentialRetrievalError

		try:
			aws_session = self.session
			logging.info(f"Accessing session object to find its account number")
			client_sts = aws_session.client('sts')
			response = client_sts.get_caller_identity()
			logging.info(f"response: {response}")
			creds = response['Account']
		except JSONDecodeError as my_Error:
			error_message = (f"There was a JSON Decode Error while using sts to gain access to account\n"
			                 f"This is most often associated with a profile that doesn't work to gain access to the account it's made for.")
			logging.error(f"{error_message}\n"
			              f"Error Message: {my_Error}")
			pass
			creds = "Failure"
		except ClientError as my_Error:
			if str(my_Error).find("UnrecognizedClientException") > 0:
				logging.info(f"Security Issue")
				pass
			elif str(my_Error).find("InvalidClientTokenId") > 0:
				logging.info(f"Security Token is bad - probably a bad entry in config")
				pass
			else:
				print(my_Error)
				logging.info(f"Other kind of failure for boto3 access in acct")
				pass
			creds = "Failure"
		except CredentialRetrievalError as my_Error:
			if str(my_Error).find("custom-process") > 0:
				logging.info(f"Profile requires custom authentication")
				pass
			else:
				print(my_Error)
				pass
			creds = "Failure"
		return creds

	def find_account_attr(self):
		import logging
		from botocore.exceptions import ClientError, CredentialRetrievalError

		"""
		In the case of an Org Root or Child account, I use the response directly from the AWS SDK. 
		You can find the output format here: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html#Organizations.Client.describe_organization
		"""
		function_response = {'AccountType'    : 'Unknown',
		                     'AccountNumber'  : None,
		                     'OrgId'          : None,
		                     'Id'             : None,
		                     'MasterAccountId': None,
		                     'MgmtAccountId'  : None,
		                     'ManagementEmail': None}
		try:
			session_org = self.session
			client_org = session_org.client('organizations')
			response_pre = client_org.describe_organization()
			response = response_pre['Organization']
			function_response['OrgId'] = response['Id']
			function_response['Id'] = self.acct_number
			function_response['AccountNumber'] = self.acct_number
			function_response['MasterAccountId'] = response['MasterAccountId']
			function_response['MgmtAccountId'] = response['MasterAccountId']
			function_response['ManagementEmail'] = response['MasterAccountEmail']
			if response['MasterAccountId'] == self.acct_number:
				function_response['AccountType'] = 'Root'
			else:
				function_response['AccountType'] = 'Child'
			return function_response
		except ClientError as my_Error:
			if str(my_Error).find("UnrecognizedClientException") > 0:
				logging.error(f"Security Issue with account {self.acct_number}")
			elif str(my_Error).find("InvalidClientTokenId") > 0:
				logging.error(f"Security Token is bad - probably a bad entry in config for account {self.acct_number}")
			elif str(my_Error).find("AccessDenied") > 0:
				logging.error(f"Access Denied for account {self.acct_number}")
			elif str(my_Error).find("Organization") > 0:
				logging.info(f"Org not in use for acct: {self.acct_number}\n"
				             f"Error: {my_Error}")
				function_response['AccountType'] = 'StandAlone'
				function_response['Id'] = self.acct_number
				function_response['OrgId'] = None
				function_response['ManagementEmail'] = 'Email not available'
				function_response['AccountNumber'] = self.acct_number
				function_response['MasterAccountId'] = self.acct_number
				function_response['MgmtAccountId'] = self.acct_number
			pass
		except CredentialRetrievalError as my_Error:
			logging.error(f"Failure pulling or updating credentials for {self.acct_number}")
			print(my_Error)
			pass
		except Exception as my_Error:
			logging.error(f"Other kind of failure: {my_Error}")
			pass
		except:
			print("Excepted")
			pass
		return function_response

	def find_child_accounts(self):
		"""
		This is an example of the list response from this call:
			[
			{'MgmtAccount':'<12 digit-number>', 'AccountId': 'xxxxxxxxxxxx', 'AccountEmail': 'EmailAddr1@example.com', 'AccountStatus': 'ACTIVE'},
			{'MgmtAccount':'<12 digit-number>', 'AccountId': 'yyyyyyyyyyyy', 'AccountEmail': 'EmailAddr2@example.com', 'AccountStatus': 'ACTIVE'},
			{'MgmtAccount':'<12 digit-number>', 'AccountId': 'zzzzzzzzzzzz', 'AccountEmail': 'EmailAddr3@example.com', 'AccountStatus': 'SUSPENDED'}
			]
		This can be convenient for appending and removing.
		"""
		import logging
		from botocore.exceptions import ClientError

		child_accounts = []
		if self.AccountType.lower() == 'root':
			try:
				session_org = self.session
				client_org = session_org.client('organizations')
				response = client_org.list_accounts()
				theresmore = True
				logging.info(f"Enumerating Account info for account: {self.acct_number}")
				while theresmore:
					for account in response['Accounts']:
						child_accounts.append({'MgmtAccount'  : self.acct_number,
						                       'AccountId'    : account['Id'],
						                       'AccountEmail' : account['Email'],
						                       'AccountStatus': account['Status']})
					if 'NextToken' in response.keys():
						theresmore = True
						response = client_org.list_accounts(NextToken=response['NextToken'])
					else:
						theresmore = False
				sorted_child_accounts = sorted(child_accounts, key=lambda d: d['AccountId'])
				return sorted_child_accounts
			except ClientError as my_Error:
				logging.warning(f"Account {self.acct_number} doesn't represent an Org Root account")
				logging.debug(my_Error)
				return ()
		elif self.find_account_attr()['AccountType'].lower() in ['standalone', 'child']:
			child_accounts.append({'MgmtAccount'  : self.acct_number,
			                       'AccountId'    : self.acct_number,
			                       'AccountEmail' : 'Not an Org Management Account',
			                       # We know the account is ACTIVE because if it was SUSPENDED, we wouldn't have gotten a valid response from the org_root check
			                       'AccountStatus': 'ACTIVE'})
			return child_accounts
		elif self.AccountType.lower() == 'unknown':
			logging.warning(f"Account {self.acct_number} came up as an Unknown Account...")
			return ()
		else:
			logging.warning(f"Account {self.acct_number} suffered a crisis of identity")
			return ()

	def __str__(self):
		return f"Account #{self.acct_number} is a {self.AccountType} account with {len(self.ChildAccounts) - 1} child accounts"

	def __repr__(self):
		try:
			return f"Account #{self.acct_number} is a {self.AccountType} account with {len(self.ChildAccounts) - 1} child accounts"
		except AttributeError as my_Error:
			logging.error (f"Profile #{self.Profile} had a failure of some kind")
			logging.info(f"Error Message: {my_Error}")
			return ("This should be an error message")


class Aws_Acct_Credentials:
	"""
	Description: The definition of the "ocredentials" object
	"""

	def __init__(self, f_sts_client_obj, f_role_arn: str, f_role_session_name: str, f_region: str = 'us-east-1'):
		"""
		@Description: The object that will hold the credentials object, to make everything standardized
		@param f_sts_client_obj: The boto3 client object
		@param f_role_arn: The role arn you're looking to assume
		@param f_role_session_name: The text string of the session name you're expecting to use
		@param f_region: The region you're expecting to authenticate to. This is defaulted to be 'us-east-1'
		@return credentials: The object containing all the information from the sts_assume_role call
		"""
		try:
			credentials = f_sts_client_obj.assume_role(RoleArn=f_role_arn, RoleSessionName=f_role_session_name)['Credentials']
			self.aws_access_key = credentials['AccessKeyId']
			self.AccessKeyId = self.aws_access_key
			self.aws_secret_access_key = credentials['SecretAccessKey']
			self.SecretAccessKey = self.aws_secret_access_key
			self.aws_session_token = credentials['SessionToken']
			self.SessionToken = self.aws_session_token
			self.region = f_region
			self.Region = self.region
			self.AccountId = f_role_arn.split(':')[4]
			self.AccountNumber = self.AccountId
			self.AccountNum = self.AccountId
			self.MgmtAccount = 'Unknown'
			self.Profile = None
			self.Role = f_role_arn.split(':')[5].split('/')[1]
			self.Success = True
			self.ErrorMessage = ''
		except (ProfileNotFound,
		        ClientError,
		        ConnectionError,
		        EndpointConnectionError,
		        CredentialRetrievalError,
		        UnknownRegionError,
		        NoCredentialsError) as myError:
			self.Success = False
			self.ErrorMessage = str(myError)
			logging.error(f"Error: {myError}")

	def __str__(self):
		if self.Profile is None:
			return f"Account #{self.AccountId} was accessed directly with credentials"
		else:
			return f"Account #{self.AccountId} was accessed using {self.Profile}"

	def __repr__(self):
		if self.Profile is None:
			return f"Account #{self.AccountId} was accessed directly with credentials"
		else:
			return f"Account #{self.AccountId} was accessed using {self.Profile}"
