import logging

__version__ = "2024.02.27"

"""
** Why are some functions "function" vs. "function2" vs. "function3"?**

As most things in computer science, my naming scheme makes sense to me, but not necessarily everyone :). Hence, here is my attempt at an explanation.

- When a function is named "<function>" without a number after it, it's because that was the original function name I chose and used. 
Back in the beginning of my coding journey, I was using *profiles* for authentication/ authorization for everything, thinking that everyone else would use that too.
However, I was wrong. But the naming convention generally sticks, so functions without a numbered prefix, tend to expect the profile to be supplied.
- After a while, I realized that I could pass a dictionary of credentials, instead of the profile itself, which could include things like the region, and therefore, 
make the script a little more flexible. So functions that end in "*2", typically take a dict (often called "ocredentials") as a parameter. I've tried to document 
what fields are expected in that parameter within the docstring of the function.
- After another long while, I realized I should be creating a class object for the account/ credentials, so I created the "account_class.py" class file, and I've 
used that for all functions that end in "*3". However, I have also realized that using the account_class object can sometimes lead to some latency, as some of the 
lookups within that class take a while. Soooo... I've recently reverted to using the "*2" functions more than the "*3" functions - since the credentials can be 
easily passed back and forth, and it's quicker. There might be some security exposure to doing this that I'm unaware of, so I'm keeping the "*3" functions around
just in case...     
"""


def get_regions3(faws_acct, fregion_list=None):
	"""
	This is a library function to get the AWS region names that correspond to the
	fragments that may have been provided via the command line.

	For instance
		- if the user provides 'us-east', this function will return ['us-east-1','us-east-2'].
		- if the user provides 'west', this function will return ['us-west-1', 'us-west-2', 'eu-west-1', etc.]
		- if the user provides 'all', this function will return all regions

	The first parameter to this library must provide a valid account object that includes a boto3 session,
	so that regions can be looked up.

	Please note that there is no paging functionality for the "describe_regions" method within EC2, hence no paging below.
	"""
	import logging

	# This handles the case where the user passes a single string, instead of a list or nothing.
	if isinstance(fregion_list, str):
		fregion_list = [fregion_list]
	region_info = faws_acct.session.client('ec2')
	if fregion_list is None or "all" in fregion_list or "ALL" in fregion_list or "All" in fregion_list:
		regions = region_info.describe_regions(Filters=[{'Name': 'opt-in-status', 'Values': ['opt-in-not-required', 'opted-in']}])
		RegionNames = [region_name['RegionName'] for region_name in regions['Regions']]
		return RegionNames
	# Special case where they want everything - globally
	elif 'global' in fregion_list:
		regions = region_info.describe_regions(AllRegions=True)
		RegionNames = [region_name['RegionName'] for region_name in regions['Regions']]
		return RegionNames
	else:
		regions = region_info.describe_regions(Filters=[{'Name': 'opt-in-status', 'Values': ['opt-in-not-required', 'opted-in']}])
		RegionNames = [region_name['RegionName'] for region_name in regions['Regions']]
		RegionNames2 = []
		for x in fregion_list:
			for y in RegionNames:
				logging.info(f"Have {y} | Looking for {x}")
				if y.find(x) >= 0:
					logging.info(f"Found {y}")
					RegionNames2.append(y)
		return RegionNames2


def get_ec2_regions3(faws_acct, fkey=None):
	"""
	This is a library function to get the AWS region names that correspond to the
	fragments that may have been provided via the command line.

	The first parameter to this library must provide a valid session object, which is used to instantiate a boto3 session,
	so that regions can be looked up.

	Please note that there is no paging functionality for the "describe_regions" method within EC2, hence no paging below.
	"""
	import logging
	from botocore.exceptions import EndpointConnectionError

	RegionNames = []
	if isinstance(fkey, str):
		fkey = [fkey]
	try:
		region_info = faws_acct.session.client('ec2')
	except AttributeError as my_Error:
		logging.error(my_Error)
		return RegionNames
	except EndpointConnectionError as my_Error:
		error_message = (f"Connection to AWS seems to not be working.\n"
		                 f"Actual error: {my_Error}")
		logging.error(error_message)
		return RegionNames
	except Exception as my_Error:
		error_message = (f"Something stopped working.\n"
		                 f"Actual error: {my_Error}")
		logging.error(error_message)
		return RegionNames
	regions = region_info.describe_regions(Filters=[
		{'Name': 'opt-in-status', 'Values': ['opt-in-not-required', 'opted-in']}])
	for region in regions['Regions']:
		RegionNames.append(region['RegionName'])
	if fkey is None or "all" in fkey or "ALL" in fkey or 'All' in fkey:
		return RegionNames
	RegionNames2 = []
	for x in fkey:
		for y in RegionNames:
			logging.info(f"Have {y} | Looking for {x}")
			if y.find(x) >= 0:
				logging.info(f"Found {y}")
				RegionNames2.append(y)
	return RegionNames2


def get_service_regions(service, fkey=None, fprofile=None, ocredentials=None, faws_acct=None):
	"""
	Parameters:
		service = the AWS service we're trying to get regions for. This is useful since not all services are supported in all regions.
		fkey = A *list* of string fragments of what region we're looking for.
			If not supplied, then we send back all regions for that service.
			If they send "us-" (for example), we would send back only those regions which matched that fragment.
			This is good for focusing a search on only those regions you're searching within.
		Either the profile, ocredentials, or aws_acct account object could be passed. We'll use whatever they pass, or nothing.
	"""
	import boto3
	import logging

	if fprofile is not None:
		s = boto3.Session(profile_name=fprofile)
	elif ocredentials is not None:
		s = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
		                  aws_secret_access_key=ocredentials['SecretAccessKey'],
		                  aws_session_token=ocredentials['SessionToken'],
		                  region_name=ocredentials['Region'])
	elif faws_acct is not None:
		s = faws_acct.session
	else:
		s = boto3.Session()
	regions = s.get_available_regions(service, partition_name='aws', allow_non_regional=False)
	if fkey is None or ('all' in fkey or 'All' in fkey or 'ALL' in fkey):
		return regions
	RegionNames = []
	for x in fkey:
		for y in regions:
			logging.info(f"Have {y} | Looking for {x}")
			if y.find(x) >= 0:
				logging.info(f"Found {y}")
				RegionNames.append(y)
	return RegionNames


def validate_region3(faws_acct, fRegion=None):
	import logging

	session_region = faws_acct.session
	client_region = session_region.client('ec2')
	if fRegion is None:
		logging.info(f"No region supplied. Defaulting to 'us-east-1'")
		fRegion = 'us-east-1'
	region_info = client_region.describe_regions(Filters=[{'Name': 'region-name', 'Values': [fRegion]}])['Regions']
	if len(region_info) == 0:
		message = f"'{fRegion}' is not a valid region name for this account"
		logging.error(message)
		result = {'Success': False, 'Message': message}
		return result
	else:
		message = f"'{fRegion}' is a valid region name for this account"
		logging.info(message)
		result = {'Success': True, 'Message': message}
		return result


def get_profiles(fSkipProfiles=None, fprofiles=None):
	"""
	We assume that the user of this function wants all profiles.
	If they provide a list of profile strings (in fprofiles),
	then we compare those strings to the full list of profiles we have,
	and return those profiles that contain the strings they sent.
	"""
	import boto3
	import logging

	profiles_to_remove = []
	my_Session = boto3.Session()
	my_profiles = my_Session._session.available_profiles
	if fSkipProfiles is None:
		fSkipProfiles = []
	if fprofiles is None:
		fprofiles = ['all']
	elif isinstance(fprofiles, str) and fprofiles in my_profiles:
		# Update the string to become a list
		return [fprofiles]
	elif isinstance(fprofiles, str):
		error_message = f"Error: The profile passed in '{fprofiles}' doesn't exist."
		logging.error(error_message)
		return error_message
	if len(fSkipProfiles) == 0:
		pass
	else:
		for profile in my_profiles:
			logging.info(f"Found profile {profile}")
			if ("skipplus" in fSkipProfiles and profile.find("+") >= 0) or profile in fSkipProfiles:
				logging.info(f"Removing profile: {profile} since it's in the fSkipProfiles parameter {fSkipProfiles}")
				profiles_to_remove.append(profile)
		my_profiles = list(set(my_profiles) - set(profiles_to_remove))
	if "all" in fprofiles or "ALL" in fprofiles or "All" in fprofiles:
		return my_profiles

	ProfileList = []
	for x in fprofiles:
		for y in my_profiles:
			logging.info(f"Have {y}| Looking for {x}")
			if y.find(x) >= 0:
				logging.info(f"Found profile {y}")
				ProfileList.append(y)
	return ProfileList


def find_in(list_to_search, list_to_find=None, fexact=False):
	import logging

	if list_to_find is None or None in list_to_find:
		return list_to_search
	elif 'all' in list_to_find or 'All' in list_to_find or 'ALL' in list_to_find:
		return list_to_search
	list_to_return = []
	for x in list_to_search:
		for y in list_to_find:
			logging.info(f"Have {x} | Looking for {y}")
			if fexact:
				if x == y:
					list_to_return.append(y)
				else:
					continue
			elif x.find(y) >= 0:
				logging.info(f"Found {y}")
				list_to_return.append(y)
	return list_to_return


def addLoggingLevel(levelName, levelNum, methodName=None):
	import logging
	"""
	Comprehensively adds a new logging level to the `logging` module and the
	currently configured logging class.

	`levelName` becomes an attribute of the `logging` module with the value
	`levelNum`. `methodName` becomes a convenience method for both `logging`
	itself and the class returned by `logging.getLoggerClass()` (usually just
	`logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
	used.

	To avoid accidental clobberings of existing attributes, this method will
	raise an `AttributeError` if the level name is already an attribute of the
	`logging` module or if the method name is already present 

	Example
	-------
	>>> addLoggingLevel('TRACE', logging.DEBUG - 5)
	>>> logging.getLogger(__name__).setLevel("TRACE")
	>>> logging.getLogger(__name__).trace('that worked')
	>>> logging.trace('so did this')
	>>> logging.TRACE
	5

	"""
	if not methodName:
		methodName = levelName.lower()

	if hasattr(logging, levelName):
		raise AttributeError(f'{levelName} already defined in logging module')
	if hasattr(logging, methodName):
		raise AttributeError(f'{methodName} already defined in logging module')
	if hasattr(logging.getLoggerClass(), methodName):
		raise AttributeError(f'{methodName} already defined in logger class')

	# This method was inspired by the answers to Stack Overflow post
	# http://stackoverflow.com/q/2183233/2988730, especially
	# http://stackoverflow.com/a/13638084/2988730
	def logForLevel(self, message, *args, **kwargs):
		if self.isEnabledFor(levelNum):
			self._log(levelNum, message, args, **kwargs)

	def logToRoot(message, *args, **kwargs):
		logging.log(levelNum, message, *args, **kwargs)

	logging.addLevelName(levelNum, levelName)
	setattr(logging, levelName, levelNum)
	setattr(logging.getLoggerClass(), methodName, logForLevel)
	setattr(logging, methodName, logToRoot)


def find_if_alz(fProfile: str) -> dict:
	import boto3

	session_org = boto3.Session(profile_name=fProfile)
	client_org = session_org.client('s3')
	bucket_list = client_org.list_buckets()
	response = dict()
	response['BucketName'] = None
	response['ALZ'] = False
	for bucket in bucket_list['Buckets']:
		if "aws-landing-zone-configuration" in bucket['Name']:
			response['BucketName'] = bucket['Name']
			response['ALZ'] = True
			response['Region'] = find_bucket_location(fProfile, bucket['Name'])
	return response


def find_bucket_location(fProfile, fBucketname):
	import boto3
	import logging
	from botocore.exceptions import ClientError

	session_org = boto3.Session(profile_name=fProfile)
	client_org = session_org.client('s3')
	try:
		response = client_org.get_bucket_location(Bucket=fBucketname)
	except ClientError as my_Error:
		if str(my_Error).find("AccessDenied") > 0:
			logging.error(f"Authorization Failure for profile {fProfile}")
		return None
	if response['LocationConstraint'] is None:
		location = 'us-east-1'
	else:
		location = response['LocationConstraint']
	return location


def find_acct_email(fOrgRootProfile, fAccountId):
	import boto3
	"""
	This function *unfortunately* only works with organization accounts.
	"""

	session_org = boto3.Session(profile_name=fOrgRootProfile)
	client_org = session_org.client('organizations')
	email_addr = client_org.describe_account(AccountId=fAccountId)['Account']['Email']
	# email_addr = response['Account']['Email']
	return email_addr


def find_account_number(fProfile=None):
	import boto3
	import logging
	from botocore.exceptions import ClientError, CredentialRetrievalError, InvalidConfigError

	response = '123456789012'  # This is the Failure response
	try:
		# logging.info("Looking for profile %s", fProfile)
		if fProfile is None:
			sts_session = boto3.Session()
		else:
			sts_session = boto3.Session(profile_name=fProfile)
		client_sts = sts_session.client('sts')
		response = client_sts.get_caller_identity()['Account']
	except ClientError as my_Error:
		if str(my_Error).find("UnrecognizedClientException") > 0:
			logging.error("%s: Security Issue", fProfile)
			pass
		elif str(my_Error).find("InvalidClientTokenId") > 0:
			logging.error("%s: Security Token is bad - probably a bad entry in config", fProfile)
			pass
	except CredentialRetrievalError as my_Error:
		if str(my_Error).find("CredentialRetrievalError") > 0:
			logging.error("%s: Some custom process isn't working", fProfile)
			pass
	except InvalidConfigError as my_Error:
		if str(my_Error).find("InvalidConfigError") > 0:
			logging.error(
				f"{fProfile}: profile is invalid. Probably due to a config profile based on a credential that doesn't work")
			pass
	except Exception as my_Error:
		logging.error(f"Other kind of failure for profile {fProfile}: {my_Error}")
		pass
	return response


def find_calling_identity(fProfile):
	import boto3
	import logging
	from botocore.exceptions import ClientError

	try:
		session_sts = boto3.Session(profile_name=fProfile)
		logging.info(f"Getting creds used within profile {fProfile}")
		client_sts = session_sts.client('sts')
		response = client_sts.get_caller_identity()
		creds = {'Arn'  : response['Arn'], 'AccountId': response['Account'],
		         'Short': response['Arn'][response['Arn'].rfind(':') + 1:]}
	except ClientError as my_Error:
		if str(my_Error).find("UnrecognizedClientException") > 0:
			print(f"{fProfile}: Security Issue")
		elif str(my_Error).find("InvalidClientTokenId") > 0:
			print(f"{fProfile}: Security Token is bad - probably a bad entry in config")
		else:
			print(f"Other kind of failure for profile {fProfile}")
			print(my_Error)
		creds = "Failure"
	return creds


def RemoveCoreAccounts(MainList, AccountsToRemove=None):
	import logging
	"""
	MainList is expected to come through looking like this:
		[{'AccountEmail': 'User+LZ@example.com', 'AccountId': '0123xxxx8912'},
		{'AccountEmail': 'User+LZ_Log@example.com', 'AccountId': '1234xxxx9012'},
			< ... >
		{'AccountEmail': 'User+LZ_SS@example.com', 'AccountId': '9876xxxx1000'},
		{'AccountEmail': 'User+Demo@example.com', 'AccountId': '9638xxxx012'}]
	AccountsToRemove is simply a list of accounts you don't want to screw with. It might look like this:
		['9876xxxx1000', '9638xxxx1012']
	"""

	if AccountsToRemove is None:
		AccountsToRemove = []
	NewCA = []
	for i in range(len(MainList)):
		if MainList[i]['AccountId'] in AccountsToRemove:
			logging.info(f"Found {str(MainList[i]['AccountId'])} in AccountsToRemove, removing from list")
			continue
		else:
			logging.info(f"Account {str(MainList[i]['AccountId'])} was allowed")
			NewCA.append(MainList[i])
	return NewCA


def print_timings(fTiming: bool = False, fverbose: int = 50, fbegin_time=None, fmessage: str = None):
	"""
	Description: Prints how long it's taken in the script to get to this point...
	@param fTiming: Boolean whether we print anything
	@param fverbose: Verbosity to determine whether we print when user didn't specify any verbosity. This allows us to only print when they want more info.
	@param fbegin_time: The beginning time to compare to
	@param fmessage: The message to print out, when we print the timings.
	@return: None
	"""
	from colorama import Fore, init
	from time import time
	init()

	if fTiming and fverbose < 50 and fbegin_time is not None:
		print(f"{Fore.GREEN}{fmessage}\n"
		      f"This script has taken {time() - fbegin_time:.6f} seconds so far{Fore.RESET}")


def make_creds(faws_acct):
	return ({'AccessKeyId'    : faws_acct.creds.access_key,
	         'SecretAccessKey': faws_acct.creds.secret_key,
	         'SessionToken'   : faws_acct.creds.token,
	         'Profile'        : faws_acct.credentials['Profile'],
	         'Region'         : faws_acct.Region,
	         'AccountId'      : faws_acct.acct_number,
	         'AccountNumber'  : faws_acct.acct_number,
	         'MgmtAccount'    : faws_acct.MgmtAccount})


def get_child_access(fRootProfile, fChildAccount, fRegion='us-east-1', fRoleList=None):
	"""
	@param: fRootProfile is a string
	@param:  fChildAccount expects an AWS account number (ostensibly of a Child Account)
	@param:  rRegion expects a string representing one of the AWS regions ('us-east-1', 'eu-west-1', etc.)
	@param:  fRoleList expects a list of roles to try, but defaults to a list of typical roles, in case you don't provide

	The first response object is a dict with account_credentials to pass onto other functions
	The min response object is the rolename that worked to gain access to the target account

	The format of the account credentials dict is here:
	account_credentials = {'Profile' : fRootProfile,
							'AccessKeyId' : '',
							'SecretAccessKey' : None,
							'SessionToken' : None,
							'AccountNumber' : None}
	"""
	import boto3
	import logging
	from botocore.exceptions import ClientError

	if not isinstance(fChildAccount, str):  # Make sure the passed in account number is a string
		fChildAccount = str(fChildAccount)
	ParentAccountId = find_account_number(fRootProfile)
	sts_session = boto3.Session(profile_name=fRootProfile)
	sts_client = sts_session.client('sts', region_name=fRegion)
	if fChildAccount == ParentAccountId:
		explain_string = ("We're trying to get access to either the Root Account (which we already have access "
		                  "to via the profile)	or we're trying to gain access to a Standalone account. "
		                  "In either of these cases, we should just use the profile passed in, "
		                  "instead of trying to do anything fancy.")
		logging.info(explain_string)
		# TODO: Wrap this in a try/except loop
		account_credentials = sts_client.get_session_token()['Credentials']
		account_credentials['AccountNumber'] = fChildAccount
		account_credentials['Profile'] = fRootProfile
		return account_credentials, 'Check Profile'
	if fRoleList is None:
		fRoleList = ['AWSCloudFormationStackSetExecutionRole', 'AWSControlTowerExecution',
		             'OrganizationAccountAccessRole', 'AdministratorAccess', 'Owner']
	# Initializing the "Negative Use Case" string, returning the whole list instead of only the last role it tried.
	# This way the operator knows that NONE of the roles supplied worked.
	return_string = f"{str(fRoleList)} failed. Try Again"

	account_credentials = {'Profile'        : fRootProfile,
	                       'AccessKeyId'    : None,
	                       'SecretAccessKey': None,
	                       'SessionToken'   : None,
	                       'AccountNumber'  : None}
	for role in fRoleList:
		try:
			logging.info("Trying to access account %s using %s profile assuming role: %s", fChildAccount, fRootProfile,
			             role)
			role_arn = f"arn:aws:iam::{fChildAccount}:role/{role}"
			account_credentials = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="Find-ChildAccount-Things")[
				'Credentials']
			# If we were successful up to this point, then we'll short-cut everything and just return the credentials that worked
			account_credentials['Profile'] = fRootProfile
			account_credentials['AccountNumber'] = fChildAccount
			return account_credentials, role
		except ClientError as my_Error:
			if my_Error.response['Error']['Code'] == 'ClientError':
				logging.info(my_Error)
			continue
	# Returns a dict object since that's what's expected
	# It will only get to the part below if the child isn't accessed properly using the roles already defined
	return account_credentials, return_string


def get_child_access3(faws_acct, fChildAccount: str, fRegion: str = None, fRoleList: list = None):
	"""
	- faws_acct is a custom class (account_class.aws_acct_access)
	- fChildAccount expects an AWS account number (ostensibly of a Child Account)
	- rRegion expects a string representing one of the AWS regions ('us-east-1', 'eu-west-1', etc.)
	- fRoleList expects a list of roles to try, but defaults to a list of typical roles, in case you don't provide

	The format of the returned account credentials dict is here:
		account_credentials = {'ParentAcctId'   : ParentAccountId,
		                       'MgmtAccount'    : faws_acct.MgmtAccount,
		                       'OrgType'        : org_type,
		                       'AccessKeyId'    : faws_acct.creds.access_key,
		                       'SecretAccessKey': faws_acct.creds.secret_key,
		                       'SessionToken'   : faws_acct.creds.token,
		                       'AccountNumber'  : fChildAccount,
		                       'AccountId'      : fChildAccount,
		                       'Region'         : fRegion,
		                       'AccountStatus'  : faws_acct.AccountStatus,
		                       'RolesTried'     : fRoleList,
		                       'Role'           : 'Use Profile',
		                       'Profile'        : If possible, the profile used to access the account,
		                       'AccessError'    : False,
		                       'Success'        : True,
		                       'ErrorMessage'   : None}
	"""
	import logging
	from botocore.exceptions import ClientError

	if not isinstance(fChildAccount, str):  # Make sure the passed in account number is a string
		fChildAccount = str(fChildAccount)
	org_type = faws_acct.AccountType
	ParentAccountId = faws_acct.acct_number
	if fRegion is None:
		fRegion = 'us-east-1'
	if fRoleList is None or fRoleList == []:
		fRoleList = ['AWSCloudFormationStackSetExecutionRole', 'AWSControlTowerExecution',
		             'OrganizationAccountAccessRole', 'AdministratorAccess', 'Owner']
	elif isinstance(fRoleList, str):
		fRoleList = [fRoleList]
	sts_client = faws_acct.session.client('sts', region_name=fRegion)
	if fChildAccount == ParentAccountId:
		explain_string = (f"We're trying to get access to either the Root Account (which we already have access "
		                  f"to via the profile) or we're trying to gain access to a Standalone account. "
		                  f"In either of these cases, we should just use the profile passed in, "
		                  f"instead of trying to do anything fancy.")
		logging.info(explain_string)
		# TODO: Wrap this in a try/except loop on the off-chance that the class doesn't work properly
		account_credentials = {'ParentAcctId'   : ParentAccountId,
		                       'MgmtAccount'    : faws_acct.MgmtAccount,
		                       'OrgType'        : org_type,
		                       'AccessKeyId'    : faws_acct.creds.access_key,
		                       'SecretAccessKey': faws_acct.creds.secret_key,
		                       'SessionToken'   : faws_acct.creds.token,
		                       'AccountNumber'  : fChildAccount,
		                       'AccountId'      : fChildAccount,
		                       'Region'         : fRegion,
		                       'AccountStatus'  : faws_acct.AccountStatus,
		                       'RolesTried'     : fRoleList,
		                       'Role'           : 'Use Profile',
		                       'Profile'        : faws_acct.session.profile_name if faws_acct.session.profile_name else None,
		                       'AccessError'    : False,
		                       'Success'        : True,
		                       'ErrorMessage'   : None}
		return account_credentials
	# Initializing the "Negative Use Case" string, returning the whole list instead of only the last role it tried.
	# This way the operator knows that NONE of the roles supplied worked.
	error_message = f"{str(fRoleList)} failed. Try Again"
	account_credentials = {'ParentAcctId'   : ParentAccountId,
	                       'MgmtAccount'    : ParentAccountId,
	                       'OrgType'        : 'Child',
	                       'AccessKeyId'    : None,
	                       'SecretAccessKey': None,
	                       'SessionToken'   : None,
	                       'AccountNumber'  : None,
	                       'AccountId'      : None,
	                       'Region'         : fRegion,
	                       'AccountStatus'  : faws_acct.AccountStatus,
	                       'RolesTried'     : fRoleList,
	                       'Role'           : None,
	                       'Profile'        : None,
	                       'AccessError'    : False,
	                       'Success'        : False,
	                       'ErrorMessage'   : error_message}
	for role in fRoleList:
		try:
			if faws_acct.session.profile_name:
				logging.info(
					f"Trying to access account {fChildAccount} using parent profile: {faws_acct.session.profile_name} assuming role: {role}")
			else:
				logging.info(
					f"Trying to access account {fChildAccount} using account number {faws_acct.acct_number} assuming role: {role}")
			role_arn = f"arn:aws:iam::{fChildAccount}:role/{role}"
			account_credentials = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="Test-ChildAccount-Access")['Credentials']
			# If we were successful up to this point, then we'll short-cut everything and just return the credentials that worked
			logging.info(f"The credentials for account {fChildAccount} using parent account "
			             f"{faws_acct.acct_number} and role name {role} worked")
			account_credentials['ParentAcctId'] = ParentAccountId
			account_credentials['MgmtAccount'] = ParentAccountId
			account_credentials['OrgType'] = 'Child'
			account_credentials['AccountNumber'] = fChildAccount
			account_credentials['AccountId'] = fChildAccount
			account_credentials['Region'] = fRegion
			account_credentials['AccountStatus'] = faws_acct.AccountStatus
			account_credentials['RolesTried'] = fRoleList
			account_credentials['Role'] = role
			account_credentials['Profile'] = None
			account_credentials['AccessError'] = False
			account_credentials['ErrorMessage'] = None
			account_credentials['Success'] = True
			return account_credentials
		except ClientError as my_Error:
			error_message = f"In Region {fRegion}, we got error message: {my_Error}"
			logging.info(error_message)
			account_credentials = {'AccessError': True, 'Success': False, 'ErrorMessage': error_message, 'RolesTried': fRoleList}
			continue
		except Exception as my_Error:
			logging.info(my_Error)
			continue
	# Returns a dict object since that's what's expected
	# It will only get to the part below if the child isn't accessed properly using the roles already defined
	logging.debug(f"Failure:\n"
	              f"Role list: {fRoleList}\n"
	              f"account credentials: {account_credentials}")
	account_credentials = {'AccessError': True, 'Success': False, 'ErrorMessage': "Access Failed", 'RolesTried': fRoleList}
	return account_credentials


def enable_drift_on_stacks2(ocredentials: dict, fRegion: str, fStackName: str):
	import boto3
	import logging

	session_cfn = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
		'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	client_cfn = session_cfn.client('cloudformation')
	logging.info(f"Enabling drift detection on Stack {fStackName} in "
	             f"Account {ocredentials['AccountNumber']} in region {fRegion}")
	response = client_cfn.detect_stack_drift(StackName=fStackName)
	return response  # Since this is an async process, there is no response to send back


def enable_drift_on_stackset2(ocredentials: dict, fStackSetName: str):
	"""
	@param: ocredentials - dict object containing account information
	@param: fStackSetName - string containing the stackset name we're going to look up
	"""
	import boto3
	import logging
	session_cfn = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_cfn = session_cfn.client('cloudformation')
	logging.info(f"Enabling drift detection on Stack {fStackSetName} in "
	             f"Account {ocredentials['AccountNumber']} in region {ocredentials['Region']}")
	response = client_cfn.detect_stack_set_drift(StackSetName=fStackSetName,
	                                             OperationPreferences={'RegionConcurrencyType'     : 'PARALLEL',
	                                                                   'FailureTolerancePercentage': 10,
	                                                                   'MaxConcurrentPercentage'   : 100},
	                                             CallAs='SELF')
	return response  # Since this is an async process, there is no response to send back


def enable_drift_on_stackset3(faws_acct, fStackSetName: str):
	"""
	@param: ocredentials - dict object containing account information
	@param: fStackSetName - string containing the stackset name we're going to look up
	"""
	import logging
	from botocore.exceptions import ClientError

	client_cfn = faws_acct.session.client('cloudformation')
	logging.info(f"Enabling drift detection on Stack {fStackSetName} in "
	             f"Account {faws_acct.acct_number} in region {faws_acct.Region}")
	response = {'Success': False, 'ErrorMessage': ''}
	try:
		response = client_cfn.detect_stack_set_drift(StackSetName=fStackSetName,
		                                             OperationPreferences={'RegionConcurrencyType'     : 'PARALLEL',
		                                                                   'FailureTolerancePercentage': 10,
		                                                                   'MaxConcurrentPercentage'   : 100},
		                                             CallAs='SELF')
		response.update({'Success': True, 'ErrorMessage': ''})
	except ClientError as my_Error:
		# Only worry about a specific service error code
		if my_Error.response['Error']['Code'] == 'OperationInProgressException':
			error_message = f"Error: {my_Error}"
			logging.error(error_message)
			# raise
			response.update({'ErrorMessage': error_message})
	except Exception as my_Error:
		error_message = f"Error: {my_Error}"
		logging.error(error_message)
		response.update({'ErrorMessage': error_message})
	return response  # Since this is an async process, there is no response to send back when things go well


"""
Above - Generic functions
Below - Specific functions to specific features
"""


def find_sns_topics2(ocredentials, fTopicFrag: str = None, fExact: bool = False):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the region
		- ['AccountNumber'] holds the account number

	Returns:
		List of Topic ARNs found that match the fragment sent
"""
	import boto3
	import logging
	if fTopicFrag is None:
		fTopicFrag = ['all']
	session_sns = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_sns = session_sns.client('sns')
	response = {'NextToken': ''}
	TopicList = []
	while 'NextToken' in response:
		response = client_sns.list_topics(NextToken=response['NextToken'])
		for item in response['Topics']:
			topic_name = item['TopicArn'][item['TopicArn'].rfind(':') + 1:]
			TopicList.append(topic_name)
	if 'all' in fTopicFrag:
		logging.info(f"Looking for all SNS Topics in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}\n"
		             f"Topics Returned: {TopicList}\n"
		             f"We found {len(TopicList)} SNS Topics")
		return TopicList
	else:
		logging.info(f"Looking for specific SNS Topics in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}")
		topic_list2 = []
		for item in fTopicFrag:
			for topic in TopicList:
				logging.info(f"Have {topic} | Looking for {item}")
				if fExact:
					logging.info("Looking for EXACT matches")
					if topic == item:
						logging.error(f"Found {topic}")
						topic_list2.append(topic)
				elif topic.find(item) >= 0:
					logging.error(f"Found {topic}")
					topic_list2.append(topic)
		logging.info(f"We found {len(topic_list2)} SNS Topics", )
		return topic_list2


def find_role_names2(ocredentials, fRegion, fRoleNameFrag=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number

	Returns:
		List of Role Names found that match the fragment list sent
	"""
	import boto3
	import logging
	if fRoleNameFrag is None:
		fRoleNameFrag = ['all']
	session_iam = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=fRegion)
	client_iam = session_iam.client('iam')
	# TODO: Enable pagination
	response = client_iam.list_roles()['Roles']
	RoleNameList = []
	for item in response:
		RoleNameList.append(item['RoleName'])
	if 'all' in fRoleNameFrag:
		logging.info(f"Looking for all RoleNames in account {ocredentials['AccountNumber']} from Region {fRegion}\n"
		             f"RoleName Arns Returned: {RoleNameList}\n"
		             f"We found {len(RoleNameList)} RoleNames")
		return RoleNameList
	else:
		logging.info(
			f"Looking for specific RoleNames in account {ocredentials['AccountNumber']} from Region {fRegion}")
		RoleNameList2 = []
		for item in fRoleNameFrag:
			for RoleName in RoleNameList:
				logging.info(f'Have {RoleName} | Looking for {item}')
				if RoleName.find(item) >= 0:
					logging.info(f'Found {RoleName}')
					RoleNameList2.append(RoleName)
		logging.info(f"We found {len(RoleNameList2)} Roles")
		return RoleNameList2


def find_cw_log_group_names2(ocredentials, fRegion, fCWLogGroupFrag=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number

	Returns:
		List of CloudWatch Log Group Names found that match the fragment list
"""
	import boto3
	import logging
	if fCWLogGroupFrag is None:
		fCWLogGroupFrag = ['all']
	session_cw = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                           aws_secret_access_key=ocredentials['SecretAccessKey'],
	                           aws_session_token=ocredentials['SessionToken'],
	                           region_name=fRegion)
	client_cw = session_cw.client('logs')
	CWLogGroupList = []
	FirstTime = True
	response = {'nextToken': None}
	while 'nextToken' in response.keys() or FirstTime:
		if FirstTime:
			response = client_cw.describe_log_groups()
			FirstTime = False
		else:
			response = client_cw.describe_log_groups(nextToken=response['nextToken'])
		for item in response['logGroups']:
			CWLogGroupList.append(item['logGroupName'])
	if 'all' in fCWLogGroupFrag:
		logging.info(f"Looking for all Log Group names in account {ocredentials['AccountNumber']} from Region {fRegion}\n"
		             f"Log Group Names Returned: {CWLogGroupList}\n"
		             f"We found {len(CWLogGroupList)} Log Group names")
		return CWLogGroupList
	else:
		logging.info(f"Looking for specific Log Group names in account {ocredentials['AccountNumber']} from Region {fRegion}")
		CWLogGroupList2 = []
		for item in fCWLogGroupFrag:
			for logGroupName in CWLogGroupList:
				logging.info(f"Have {logGroupName} | Looking for {item}")
				if logGroupName.find(item) >= 0:
					logging.info(f"Found {logGroupName}")
					CWLogGroupList2.append(logGroupName)
		logging.info(f"We found {len(CWLogGroupList2)} Log Groups")
		return CWLogGroupList2


def find_org_services2(ocredentials, serviceNameList=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Region'] holds the Region
	serviceName allows the user to provide the specific service we're looking for

	Returns:
		List of services that match the items found in the list provided
"""
	import boto3
	import logging
	if serviceNameList is None:
		serviceNameList = ['all']
	session_org = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_org = session_org.client('organizations')
	EnabledOrgServicesList = []
	FirstTime = True
	response = {'NextToken': None}
	while 'NextToken' in response.keys() or FirstTime:
		if FirstTime:
			response = client_org.list_aws_service_access_for_organization()
			FirstTime = False
		else:
			response = client_org.list_aws_service_access_for_organization(NextToken=response['NextToken'])
		EnabledOrgServicesList.extend(response['EnabledServicePrincipals'])
	if 'all' in serviceNameList or 'All' in serviceNameList or 'ALL' in serviceNameList:
		logging.info(f"Looking for all Org-Enabled services in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}\n"
		             f"Enabled Services Returned: {EnabledOrgServicesList}\n"
		             f"We found {len(EnabledOrgServicesList)} enabled Org Services")
		return EnabledOrgServicesList
	else:
		logging.info(f"Looking for specific enabled Org services in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}")
		EnabledOrgServicesList2 = []
		for item in serviceNameList:
			for serviceName in EnabledOrgServicesList:
				logging.info(f"Have {serviceName} | Looking for {item}")
				if serviceName['ServicePrincipal'].find(item) >= 0:
					logging.info(f"Found {serviceName}")
					EnabledOrgServicesList2.append(serviceName)
		logging.info(f"We found {len(EnabledOrgServicesList2)} enabled Org services")
		return EnabledOrgServicesList2


def disable_org_service2(ocredentials, serviceName=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Region'] holds the Region
	serviceName allows the user to provide the specific service we're looking for

	Returns:
		List of CloudWatch Log Group Names found that match the fragment list
"""
	import boto3
	# import logging

	returnResponse = {}
	if serviceName is None:
		returnResponse = {'Success': False, 'ErrorMessage': 'No service name specified'}
		return returnResponse
	session_org = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_org = session_org.client('organizations')
	try:
		delResponse = client_org.disable_aws_service_access_for_organization(ServicePrincipal=serviceName)
		checkResponse = find_org_services2(ocredentials, serviceName)
		if len(checkResponse) == 0:
			returnResponse = {'Success': True, 'ErrorMessage': None}
		else:
			returnResponse = {'Success': False, 'ErrorMessage': 'Service didn\'t get deleted properly'}
	except (client_org.exceptions.AccessDeniedException, client_org.exceptions.AWSOrganizationsNotInUseException, client_org.exceptions.ConcurrentModificationException,
	        client_org.exceptions.ConstraintViolationException, client_org.exceptions.InvalidInputException, client_org.exceptions.ServiceException,
	        client_org.exceptions.TooManyRequestsException, client_org.exceptions.UnsupportedAPIEndpointException) as my_Error:
		error_message = f"Error disabling {serviceName} in account {ocredentials['AccountId']}\n" \
		                f"Full Error: {my_Error}"
		returnResponse.update({'Success': False, 'ErrorMessage': error_message})
	return returnResponse


def find_security_groups2(ocredentials, f_fragments: list = None, f_exact: bool = False, defaultOnly: bool = False) -> list:
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Region'] holds the region
	@param:  f_fragments - a list of fragments to search for
	@param:  f_exact - a boolean to indicate whether to use exact matching or not
	@param:  defaultOnly - a boolean to indicate whether to return only default security groups or not
	@return: list
	"""
	import boto3
	import logging

	SecurityGroups = []
	AllSecurityGroups = []
	session_vpc = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_vpc = session_vpc.client('ec2')
	logging.info(f"Looking for default Security Groups in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}")
	response = client_vpc.describe_security_groups()
	SecurityGroups.extend(response['SecurityGroups'])
	while 'NextToken' in response.keys():
		response = client_vpc.describe_security_groups(NextToken=response['NextToken'])
		SecurityGroups.extend(response['SecurityGroups'])
	for security_group in SecurityGroups:
		if security_group['GroupName'] == 'default':
			security_group['Default'] = True
			AllSecurityGroups.append(security_group)
		else:
			security_group['Default'] = False
			AllSecurityGroups.append(security_group) if defaultOnly is False else None
	logging.info(f"We found {len(AllSecurityGroups)} {'default' if defaultOnly else ''} Security Groups in account {ocredentials['AccountNumber']} in Region {ocredentials['Region']}")
	return AllSecurityGroups


def find_references_to_security_groups2(ocredentials, f_security_group: dict):
	"""
	Description: An effort to find all resources that might be referencing this security group

	@params: ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	@params: f_security_group - a dict object of the security group we're looking for
	In this function, we'll list all network interfaces, and query for those ENIs that mention the SG within.
	Additionally, we'll have to look through *other* security groups, and find any that reference this SG
	We may also need to look at peered VPCs, which could reference these SGs, which may be more effort...
	"""
	import boto3
	import logging

	session_vpc = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_vpc = session_vpc.client('ec2')
	SecurityGroupReferences = []
	logging.info(f"Looking for Security Groups in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}")

	# There are two places where Security Groups are referenced.
	# In ENIs, and in Security Groups.
	# This first lookup handles the ENI case.
	response = client_vpc.describe_network_interfaces(
		Filters=[
			{
				'Name'  : 'group-id',
				'Values': [f_security_group['GroupId']]
				},
			]
		)
	for network_interface in response['NetworkInterfaces']:
		network_interface['ResourceType'] = network_interface['InterfaceType']
		network_interface['Id'] = network_interface['NetworkInterfaceId']
		network_interface['AttachmentId'] = network_interface['Attachment']['InstanceId'] if 'InstanceId' in network_interface['Attachment'].keys() else None
		if 'InstanceId' in network_interface['Attachment'].keys():
			InstanceTags = client_vpc.describe_instances(InstanceIds=[network_interface['Attachment']['InstanceId']])['Reservations'][0]['Instances'][0]['Tags']
			InstanceNameTags = [x['Value'] for x in InstanceTags if x['Key'] == 'Name']
			network_interface['InstanceNameTag'] = InstanceNameTags[0]
		else:
			network_interface['InstanceNameTag'] = None
		network_interface['IpAddress'] = network_interface['PrivateIpAddress']
		SecurityGroupReferences.append(network_interface)
	while 'NextToken' in response.keys():
		response = client_vpc.describe_network_interfaces(
			Filters=[
				{
					'Name'  : 'group-id',
					'Values': [f_security_group['GroupId']]
					},
				]
			)
		for network_interface in response['NetworkInterfaces']:
			network_interface['ResourceType'] = network_interface['InterfaceType']
			network_interface['Id'] = network_interface['NetworkInterfaceId']
			network_interface['AttachmentId'] = network_interface['Attachment']['InstanceId'] if 'InstanceId' in network_interface['Attachment'].keys() else None
			if 'InstanceId' in network_interface['Attachment'].keys():
				InstanceTags = client_vpc.describe_instances(InstanceIds=[network_interface['Attachment']['InstanceId']])['Reservations'][0]['Instances'][0]['Tags']
				InstanceNameTags = [x['Value'] for x in InstanceTags if x['Key'] == 'Name']
				network_interface['InstanceNameTag'] = InstanceNameTags[0]
			else:
				network_interface['InstanceNameTag'] = None
			network_interface['IpAddress'] = network_interface['PrivateIpAddress']

			SecurityGroupReferences.append(network_interface)
	logging.info(f"We found {len(SecurityGroupReferences)} references to security groups in account {ocredentials['AccountNumber']} in Region {ocredentials['Region']}")
	# This second lookup section handles the other Security Groups case.
	response_inbound = client_vpc.describe_security_groups(
		Filters=[
			{
				'Name'  : 'ip-permission.group-id',
				'Values': [f_security_group['GroupId']]
				},
			]
		)
	for security_group in response_inbound['SecurityGroups']:
		security_group['ResourceType'] = 'InboundRule'
		# for rule in security_group['IpPermissions']:
		# 	rule['Protocol'] = 'AllTraffic' if rule['IpProtocol'] == '-1' else rule['IpProtocol']
		# for permission in security_group['IpPermissions']:
		# 	security_group['IpPermissions'].append(permission)
		security_group['Id'] = security_group['GroupId']
		SecurityGroupReferences.append(security_group)
	while 'NextToken' in response_inbound.keys():
		response_inbound = client_vpc.describe_security_groups(
			Filters=[
				{
					'Name'  : 'ip-permission.group-id',
					'Values': [f_security_group['GroupId']]
					},
				], NextToken=response_inbound['NextToken']
			)
		for security_group in response_inbound['SecurityGroups']:
			security_group['ResourceType'] = 'InboundRule'
			# for rule in security_group['IpPermissions']:
			# 	rule['Protocol'] = 'AllTraffic' if rule['IpProtocol'] == '-1' else rule['IpProtocol']
			security_group['Id'] = security_group['GroupId']
			SecurityGroupReferences.append(security_group)

	response_outbound = client_vpc.describe_security_groups(
		Filters=[
			{
				'Name'  : 'egress.ip-permission.group-id',
				'Values': [f_security_group['GroupId']]
				},
			]
		)
	for security_group in response_outbound['SecurityGroups']:
		security_group['ResourceType'] = 'OutboundRule'
		# for rule in security_group['IpPermissions']:
		# 	rule['Protocol'] = 'AllTraffic' if rule['IpProtocol'] == '-1' else rule['IpProtocol']
		security_group['Id'] = security_group['GroupId']
		SecurityGroupReferences.append(security_group)
	while 'NextToken' in response_outbound.keys():
		response_outbound = client_vpc.describe_security_groups(
			Filters=[
				{
					'Name'  : 'egress.ip-permission.group-id',
					'Values': [f_security_group['GroupId']]
					},
				], NextToken=response_outbound['NextToken']
			)
		for security_group in response_outbound['SecurityGroups']:
			security_group['ResourceType'] = 'OutboundRule'
			# for rule in security_group['IpPermissions']:
			# 	rule['Protocol'] = 'AllTraffic' if rule['IpProtocol'] == '-1' else rule['IpProtocol']
			security_group['Id'] = security_group['GroupId']
			SecurityGroupReferences.append(security_group)

	logging.info(f"We found {len(SecurityGroupReferences)} references to security groups in account {ocredentials['AccountNumber']} in Region {ocredentials['Region']}")
	return SecurityGroupReferences


def find_account_vpcs2(ocredentials, defaultOnly=False):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	"""
	import boto3
	import logging

	session_vpc = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_vpc = session_vpc.client('ec2')
	if defaultOnly:
		logging.info(f"Looking for default VPCs in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}")
		logging.info(f"defaultOnly: {str(defaultOnly)}")
		response = client_vpc.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
	else:
		logging.info(f"Looking for all VPCs in account {ocredentials['AccountNumber']} from Region {ocredentials['Region']}")
		logging.info(f"defaultOnly: {str(defaultOnly)}")
		response = client_vpc.describe_vpcs()
	# TODO: Enable pagination
	logging.info(f"We found {len(response['Vpcs'])} VPCs in account {ocredentials['AccountNumber']} in Region {ocredentials['Region']}")
	return response


def find_account_vpcs3(faws_acct, fRegion, defaultOnly=False):
	"""
	faws_acct uses the account_class object
	"""
	import logging

	client_vpc = faws_acct.session.client('ec2')
	# TODO: Enable pagination
	if defaultOnly:
		logging.info(f"Looking for default VPCs in account {faws_acct.acct_number} from Region {fRegion}")
		logging.info(f"defaultOnly: {str(defaultOnly)}")
		response = client_vpc.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
	else:
		logging.info(f"Looking for all VPCs in account {faws_acct.acct_number} from Region {fRegion}")
		logging.info(f"defaultOnly: {str(defaultOnly)}")
		response = client_vpc.describe_vpcs()
	logging.info(f"We found {len(response['Vpcs'])} VPCs")
	return response


def find_config_recorders2(ocredentials, fRegion):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number

	Returned object looks like:
	{
		"ConfigurationRecorders": [
			{
				"name": "AWS-Landing-Zone-BaselineConfigRecorder",
				"roleARN": "arn:aws:iam::123456789012:role/AWS-Landing-Zone-ConfigRecorderRole",
				"recordingGroup": {
					"allSupported": true,
					"includeGlobalResourceTypes": true,
					"resourceTypes": []
				}
			}
		]
	}

	Pagination isn't an issue here since only one config recorder per account / region is allowed.
	"""
	import boto3
	import logging
	session_cfg = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=fRegion)
	client_cfg = session_cfg.client('config')
	logging.info("Looking for Config Recorders in account %s from Region %s", ocredentials['AccountNumber'], fRegion)
	response = client_cfg.describe_configuration_recorders()
	# logging.info(response)
	return response


def del_config_recorder2(ocredentials, fRegion, fConfig_recorder_name):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	fRegion = region
	fConfig_recorder_name = Config Recorder Name
	"""
	import boto3
	import logging
	session_cfg = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
		'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	client_cfg = session_cfg.client('config')
	logging.error("Deleting Config Recorder %s from Region %s in account %s", fConfig_recorder_name, fRegion,
	              ocredentials['AccountNumber'])
	response = client_cfg.delete_configuration_recorder(ConfigurationRecorderName=fConfig_recorder_name)
	return response  # There is no response to send back


def find_delivery_channels2(ocredentials, fRegion):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number

	Returned object looks like:
	{
		'DeliveryChannels': [
		{
			'name': 'string',
			's3BucketName': 'string',
			's3KeyPrefix': 'string',
			'snsTopicARN': 'string',
			'configSnapshotDeliveryProperties': {
				'deliveryFrequency': 'One_Hour'|'Three_Hours'|'Six_Hours'|'Twelve_Hours'|'TwentyFour_Hours'
			}
		},
		]
	}

	Pagination isn't an issue here since delivery channels are limited to only one / account / region
	"""
	import boto3
	from botocore.exceptions import ClientError
	import logging

	session_cfg = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=fRegion)
	client_cfg = session_cfg.client('config')
	logging.info(f"Looking for Delivery Channels in account {ocredentials['AccountNumber']} from Region {fRegion}")
	response = {'Success': False, 'ErrorMessage': None}

	try:
		response.update(client_cfg.describe_delivery_channels())
		response.update({'Success': True})
	except ClientError as my_Error:
		logging.error(f"Error accessing {ocredentials['AccountId']} in region {fRegion}\n"
		              f"Error Message: {my_Error}")
		response.update({'ErrorMessage': my_Error})
	return response


def del_delivery_channel2(ocredentials, fRegion, fDelivery_channel_name):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	rRegion = region
	fDelivery_channel_name = delivery channel name
	"""
	import boto3
	import logging

	session_cfg = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
		'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	client_cfg = session_cfg.client('config')
	logging.error("Deleting Delivery Channel %s from Region %s in account %s", fDelivery_channel_name, fRegion,
	              ocredentials['AccountNumber'])
	response = client_cfg.delete_delivery_channel(DeliveryChannelName=fDelivery_channel_name)
	return response


def del_config_recorder_or_delivery_channel2(deletion_item):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	fRegion = region
	fConfig_recorder_name = Config Recorder Name
	"""
	import boto3
	import logging
	session_cfg = boto3.Session(aws_access_key_id=deletion_item['AccessKeyId'],
	                            aws_secret_access_key=deletion_item['SecretAccessKey'],
	                            aws_session_token=deletion_item['SessionToken'],
	                            region_name=deletion_item['Region'])
	client_cfg = session_cfg.client('config')
	logging.error(f"Deleting {deletion_item['Type']} '{deletion_item['name']}' from Region {deletion_item['Region']} in account {deletion_item['AccountId']}")
	response = {'Success': False, 'ErrorMessage': None}
	try:
		if deletion_item['Type'] == 'Config Recorder':
			response.update(client_cfg.delete_configuration_recorder(ConfigurationRecorderName=deletion_item['name']))
		elif deletion_item['Type'] == 'Delivery Channel':
			response.update(client_cfg.delete_delivery_channel(DeliveryChannelName=deletion_item['name']))
		response.update({'Success': True})
	except Exception as my_Error:
		response.update({'ErrorMessage': my_Error})
	return response  # There is no response to send back


def find_cloudtrails2(ocredentials, fRegion, fCloudTrailnames=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	fRegion = region
	fCloudTrailnames = List of CloudTrail names we're looking for (null value returns all cloud trails)

	Returned Object looks like this:
	{
		'trailList': [
			{
				'Name': 'string',
				'S3BucketName': 'string',
				'S3KeyPrefix': 'string',
				'SnsTopicName': 'string',
				'SnsTopicARN': 'string',
				'IncludeGlobalServiceEvents': True|False,
				'IsMultiRegionTrail': True|False,
				'HomeRegion': 'string',
				'TrailARN': 'string',
				'LogFileValidationEnabled': True|False,
				'CloudWatchLogsLogGroupArn': 'string',
				'CloudWatchLogsRoleArn': 'string',
				'KmsKeyId': 'string',
				'HasCustomEventSelectors': True|False,
				'HasInsightSelectors': True|False,
				'IsOrganizationTrail': True|False
			},
		]
	}
	CTtrails = Inventory_Modules.find_cloudtrails(account_creds, 'us-east-1', ['AWS-Landing-Zone-BaselineCloudTrail'])
	"""
	import boto3
	import logging
	from botocore.exceptions import ClientError

	session_ct = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                           aws_secret_access_key=ocredentials['SecretAccessKey'],
	                           aws_session_token=ocredentials['SessionToken'],
	                           region_name=fRegion)
	client_ct = session_ct.client('cloudtrail')
	logging.info(f"Looking for CloudTrail trails in account {ocredentials['AccountNumber']} from Region {fRegion}")
	fullresponse = []
	if fCloudTrailnames is None or len(
			fCloudTrailnames) == 0:  # Therefore - they're really looking for a list of trails
		try:
			response = client_ct.list_trails()
			fullresponse = response['Trails']
			if 'NextToken' in response.keys():
				while 'NextToken' in response.keys():
					response = client_ct.list_trails(NextToken=response['NextToken'])
					fullresponse.extend(response['Trails'])
		except ClientError as my_Error:
			logging.error(my_Error)
			fullresponse = {'Success': False, 'Error_Message': my_Error}
		return fullresponse
	else:
		# TODO: This doesn't work... Needs to be fixed.
		# TODO: The reason this doesn't work is because the user submits a *list* of names,
		#  but the function exits after only one match, so the min match is never found.
		# They've provided a list of trails and want specific info about them
		for trailname in fCloudTrailnames:
			error_message = f"{trailname} didn't work. Try Again"
			response = {'Success': False, 'Error_Message': error_message}
			try:
				response = client_ct.describe_trails(trailNameList=[trailname])
				fullresponse.extend(response['trailList'])
			except ClientError as my_Error:
				if str(my_Error).find("InvalidTrailNameException") > 0:
					logging.error("Bad CloudTrail name provided")
		# TODO: This is also wrong, since it belongs outside this try (remember - this is a list)
		# TODO: But since the top part is broken, I'm leaving this broken too.
		return fullresponse


def del_cloudtrails2(ocredentials, fRegion, fCloudTrail):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	fRegion = region
	fCloudTrail = CloudTrail we're deleting
	"""
	import boto3
	import logging

	session_ct = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
		'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	client_ct = session_ct.client('cloudtrail')
	logging.info("Deleting CloudTrail %s in account %s from Region %s", fCloudTrail,
	             ocredentials['AccountNumber'], fRegion)
	response = client_ct.delete_trail(Name=fCloudTrail)
	return response


# def check_cw_groups_retention2(ocredentials):
# 	AllCWLogGroups = []
# 	try:
# 		logging.info(f"Checking account {ocredentials['AccountId']} in region {ocredentials['Region']}")
# 		# TODO: Will eventually support a filter for string fragments, and retention periods
# 		CW_Groups = find_cw_groups_retention2(account_credentials, ocredentials['Region'])
# 		logging.info(f"Root Account: {faws_acct.acct_number} Account: {account['AccountId']} Region: {ocredentials['Region']} | Found {len(CW_Groups['logGroups'])} groups")
# 	except ClientError as my_Error:
# 		if "AuthFailure" in str(my_Error):
# 			logging.error(f"Authorization Failure accessing account {account['AccountId']} in {ocredentials['Region']} region")
# 			logging.warning(f"It's possible that the region {ocredentials['Region']} hasn't been opted-into")
# 			pass
# 	if 'logGroups' in CW_Groups.keys():
# 		for y in range(len(CW_Groups['logGroups'])):
# 			if 'retentionInDays' in CW_Groups['logGroups'][y].keys():
# 				CW_Groups['logGroups'][y]['Retention'] = Retention = CW_Groups['logGroups'][y]['retentionInDays']
# 			else:
# 				CW_Groups['logGroups'][y]['Retention'] = Retention = "Never"
# 				CW_Groups['logGroups'][y]['Name'] = Name = CW_Groups['logGroups'][y]['logGroupName']
# 				CW_Groups['logGroups'][y]['Size'] = Size = CW_Groups['logGroups'][y]['storedBytes']
# 				CW_Groups['logGroups'][y]['AccessKeyId'] = account_credentials['AccessKeyId']
# 				CW_Groups['logGroups'][y]['SecretAccessKey'] = account_credentials['SecretAccessKey']
# 				CW_Groups['logGroups'][y]['SessionToken'] = account_credentials['SessionToken']
# 				CW_Groups['logGroups'][y]['ParentProfile'] = faws_acct.credentials['Profile'] if faws_acct.credentials['Profile'] is not None else 'default'
# 				CW_Groups['logGroups'][y]['MgmtAccount'] = faws_acct.MgmtAccount
# 				CW_Groups['logGroups'][y]['AccountId'] = account_credentials['AccountId']
# 				CW_Groups['logGroups'][y]['Region'] = ocredentials['Region']
# 		# fmt = f'%-12s %-{account_number_format} %-15s %-10s %15d %-50s'
# 		# print(fmt % (faws_acct.acct_number, account['AccountId'], region, Retention, Size, Name))
# 		# print(f"{str(faws_acct.acct_number):{account_number_format}} {str(account['AccountId']):{account_number_format}} {region:15s} "
# 		# 	  f"{str(Retention):10s} {'' if Retention == 'Never' else 'days'} {Size: >15,} {Name:50s}")
# 		AllCWLogGroups.extend(CW_Groups['logGroups'])
#
# 	return AllCWLogGroups


def find_gd_invites2(ocredentials, fRegion):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	fRegion = region
	"""
	import boto3
	import logging

	from botocore.exceptions import ClientError

	session_gd = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
		'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	client_gd = session_gd.client('guardduty')
	logging.info("Looking for GuardDuty invitations in account %s from Region %s",
	             ocredentials['AccountNumber'], fRegion)
	try:
		response = client_gd.list_invitations()
	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			print(ocredentials['AccountNumber'] + ": Authorization Failure for account {}".format(
				ocredentials['AccountNumber']))
		if str(my_Error).find("security token included in the request is invalid") > 0:
			print("Account #:" + ocredentials[
				'AccountNumber'] + f" - It's likely that the region you're trying ({fRegion}) isn't enabled for your account")
		else:
			print(my_Error)
		response = {'Invitations': []}
	return response


def delete_gd_invites2(ocredentials, fRegion, fAccountId):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
	fRegion = region
	"""
	import boto3
	import logging

	from botocore.exceptions import ClientError

	session_gd = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
		'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	client_gd = session_gd.client('guardduty')
	logging.info("Looking for GuardDuty invitations in account %s in Region %s",
	             ocredentials['AccountNumber'], fRegion)
	try:
		response = client_gd.delete_invitations(AccountIds=[fAccountId])
		return response['Invitations']
	except ClientError as my_Error:
		if "AuthFailure" in str(my_Error):
			print(f"{ocredentials['AccountNumber']}: Authorization Failure for account {ocredentials['AccountNumber']}")
		if str(my_Error).find("security token included in the request is invalid") > 0:
			print(
				f"Account #:{ocredentials['AccountNumber']} - It's likely that the region you're trying ({fRegion}) isn't enabled for your account")
		else:
			print(my_Error)


def find_account_instances2(ocredentials, fRegion='us-east-1'):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	import logging

	if 'Profile' in ocredentials.keys() and ocredentials['Profile'] is not None:
		ProfileAccountNumber = find_account_number(ocredentials['Profile'])
		logging.info(
			f"Profile: {ocredentials['Profile']} | Profile Account Number: {ProfileAccountNumber} | Account Number passed in: {ocredentials['AccountNumber']}")
		if ProfileAccountNumber == ocredentials['AccountNumber']:
			session_ec2 = boto3.Session(profile_name=ocredentials['Profile'],
			                            region_name=fRegion)
		else:
			session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
			                            aws_secret_access_key=ocredentials['SecretAccessKey'],
			                            aws_session_token=ocredentials['SessionToken'],
			                            region_name=fRegion)
	else:
		session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
		                            aws_secret_access_key=ocredentials['SecretAccessKey'],
		                            aws_session_token=ocredentials['SessionToken'],
		                            region_name=fRegion)
	instance_info = session_ec2.client('ec2')
	logging.info(f"Looking for instances in account # {ocredentials['AccountNumber']} in region {fRegion}")
	instances = instance_info.describe_instances()
	AllInstances = instances
	while 'NextToken' in instances.keys():
		instances = instance_info.describe_instances(NextToken=instances['NextToken'])
		AllInstances['Reservations'].extend(instances['Reservations'])
	return AllInstances


def find_cw_groups_retention2(ocredentials, fRegion: str = 'us-east-1'):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Region'] holds the region
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	import logging

	session_cw = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                           aws_secret_access_key=ocredentials['SecretAccessKey'],
	                           aws_session_token=ocredentials['SessionToken'],
	                           region_name=fRegion)
	log_group_info = session_cw.client('logs')
	logging.info(f"Looking for cw_groups in account # {ocredentials['AccountNumber']} in region {fRegion}")
	log_groups = log_group_info.describe_log_groups()
	# TODO: Will need to add some kind of string fragment filter here later
	# TODO: Also want to add a "retention filter" here as well to only find log groups matching a certain retention period
	AllLogGroups = log_groups['logGroups']
	while 'NextToken' in log_groups.keys():
		log_groups = log_group_info.describe_instances(NextToken=log_groups['NextToken'])
		AllLogGroups.extend(log_groups['logGroups'])
	return AllLogGroups


def find_account_rds_instances2(ocredentials, fRegion='us-east-1'):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	import logging

	if 'Profile' in ocredentials.keys() and ocredentials['Profile'] is not None:
		ProfileAccountNumber = find_account_number(ocredentials['Profile'])
		logging.info(
			f"Profile: {ocredentials['Profile']} | Profile Account Number: {ProfileAccountNumber} | Account Number passed in: {ocredentials['AccountNumber']}")
		if ProfileAccountNumber == ocredentials['AccountNumber']:
			session_rds = boto3.Session(profile_name=ocredentials['Profile'], region_name=fRegion)
		else:
			session_rds = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
			                            aws_secret_access_key=ocredentials['SecretAccessKey'],
			                            aws_session_token=ocredentials['SessionToken'],
			                            region_name=fRegion)
	else:
		session_rds = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
			'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	instance_info = session_rds.client('rds')
	logging.info(f"Looking for RDS instances in account #{ocredentials['AccountNumber']} in region {fRegion}")
	instances = instance_info.describe_db_instances()
	AllInstances = instances
	while 'NextToken' in instances.keys():
		instances = instance_info.describe_db_instances(NextToken=instances['NextToken'])
		AllInstances['DBInstances'].extend(instances['DBInstances'])
	return AllInstances


def find_account_cloudtrail2(ocredentials, fRegion='us-east-1'):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	import logging

	if 'Profile' in ocredentials.keys() and ocredentials['Profile'] is not None:
		ProfileAccountNumber = find_account_number(ocredentials['Profile'])
		logging.info(
			f"Profile: {ocredentials['Profile']} | Profile Account Number: {ProfileAccountNumber} | Account Number passed in: {ocredentials['AccountNumber']}")
		if ProfileAccountNumber == ocredentials['AccountNumber']:
			session_ct = boto3.Session(profile_name=ocredentials['Profile'], region_name=fRegion)
		else:
			session_ct = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
			                           aws_secret_access_key=ocredentials['SecretAccessKey'],
			                           aws_session_token=ocredentials['SessionToken'],
			                           region_name=fRegion)
	else:
		session_ct = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'], aws_secret_access_key=ocredentials[
			'SecretAccessKey'], aws_session_token=ocredentials['SessionToken'], region_name=fRegion)
	instance_info = session_ct.client('cloudtrail')
	logging.info(f"Looking for CloudTrail logging in account #{ocredentials['AccountNumber']} in region {fRegion}")
	Trails = instance_info.describe_trails(trailNameList=[], includeShadowTrails=True)
	AllTrails = Trails
	while 'NextToken' in Trails.keys():
		Trails = instance_info.describe_trails(NextToken=Trails['NextToken'])
		AllTrails['trailList'].extend(Trails['trailList'])
	return AllTrails


# def find_account_subnets2(ocredentials, fRegion=None, fipaddresses=None):
def find_account_subnets2(ocredentials, fipaddresses=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Region'] holds the region being accessed
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	from botocore.exceptions import ClientError
	import logging
	import ipaddress

	if 'Region' not in ocredentials.keys() or ocredentials['Region'] is None:
		ocredentials['Region'] = 'us-east-1'
	if 'Profile' in ocredentials.keys() and ocredentials['Profile'] is not None:
		ProfileAccountNumber = find_account_number(ocredentials['Profile'])
		logging.info(
			f"Profile: {ocredentials['Profile']} | Profile Account Number: {ProfileAccountNumber} | Account Number passed in: {ocredentials['AccountNumber']}")
		if ProfileAccountNumber == ocredentials['AccountNumber']:
			session_ec2 = boto3.Session(profile_name=ocredentials['Profile'],
			                            region_name=ocredentials['Region'])
		else:
			session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
			                            aws_secret_access_key=ocredentials['SecretAccessKey'],
			                            aws_session_token=ocredentials['SessionToken'],
			                            region_name=ocredentials['Region'])
	else:
		session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
		                            aws_secret_access_key=ocredentials['SecretAccessKey'],
		                            aws_session_token=ocredentials['SessionToken'],
		                            region_name=ocredentials['Region'])
	subnet_info = session_ec2.client('ec2')
	Subnets = {'NextToken': None}
	AllSubnets = {'Subnets': []}

	while 'NextToken' in Subnets.keys():
		# Had to add this so that a failure of the describe_subnet function doesn't cause a race condition
		Subnets = dict()
		try:
			if fipaddresses is None:
				logging.info(f"Looking for all subnets in account #{ocredentials['AccountNumber']} in region {ocredentials['Region']}")
				Subnets = subnet_info.describe_subnets()
				AllSubnets = Subnets
			else:
				logging.info(f"Looking for Subnets that match any of {fipaddresses} in account #{ocredentials['AccountNumber']} in region {ocredentials['Region']}")
				Subnets = subnet_info.describe_subnets()
				# Run through each of the subnets, and determine if the passed in IP address fits within any of them
				# If it does - then include that data within the array, otherwise next...
				for subnet in Subnets['Subnets']:
					for address in fipaddresses:
						logging.info(f"{address} in {subnet['CidrBlock']}: {ipaddress.ip_address(address) in ipaddress.ip_network(subnet['CidrBlock'])}")
						if ipaddress.ip_address(address) in ipaddress.ip_network(subnet['CidrBlock']):
							AllSubnets['Subnets'].append(subnet)
		except ClientError as my_Error:
			logging.error(f"Error connecting to account {ocredentials['AccountNumber']} in region {ocredentials['Region']}\n"
			              f"This is likely due to '{ocredentials['Region']}' not being enabled for your account\n"
			              f"Error Message: {my_Error}")
			continue
	return AllSubnets


def find_account_enis2(ocredentials, fRegion=None, fipaddresses=None):
	"""
	@param: ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the region
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	@param: fRegion is a string specifying which region we're looking at
	@param: fipaddresses is a list of IP addresses to search for

	"""
	import boto3
	from botocore.exceptions import ClientError
	import logging

	if fRegion is None and 'Region' in ocredentials.keys():
		fRegion = ocredentials['Region']
	elif fRegion is None:
		fRegion = 'us-east-1'

	session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	eni_info = session_ec2.client('ec2')
	ENIs = {'NextToken': None}
	AllENIs = []
	return_this_result = True if fipaddresses is None else False

	while 'NextToken' in ENIs.keys():
		# Had to add this so that a failure of the describe_subnet function doesn't cause a race condition
		ENIs = dict()
		try:
			logging.info(f"Looking for ENIs that match any of {fipaddresses} in account #{ocredentials['AccountNumber']} in region {fRegion}")
			ENIs = eni_info.describe_network_interfaces()
			for interface in ENIs['NetworkInterfaces']:
				if fipaddresses is not None:
					return_this_result = False
					for address in fipaddresses:
						if address == interface['PrivateIpAddress']:
							logging.info(f"Found it - {interface['PrivateIpAddress']} - ENI: {interface['NetworkInterfaceId']}")
							return_this_result = True
						elif 'Association' in interface.keys() and 'PublicIp' in interface['Association'].keys() and address == interface['Association']['PublicIp']:
							logging.info(f"Found it - {interface['Association']['PublicIp']} - ENI: {interface['NetworkInterfaceId']}")
							return_this_result = True
						else:
							continue
				if return_this_result:
					Name = None
					if 'TagSet' in interface.keys():
						for tag in interface['TagSet']:
							if tag['Key'] == 'Name':
								Name = tag['Value']
					AllENIs.append({
						'Name'            : Name,
						'AccountId'       : ocredentials['AccountNumber'],
						'Region'          : ocredentials['Region'],
						'ENIId'           : interface['NetworkInterfaceId'],
						'InterfaceType'   : interface['InterfaceType'],
						'PrivateDnsName'  : interface['PrivateDnsName'],
						'PrivateIpAddress': interface['PrivateIpAddress'],
						'Status'          : interface['Status'],
						'VpcId'           : interface['VpcId'] if 'VpcId' in interface.keys() else "No VPC Associated",
						'InstanceId'      : interface['Attachment']['InstanceId'] if ('Attachment' in interface.keys() and 'InstanceId' in interface['Attachment'].keys()) else "No instance association",
						'AttachmentStatus': interface['Attachment']['Status'] if 'Attachment' in interface.keys() else "Not attached",
						'PublicIp'        : interface['Association']['PublicIp'] if 'Association' in interface.keys() and 'PublicIp' in interface['Association'].keys() else "No Public IP", })
		except ClientError as my_Error:
			logging.error(f"Error connecting to account {ocredentials['AccountNumber']} in region {fRegion}\n"
			              f"This is likely due to '{fRegion}' not being enabled for your account\n"
			              f"Error Message: {my_Error}")
			continue
		except KeyError as my_Error:
			logging.error(f"Some kind of KeyError\n"
			              f"Error Message: {my_Error}")
			continue
	return AllENIs


def find_account_volumes2(ocredentials):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the region
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	from botocore.exceptions import ClientError
	import logging

	session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	ebs_info = session_ec2.client('ec2')
	Volumes = {'NextToken': None}
	AllVolumes = []
	# return_this_result = True if fipaddresses is None else False

	while 'NextToken' in Volumes.keys():
		# Had to add this so that a failure of the describe_subnet function doesn't cause a race condition
		Volumes = dict()
		try:
			logging.info(f"Looking for all volumes in account #{ocredentials['AccountNumber']} in region {ocredentials['Region']}")
			Volumes = ebs_info.describe_volumes()
			# Run through each of the volumes, and determine if the passed in fragment fits within any of them
			# If it does - then include that data within the array, otherwise next...
			for volume in Volumes['Volumes']:
				Name = 'None'
				AttachmentList = []
				if 'Tags' in volume.keys():
					for tag in volume['Tags']:
						if tag['Key'] == 'Name':
							Name = tag['Value']
				if 'Attachments' in volume.keys():
					for attachment in volume['Attachments']:
						if 'InstanceId' in attachment.keys():
							AttachmentList.append({'InstanceId'      : attachment['InstanceId'],
							                       'AttachmentStatus': attachment['State']})
				AllVolumes.append({
					'VolumeName' : Name,
					'AccountId'  : ocredentials['AccountNumber'],
					'Region'     : ocredentials['Region'],
					'Encrypted'  : volume['Encrypted'],
					'VolumeId'   : volume['VolumeId'],
					'VolumeType' : volume['VolumeType'],
					'Iops'       : volume['Iops'],
					'Size'       : volume['Size'],
					'State'      : volume['State'],
					# 'KmsKeyId'   : volume['KmsKeyId'] if volume['Encrypted'] else None,
					'Throughput' : volume['Throughput'] if 'Throughput' in volume.keys() else None,
					'Attachments': AttachmentList})
				logging.info(f"Wrote volume id {volume['VolumeId']} into 'AllVolumes' list")
		except ClientError as my_Error:
			logging.error(f"Error connecting to account {ocredentials['AccountNumber']} in region {ocredentials['Region']}\n"
			              f"This is likely due to '{ocredentials['Region']}' not being enabled for your account\n"
			              f"Error Message: {my_Error}")
			continue
		except KeyError as my_Error:
			logging.error(f"Some kind of KeyError\n"
			              f"Error Message: {my_Error}")
			continue
	return AllVolumes


def find_account_policies2(ocredentials, fRegion='us-east-1', fFragments: list = None, fExact: bool = False, fCMP: bool = False) -> list:
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	fRegion is the region in which you're looking for policies
	fFragments is a list of fragments you might be looking for in the policy name
	fExact is whether the string fragment passed in should match what's found exactly, or not.
	fCMP is a flag to determine whether you want to retrieve ONLY Customer Managed Policies, to limit the policies passed back
	"""
	import boto3
	from botocore.exceptions import ClientError
	import logging

	session_iam = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	policy_info = session_iam.client('iam')
	AllPolicies = []
	first_time = True
	marker = Policies = None
	while first_time or Policies['IsTruncated']:
		# Had to add this so that a failure of the describe_policy function doesn't cause a race condition
		try:
			if first_time:
				logging.info(f"Looking in account #{ocredentials['AccountNumber']} for policies")
				if fCMP:
					Policies = policy_info.list_policies(Scope='Local')
				else:
					Policies = policy_info.list_policies()
				first_time = False
			else:
				if fCMP:
					Policies = policy_info.list_policies(Marker=marker, Scope='Local')
				# Policies = policy_info.list_policies(Marker=Policies['Marker'])
				else:
					Policies = policy_info.list_policies(Marker=marker)
			# Policies = policy_info.list_policies(Marker=Policies['Marker'], Scope='Local')
			marker = Policies['Marker'] if Policies['IsTruncated'] else None
			# marker = "skfjhskfjhsdfkjh"
			for policy in Policies['Policies']:
				if fFragments is None or 'all' in fFragments:
					policy.update({'AccountNumber': ocredentials['AccountNumber'],
					               'MgmtAccount'  : ocredentials['MgmtAccount'],
					               'Region'       : ocredentials['Region']})
					AllPolicies.append(policy)
				elif fExact:
					for fragment in fFragments:
						if fragment == policy['PolicyName']:
							# Run through each of the policies, and determine if the passed in policy fragment matches the policy name
							# If it does - then include that policy within the returned list, otherwise next...
							policy.update({'AccountNumber': ocredentials['AccountNumber'],
							               'MgmtAccount'  : ocredentials['MgmtAccount'],
							               'Region'       : ocredentials['Region']})
							AllPolicies.append(policy)
				elif not fExact:
					for fragment in fFragments:
						if fragment in policy['PolicyName']:
							# Run through each of the policies, and determine if the passed in policy fragment matches any part of the policy name
							# If it does - then include that policy within the returned list, otherwise next...
							policy.update({'AccountNumber': ocredentials['AccountNumber'],
							               'MgmtAccount'  : ocredentials['MgmtAccount'],
							               'Region'       : ocredentials['Region']})
							AllPolicies.append(policy)
			logging.info(f"Found {len(AllPolicies)} matching policies within account #{ocredentials['AccountNumber']}")
		except ClientError as my_Error:
			logging.error(f"Error connecting to account {ocredentials['AccountNumber']} in region {fRegion}\n"
			              f"This is likely due to '{fRegion}' not being enabled for your account\n"
			              f"Error Message: {my_Error}")
			continue
	return AllPolicies


def find_account_policies3(faws_acct, fRegion='us-east-1', fFragments=None):
	"""
	faws_acct is an aws_acct object
	fRegion is the region in which you're looking for policies
	fFragments is a list of fragments you might be looking for in the policy name
	"""
	from botocore.exceptions import ClientError
	import logging

	logging.info(f"Account: {faws_acct.acct_number}")
	client_iam = faws_acct.session.client('iam')
	Policies = {'IsTruncated': True}
	AllPolicies = []
	first_time = True

	while Policies['IsTruncated']:
		# Had to add this so that a failure of the describe_policy function doesn't cause a race condition
		try:
			logging.info(f"Looking for all policies that exist within account #{faws_acct.acct_number}")
			if first_time:
				Policies = client_iam.list_policies()
				first_time = False
			else:
				Policies = client_iam.list_policies(Marker=Policies['Marker'])
			for policy in Policies['Policies']:
				if fFragments is None:
					policy.update({'AccountNumber': faws_acct.acct_number,
					               'MgmtAccount'  : faws_acct.MgmtAccount,
					               'Region'       : fRegion})
					AllPolicies.append(policy)
				else:
					for fragment in fFragments:
						if fragment in policy['PolicyName']:
							# Run through each of the policies, and determine if the passed in action fits within any of them
							# If it does - then include that data within the array, otherwise next...
							policy.update({'AccountNumber': faws_acct.acct_number,
							               'MgmtAccount'  : faws_acct.MgmtAccount,
							               'Region'       : fRegion})
							AllPolicies.append(policy)
		except ClientError as my_Error:
			logging.error(f"Error connecting to account {faws_acct.acct_number} in region {fRegion}\n"
			              f"This is likely due to '{fRegion}' not being enabled for your account\n"
			              f"Error Message: {my_Error}")
			continue
	return AllPolicies


def find_policy_action2(ocredentials, fpolicy, f_action):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the account number
		- ['Profile'] can hold the profile, instead of the session credentials
	"""
	import boto3
	from botocore.exceptions import ClientError
	import logging

	fRegion = 'us-east-1'
	if 'Profile' in ocredentials.keys() and ocredentials['Profile'] is not None:
		ProfileAccountNumber = find_account_number(ocredentials['Profile'])
		logging.info(
			f"Profile: {ocredentials['Profile']} | Profile Account Number: {ProfileAccountNumber} | Account Number passed in: {ocredentials['AccountNumber']}")
		if ProfileAccountNumber == ocredentials['AccountNumber']:
			session_iam = boto3.Session(profile_name=ocredentials['Profile'], region_name=fRegion)
		else:
			session_iam = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
			                            aws_secret_access_key=ocredentials['SecretAccessKey'],
			                            aws_session_token=ocredentials['SessionToken'],
			                            region_name=fRegion)
	else:
		session_iam = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
		                            aws_secret_access_key=ocredentials['SecretAccessKey'],
		                            aws_session_token=ocredentials['SessionToken'],
		                            region_name=fRegion)
	policy_info = session_iam.client('iam')
	results = list()

	try:
		logging.debug(f"Getting policy statements for policy {fpolicy} that exists within account #{ocredentials['AccountNumber']}")
		Policy_statements = policy_info.get_policy_version(PolicyArn=fpolicy['Arn'], VersionId=fpolicy['DefaultVersionId'])['PolicyVersion']
		# Run through each of the policies, and determine if the passed in action fits within any of them
		# If it does - then include that data within the array, otherwise next...
		for policy_statement in Policy_statements['Document']['Statement']:
			for key, value in policy_statement.items():
				result = {'Success': False}
				if key == 'Action':
					try:
						# TODO: When this is called from two sepaarte threads for the same statement, there's some caching going on that duplicates the result added to the results dict.
						if isinstance(value, list):
							for action in value:
								if action.find(f_action) >= 0:
									result.update(fpolicy)
									result.update({'Success'       : True,
									               'message'       : f"Found action '{f_action}' in policy '{fpolicy['PolicyName']}' in set of actions '{value}' as single action '{action}'",
									               'PolicyName'    : fpolicy['PolicyName'],
									               'Statement'     : policy_statement,
									               'SearchedAction': f_action,
									               'PolicyAction'  : action})
									results.append(result)
						elif isinstance(value, str):
							action = value
							if action.find(f_action) >= 0:
								result.update(fpolicy)
								result.update({'Success'       : True,
								               'message'       : f"Found action '{f_action}' in policy '{fpolicy['PolicyName']}' in single action '{value}'",
								               'PolicyName'    : fpolicy['PolicyName'],
								               'Statement'     : policy_statement,
								               'SearchedAction': f_action,
								               'PolicyAction'  : action})
								results.append(result)
					except Exception as my_Error:
						logging.error(f"Error in statements: {my_Error}")
		return results
	except ClientError as my_Error:
		logging.error(f"Error connecting to account {ocredentials['AccountNumber']}\n"
		              f"Error Message: {my_Error}")
	return results


def find_iam_users2(ocredentials):
	"""
	ocredentials is an object with the following structure:
		- ['AccountId'] holds the Account ID for the account you're looking for
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the region
	"""
	import boto3
	import logging

	users = []
	logging.info(f"Account ID #: {str(ocredentials['AccessKeyId'])}")
	session_iam = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'] if 'Region' in ocredentials.keys() else 'us-east-1')
	client_iam = session_iam.client('iam')
	user_info = client_iam.list_users()
	for user in user_info['Users']:
		user['Type'] = 'IAM User'
		user['Region'] = ocredentials['Region']
		user['AccountId'] = ocredentials['AccountId']
		user['MgmtAccount'] = ocredentials['MgmtAccount']
		users.append(user)
	while 'Marker' in user_info.keys():
		user_info = client_iam.list_users(Marker=user_info['Marker'])
		for user in user_info['Users']:
			user['Type'] = 'IAM User'
			user['Region'] = ocredentials['Region']
			user['AccountId'] = ocredentials['AccountId']
			user['MgmtAccount'] = ocredentials['MgmtAccount']
			users.append(user)
	return users


def find_idc_directory_id2(ocredentials) -> list:
	"""
	Description: Finds the IDC Directory ID
	@param ocredentials: AWS Credentials
	@return: Returns the IDC Directory ID
	"""
	import boto3
	session_idc = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'] if 'Region' in ocredentials.keys() else 'us-east-1')

	client_idc = session_idc.client('sso-admin')
	all_idc_info_list = []
	idc_info = client_idc.list_instances()
	all_idc_info_list.extend(idc_info['Instances'])
	while 'NextToken' in idc_info.keys():
		idc_info = client_idc.list_instances(NextToken=idc_info['NextToken'])
		all_idc_info_list.extend(idc_info['Instances'])
	idc_directory_id_list = [instance['IdentityStoreId'] for instance in all_idc_info_list if 'IdentityStoreId' in instance.keys()]
	return idc_directory_id_list


def find_idc_users2(ocredentials, f_IdentityStoreId: str) -> list:
	"""
	Description: This function will find all users in an Identity Store.
	@param  ocredentials: The credentials for the account you're looking in.
		- ['AccountId'] holds the Account ID for the account you're looking for
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the region
	@param f_IdentityStoreId: The Id of the Identity Store you're looking for users in.
	@return : A list of users in the Identity Store.
	"""
	import boto3
	import logging

	if f_IdentityStoreId is None:
		logging.info("No Identity Store ID was provided.\n"
		             "Likely this account doesn't have an Identity Center Directory configured to keep users")
		return []
	users = []
	logging.info(f"Account ID #: {str(ocredentials['AccountId'])}")
	session_idc = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'] if 'Region' in ocredentials.keys() else 'us-east-1')
	client_idc = session_idc.client('identitystore')
	user_info = client_idc.list_users(IdentityStoreId=f_IdentityStoreId)
	for user in user_info['Users']:
		user['Type'] = 'IDC User'
		user['Region'] = ocredentials['Region']
		user['AccountId'] = ocredentials['AccountId']
		user['MgmtAccount'] = ocredentials['MgmtAccount']
		users.append(user)
	while 'NextToken' in user_info.keys():
		user_info = client_idc.list_users(NextToken=user_info['NextToken'], IdentityStoreId=f_IdentityStoreId)
		for user in user_info['Users']:
			user['Type'] = 'IDC User'
			user['Region'] = ocredentials['Region']
			user['AccountId'] = ocredentials['AccountId']
			user['MgmtAccount'] = ocredentials['MgmtAccount']
			users.append(user)
	return users


def find_profile_vpcs(fProfile, fRegion, fDefaultOnly):
	import boto3
	session_ec2 = boto3.Session(profile_name=fProfile, region_name=fRegion)
	vpc_info = session_ec2.client('ec2')
	if fDefaultOnly:
		vpcs = vpc_info.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
	else:
		vpcs = vpc_info.describe_vpcs()
	return vpcs


def find_profile_functions(fProfile, fRegion):
	import boto3
	session_lambda = boto3.Session(profile_name=fProfile, region_name=fRegion)
	lambda_info = session_lambda.client('lambda')
	functions = lambda_info.list_functions()
	return functions


def find_lambda_functions2(ocredentials, fRegion='us-east-1', fSearchStrings=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the AccountId
		- ['Region'] holds the region for the credentials (optional)
	fRegion is a string
	fSearchString is a list of strings
	"""
	import boto3
	import logging

	if fSearchStrings is None:
		fSearchStrings = ['all']
	if 'Region' in ocredentials.keys():
		fRegion = ocredentials['Region']
	session_lambda = boto3.Session(region_name=fRegion,
	                               aws_access_key_id=ocredentials['AccessKeyId'],
	                               aws_secret_access_key=ocredentials['SecretAccessKey'],
	                               aws_session_token=ocredentials['SessionToken'])
	client_lambda = session_lambda.client('lambda')
	# TODO: Consider using try..except here to handle errors in the API call
	functions = client_lambda.list_functions()['Functions']
	functions2 = []
	if 'all' in fSearchStrings:
		for i in range(len(functions)):
			logging.info(f"Found function {functions[i]['FunctionName']}")
			functions2.append({'FunctionName': functions[i]['FunctionName'],
			                   'FunctionArn' : functions[i]['FunctionArn'],
			                   'Role'        : functions[i]['Role'],
			                   'Runtime'     : functions[i]['Runtime']})
		return functions2
	else:
		for i in range(len(functions)):
			for searchitem in fSearchStrings:
				if searchitem in functions[i]['FunctionName'] or searchitem in functions[i]['Runtime']:
					logging.info(f"Found function {functions[i]['FunctionName']} with runtime {functions[i]['Runtime']}")
					functions2.append({'FunctionName': functions[i]['FunctionName'],
					                   'FunctionArn' : functions[i]['FunctionArn'],
					                   'Role'        : functions[i]['Role'],
					                   'Runtime'     : functions[i]['Runtime']})
		return functions2


def find_lambda_functions3(faws_acct, fRegion='us-east-1', fSearchStrings=None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the AccountId
	fRegion is a string
	fSearchString is a list of strings
	"""
	import logging

	functions2 = []
	# TODO: Add pagination here
	try:
		client_lambda = faws_acct.session.client('lambda', region_name=fRegion)
		functions = client_lambda.list_functions()['Functions']
	except AttributeError as my_Error:
		logging.info(f"Error: {my_Error}")
		return functions2
	if fSearchStrings is None:
		for i in range(len(functions)):
			logging.info(f"Found function {functions[i]['FunctionName']}")
			functions2.append({'FunctionName': functions[i]['FunctionName'],
			                   'FunctionArn' : functions[i]['FunctionArn'], 'Role': functions[i]['Role']})
	else:
		for i in range(len(functions)):
			for searchitem in fSearchStrings:
				if searchitem in functions[i]['FunctionName']:
					logging.info(f"Found function {functions[i]['FunctionName']}")
					functions2.append({'FunctionName': functions[i]['FunctionName'],
					                   'FunctionArn' : functions[i]['FunctionArn'], 'Role': functions[i]['Role']})
	return functions2


def get_lambda_code_url(fprofile, fregion, fFunctionName):
	import boto3
	session_lambda = boto3.Session(profile_name=fprofile, region_name=fregion)
	client_lambda = session_lambda.client('lambda')
	code_url = client_lambda.get_function(FunctionName=fFunctionName)['Code']['Location']
	return code_url


def find_directories2(ocredentials, fRegion='us-east-1', fSearchStrings=None, fExact: bool = False):
	"""
	Description: This function will search for directories in an account/region
	@param: ocredentials is an aws_acct object
	@param: fRegion is a string
	@param: fSearchString is a list of strings
	@param: fExact is a boolean to determine whether to search for an exact match or a fragment
	@return: List of directories found in account/ region
	"""
	import logging
	import boto3

	directories2 = []
	directories = []
	all_directories = []
	try:
		session_ds = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
		                           aws_secret_access_key=ocredentials['SecretAccessKey'],
		                           region_name=ocredentials['Region'],
		                           aws_session_token=ocredentials['SessionToken'])
		client_ds = session_ds.client('ds', region_name=fRegion)
		# TODO: Need paging here
		directories = client_ds.describe_directories()
		all_directories.extend(directories['DirectoryDescriptions'])
		while 'NextToken' in directories.keys():
			directories = client_ds.describe_directories(NextToken=directories['NextToken'])
			all_directories.extend(directories['DirectoryDescriptions'])
		logging.info(f"Found {len(all_directories)} directories: {all_directories}")
	except AttributeError as my_Error:
		logging.info(f"Error: {my_Error}")
	if fSearchStrings is None or 'all' in fSearchStrings:
		# If we're sending everything back
		for directory in all_directories:
			logging.info(f"Found directory {directory['Name']}")
			response_dict = {'DirectoryName': directory['Name'],
			                 'DirectoryId'  : directory['DirectoryId'],
			                 'Status'       : directory.get('ShareStatus', 'Owned'),
			                 'Type'         : directory['Type'], }
			if 'RegionsInfo' in directory:
				response_dict.update({'HomeRegion': directory['RegionsInfo'].get('PrimaryRegion', None)})
			else:
				response_dict.update({'HomeRegion': fRegion})
			if 'OwnerDirectoryDescription' in directory:
				response_dict.update({'Owner': directory['OwnerDirectoryDescription'].get('AccountId', None)})
			else:
				response_dict.update({'Owner': ocredentials['AccountId']})
			directories2.append(response_dict)
		return directories2
	else:
		# If we're only sending back that which matches a fragment or EXACT
		for directory in all_directories:
			for searchitem in fSearchStrings:
				Collectitem = False
				if fExact and (searchitem == directory['Name'] or searchitem == directory['DirectoryId']):
					Collectitem = True
				elif not fExact and (searchitem in directory['Name'] or searchitem in directory['DirectoryId']):
					Collectitem = True
				if Collectitem:
					logging.info(f"Found fragment {searchitem} in directory {directory['Name']} in account {ocredentials['AccountId']}")
					response_dict = {'DirectoryName': directory['Name'],
					                 'DirectoryId'  : directory['DirectoryId'],
					                 'Status'       : directory.get('ShareStatus', 'Owned'),
					                 'Type'         : directory['Type']}
					if 'RegionsInfo' in directory:
						response_dict.update({'HomeRegion': directory['RegionsInfo'].get('PrimaryRegion', None)})
					else:
						response_dict.update({'HomeRegion': fRegion})
					if 'OwnerDirectoryDescription' in directory:
						response_dict.update({'Owner': directory['OwnerDirectoryDescription'].get('AccountId', None)})
					else:
						response_dict.update({'Owner': ocredentials['AccountId']})
					directories2.append(response_dict)
		return directories2


# def find_directories3(faws_acct, fRegion='us-east-1', fSearchStrings=None):
# 	"""
# 	faws_acct is an aws_acct object
# 	fRegion is a string
# 	fSearchString is a list of strings
# 	"""
# 	import logging
#
# 	directories2 = []
# 	# TODO: Add pagination here
# 	try:
# 		client_ds = faws_acct.session.client('ds', region_name=fRegion)
# 		directories = client_ds.describe_directories()['DirectoryDescriptions']
# 		logging.info(f"Found {len(directories)} directories")
# 	except AttributeError as my_Error:
# 		logging.info(f"Error: {my_Error}")
# 		return directories2
# 	if fSearchStrings is None or 'all' in fSearchStrings:
# 		for directory in directories:
# 			logging.info(f"Found directory {directory['Name']}")
# 			response_dict = {'DirectoryName': directory['Name'],
# 			                 'DirectoryId'  : directory['DirectoryId'],
# 			                 'Status'       : directory.get('ShareStatus', 'Owned'),
# 			                 'Type'         : directory['Type'], }
# 			if 'RegionsInfo' in directory:
# 				response_dict.update({'HomeRegion': directory['RegionsInfo'].get('PrimaryRegion', None)})
# 			else:
# 				response_dict.update({'HomeRegion': fRegion})
# 			if 'OwnerDirectoryDescription' in directory:
# 				response_dict.update({'Owner': directory['OwnerDirectoryDescription'].get('AccountId', None)})
# 			else:
# 				response_dict.update({'Owner': faws_acct.acct_number})
# 			directories2.append(response_dict)
# 	else:
# 		for directory in directories:
# 			for searchitem in fSearchStrings:
# 				if searchitem in directory['Name']:
# 					logging.info(f"Found directory {directory['Name']}")
# 					response_dict = {'DirectoryName': directory['Name'],
# 					                 'DirectoryId'  : directory['DirectoryId'],
# 					                 'Status'       : directory.get('ShareStatus', 'Owned'),
# 					                 'Type'         : directory['Type'], }
# 					if 'RegionsInfo' in directory:
# 						response_dict.update({'HomeRegion': directory['RegionsInfo'].get('PrimaryRegion', None)})
# 					else:
# 						response_dict.update({'HomeRegion': fRegion})
# 					if 'OwnerDirectoryDescription' in directory:
# 						response_dict.update({'Owner': directory['OwnerDirectoryDescription'].get('AccountId', None)})
# 					else:
# 						response_dict.update({'Owner': faws_acct.acct_number})
# 					directories2.append(response_dict)
# 	return directories2
#
#
# def find_private_hosted_zones(fProfile, fRegion):
# 	"""
# 	SOON TO BE DEPRECATED
#
# 	This library script returns the hosted zones within an account and a region
# 	"""
# 	import boto3
# 	session_r53 = boto3.Session(profile_name=fProfile, region_name=fRegion)
# 	phz_info = session_r53.client('route53')
# 	hosted_zones = phz_info.list_hosted_zones()
# 	return hosted_zones


def find_private_hosted_zones2(ocredentials, fRegion=None):
	"""
	This library script returns the hosted zones within an account and a region
	"""
	import logging
	import boto3

	if fRegion is None:
		fRegion = 'us-east-1'
	session_r53 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])

	logging.info(f"Finding the private hosted zones within account {ocredentials['AccountId']} and region {fRegion}")
	phz_info = session_r53.client('route53', region_name=fRegion)
	hosted_zones = phz_info.list_hosted_zones()
	return hosted_zones


def find_private_hosted_zones3(faws_acct, fRegion=None):
	"""
	This library script returns the hosted zones within an account and a region
	"""
	import logging

	if fRegion is None:
		fRegion = faws_acct.session.region_name
	logging.info(f"Finding the private hosted zones within account {faws_acct.acct_number} and region {fRegion}")
	session_r53 = faws_acct.session
	# session_r53 = boto3.Session(region_name=fRegion,
	# 							aws_access_key_id=ocredentials['AccessKeyId'],
	# 							aws_secret_access_key=ocredentials['SecretAccessKey'],
	# 							aws_session_token=ocredentials['SessionToken'])
	phz_info = session_r53.client('route53', region_name=fRegion)
	hosted_zones = phz_info.list_hosted_zones()
	return hosted_zones


def find_load_balancers(fProfile, fRegion, fStackFragment='all', fStatus='all'):
	import boto3
	import logging

	logging.info("Profile: %s | Region: %s | Fragment: %s | Status: %s", fProfile, fRegion, fStackFragment, fStatus)
	session_cfn = boto3.Session(profile_name=fProfile, region_name=fRegion)
	lb_info = session_cfn.client('elbv2')
	load_balancers = lb_info.describe_load_balancers()
	load_balancers_Copy = []
	if fStackFragment.lower() == 'all' and (fStatus.lower() == 'active' or fStatus.lower() == 'all'):
		logging.info("Found all the lbs in Profile: %s in Region: %s with Fragment: %s and Status: %s", fProfile,
		             fRegion, fStackFragment, fStatus)
		return load_balancers['LoadBalancers']
	elif fStackFragment.lower() == 'all':
		for load_balancer in load_balancers['LoadBalancers']:
			if fStatus in load_balancer['State']['Code']:
				logging.info("Found lb %s in Profile: %s in Region: %s with Fragment: %s and Status: %s",
				             load_balancers['LoadBalancerName'], fProfile, fRegion, fStackFragment, fStatus)
				load_balancers_Copy.append(load_balancer)
	elif fStatus.lower() == 'active':
		for load_balancer in load_balancers['LoadBalancers']:
			if fStackFragment in load_balancer['LoadBalancerName']:
				logging.info("Found lb %s in Profile: %s in Region: %s with Fragment: %s and Status: %s",
				             load_balancers['LoadBalancerName'], fProfile, fRegion, fStackFragment, fStatus)
				load_balancers_Copy.append(load_balancer)
	return load_balancers_Copy


def find_load_balancers2(credential, fStackFragments=None, fStatus='all'):
	"""
	This library script returns the list of load balancers within an account and a region
	"""
	import logging
	import boto3

	if fStackFragments is None:
		fStackFragments = ['all']
	logging.info(f"Account: {credential['AccountId']} | Profile: {credential['Profile']} | Region: {credential['Region']} | Fragment: {fStackFragments} | Status: {fStatus}")
	session_elb = boto3.Session(region_name=credential['Region'],
	                            aws_access_key_id=credential['AccessKeyId'],
	                            aws_secret_access_key=credential['SecretAccessKey'],
	                            aws_session_token=credential['SessionToken'])
	lb_info = session_elb.client('elbv2', region_name=credential['Region'])
	load_balancers = lb_info.describe_load_balancers()
	load_balancers_Copy = []
	if ('all' in fStackFragments or 'All' in fStackFragments or 'ALL' in fStackFragments) and (fStatus.lower() == 'active' or fStatus.lower() == 'all'):
		logging.info(f"Found all the lbs in Account: {credential['AccountId']} in Region: {credential['Region']} with Fragment: {fStackFragments} and Status: {fStatus}")
		return load_balancers['LoadBalancers']
	elif 'all' in fStackFragments or 'All' in fStackFragments or 'ALL' in fStackFragments:
		for load_balancer in load_balancers['LoadBalancers']:
			if fStatus in load_balancer['State']['Code']:
				logging.info(f"Found lb {load_balancers['LoadBalancerName']} in Account: {credential['AccountId']} in Region: {credential['Region']} with Fragment in {fStackFragments} and Status: {fStatus}")
				load_balancers_Copy.append(load_balancer)
	elif fStatus.lower() == 'active':
		for load_balancer in load_balancers['LoadBalancers']:
			for stack_fragment in fStackFragments:
				if stack_fragment in load_balancer['LoadBalancerName']:
					logging.info(f"Found lb {load_balancers['LoadBalancerName']} in Account: {credential['AccountId']} in Region: {credential['Region']} with Fragment: {stack_fragment} and Status: {fStatus}")
					load_balancers_Copy.append(load_balancer)
	return load_balancers_Copy


def find_load_balancers3(faws_acct, fRegion='us-east-1', fStackFragments=None, fStatus='all'):
	"""
	This library script returns the list of load balancers within an account and a region
	"""
	import logging

	if fStackFragments is None:
		fStackFragments = ['all']
	if faws_acct.Success:
		logging.info(f"Account: {faws_acct.acct_number} | Region: {fRegion} | Fragment: {fStackFragments} | Status: {fStatus}")
		session_cfn = faws_acct.session
		lb_info = session_cfn.client('elbv2', region_name=fRegion)
		load_balancers = lb_info.describe_load_balancers()
		load_balancers_Copy = []
		if ('all' in fStackFragments or 'All' in fStackFragments or 'ALL' in fStackFragments) and (fStatus.lower() == 'active' or fStatus.lower() == 'all'):
			logging.info(
				f"Found all the lbs in Account: {faws_acct.acct_number} in Region: {fRegion} with Fragment: {fStackFragments} and Status: {fStatus}")
			return load_balancers['LoadBalancers']
		elif 'all' in fStackFragments or 'All' in fStackFragments or 'ALL' in fStackFragments:
			for load_balancer in load_balancers['LoadBalancers']:
				if fStatus in load_balancer['State']['Code']:
					logging.info(f"Found lb {load_balancers['LoadBalancerName']} in Account: {faws_acct.acct_number} in Region: {fRegion} with Fragment in {fStackFragments} and Status: {fStatus}")
					load_balancers_Copy.append(load_balancer)
		elif fStatus.lower() == 'active':
			for load_balancer in load_balancers['LoadBalancers']:
				for stack_fragment in fStackFragments:
					if stack_fragment in load_balancer['LoadBalancerName']:
						logging.info(f"Found lb {load_balancers['LoadBalancerName']} in Account: {faws_acct.acct_number} in Region: {fRegion} with Fragment: {stack_fragment} and Status: {fStatus}")
						load_balancers_Copy.append(load_balancer)
		return load_balancers_Copy
	else:
		raise Exception(f"Profile: {faws_acct.Profile} in Region: {faws_acct.Region} didn't authenticate properly. Please check credentials")


def find_stacks(fProfile, fRegion, fStackFragment="all", fStatus="active"):
	"""
	fProfile refers to the name of the profile you're connecting to:
	fRegion refers to  the region you're connecting to
	fStackFragment is a string fragment to match to filter stacks by name
	fStatus is a string describing the status of the stacks you want to find

	There should be (4) use-cases here:
	1. All active stacks, but only the ones that match the fragment sent via parameter.
	2. All active stacks, regardless of name or status. For that - you could supply only the first two parameters
	3. All stacks, regardless of name or status. Only the stacks that match the status you've provided.
		For that - you would provide 'all' as the 3rd parameter and 4th parameter.
	4. Only those stacks that match the string fragment you've sent, and that match the status you've sent.

	Returns a dict that looks like this:
		'StackId':
		'StackName':
		'TemplateDescription':
		'CreationTime': {
			'day':
			'fold':
			'hour':
			'max':
			'microsecond':
			'min':
			'minute':
			'month':
			'resolution':
			'min':
			'tzinfo':
			'year':
		}
		'StackStatus':
		'DriftInformation': {
			'StackDriftStatus': ['NOT_CHECKED']
		}

	"""
	import boto3
	import logging

	logging.info("Profile: %s | Region: %s | Fragment: %s | Status: %s", fProfile, fRegion, fStackFragment, fStatus)
	session_cfn = boto3.Session(profile_name=fProfile, region_name=fRegion)
	client_cfn = session_cfn.client('cloudformation')
	response = client_cfn.describe_stacks()
	AllStacks = response['Stacks']
	logging.info("Found %s stacks this time around", len(response['Stacks']))
	while 'NextToken' in response.keys():
		response = client_cfn.describe_stacks()
		AllStacks.extend(response['Stacks'])
		logging.info("Found %s stacks this time around", len(response['Stacks']))
	logging.info("Done with loops and found a total of %s stacks", len(AllStacks))
	stacksCopy = []
	stacks = dict()
	if fStatus.lower() == 'active' and not fStackFragment.lower() == 'all':
		# Send back stacks that are active, check the fragment further down.
		# stacks = client_cfn.list_stacks(StackStatusFilter=["CREATE_COMPLETE", "DELETE_FAILED", "UPDATE_COMPLETE", "UPDATE_ROLLBACK_COMPLETE", "DELETE_IN_PROGRESS"])
		logging.info("1 - Found %s stacks. Looking for fragment %s", len(AllStacks), fStackFragment)
		for stack in AllStacks:
			if fStackFragment in stack['StackName']:
				# Check the fragment now - only send back those that match
				logging.info("Found stack %s in Profile: %s in Region: %s with Fragment: %s and Status: %s",
				             stack['StackName'], fProfile, fRegion, fStackFragment, fStatus)
				stacksCopy.append(stack)
	elif fStatus.lower() == 'active' and fStackFragment.lower() == 'all':
		# Send back all stacks regardless of fragment, check the status further down.
		# TODO: This section needs paging
		stacks = client_cfn.list_stacks(StackStatusFilter=["CREATE_COMPLETE", "DELETE_FAILED", "UPDATE_COMPLETE",
		                                                   "UPDATE_ROLLBACK_COMPLETE"])
		logging.info("2 - Found ALL %s stacks in 'active' status.", len(stacks['StackSummaries']))
		for stack in stacks['StackSummaries']:
			# if fStatus in stack['StackStatus']:
			# Check the status now - only send back those that match a single status
			# I don't see this happening unless someone wants Stacks in a "Deleted" or "Rollback" type status
			logging.info("Found stack %s in Profile: %s in Region: %s regardless of fragment and Status: %s",
			             stack['StackName'], fProfile, fRegion, fStatus)
			stacksCopy.append(stack)
	elif fStatus.lower() == 'all' and fStackFragment.lower() == 'all':
		# Send back all stacks.
		# TODO: Need paging here
		stacks = client_cfn.list_stacks()
		logging.info("3 - Found ALL %s stacks in ALL statuses", len(stacks['StackSummaries']))
		return stacks['StackSummaries']
	elif not fStatus.lower() == 'active':
		try:
			# TODO: Need paging here
			stacks = client_cfn.list_stacks()
			# TODO: The logic in this script to actually filter on the status is missing.
			# stacks = client_cfn.list_stacks(stackstatusfilter = [''])
			# The valid parameters to use here:
			# StackStatusFilter = [
			#   'CREATE_IN_PROGRESS'
			# | 'CREATE_FAILED'
			# | 'CREATE_COMPLETE'
			# | 'ROLLBACK_IN_PROGRESS'
			# | 'ROLLBACK_FAILED'
			# | 'ROLLBACK_COMPLETE'
			# | 'DELETE_IN_PROGRESS'
			# | 'DELETE_FAILED'
			# | 'DELETE_COMPLETE'
			# | 'UPDATE_IN_PROGRESS'
			# | 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'
			# | 'UPDATE_COMPLETE'
			# | 'UPDATE_ROLLBACK_IN_PROGRESS'
			# | 'UPDATE_ROLLBACK_FAILED'
			# | 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS'
			# | 'UPDATE_ROLLBACK_COMPLETE'
			# | 'REVIEW_IN_PROGRESS'
			# | 'IMPORT_IN_PROGRESS'
			# | 'IMPORT_COMPLETE'
			# | 'IMPORT_ROLLBACK_IN_PROGRESS'
			# | 'IMPORT_ROLLBACK_FAILED'
			# | 'IMPORT_ROLLBACK_COMPLETE', ]
			logging.info("4 - Found %s stacks ", len(stacks['StackSummaries']))
		except Exception as e:
			print(e)
		if 'StackSummaries' in stacks.keys():
			for stack in stacks['StackSummaries']:
				if fStackFragment in stack['StackName']:
					# Check the fragment now - only send back those that match
					logging.info("Found stack %s in Profile: %s in Region: %s with Fragment: %s and Status: %s",
					             stack['StackName'], fProfile, fRegion, fStackFragment, stack['StackStatus'])
					stacksCopy.append(stack)
	return stacksCopy


def find_stacks2(ocredentials: dict, fRegion: str, fStackFragment: list = None, fStatus: list = None):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the AccountId
		- ['Region'] holds the Region

	fRegion is a string
	fStackFragment is a list - default to ["all"]
	fStatus is a string - default to "active"
	"""

	import boto3
	import logging
	from botocore.config import Config

	my_config = Config(
		signature_version='v4',
		retries={
			'max_attempts': 6,
			'mode'        : 'standard'
			}
		)

	if fStatus is None:
		fStatus = ['active']
	logging.info(f"Status looked for is {fStatus}")
	if 'active' in fStatus:
		fStatus = ["CREATE_COMPLETE", "UPDATE_COMPLETE", "UPDATE_ROLLBACK_COMPLETE"]
		desired_status = 'active'
	elif 'all' in fStatus or 'All' in fStatus or 'ALL' in fStatus:
		fStatus = ['CREATE_IN_PROGRESS', 'CREATE_FAILED',
		           'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS',
		           'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE',
		           'DELETE_IN_PROGRESS', 'DELETE_FAILED',
		           'DELETE_COMPLETE', 'UPDATE_IN_PROGRESS',
		           'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
		           'UPDATE_COMPLETE', 'UPDATE_FAILED',
		           'UPDATE_ROLLBACK_IN_PROGRESS',
		           'UPDATE_ROLLBACK_FAILED',
		           'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
		           'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS',
		           'IMPORT_IN_PROGRESS', 'IMPORT_COMPLETE',
		           'IMPORT_ROLLBACK_IN_PROGRESS', 'IMPORT_ROLLBACK_FAILED',
		           'IMPORT_ROLLBACK_COMPLETE']
		desired_status = 'all'
	else:
		desired_status = 'unknown'
	if fStackFragment is None:
		fStackFragment = ['all']
	elif isinstance(fStackFragment, str):
		fStackFragment = [fStackFragment]
	logging.info(f"Acct ID #: {str(ocredentials['AccountNumber'])} | Region:  {fRegion} | Fragment: {fStackFragment} | Status: {fStatus}")
	session_cfn = boto3.Session(region_name=fRegion,
	                            aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'])
	client_cfn = session_cfn.client('cloudformation', config=my_config)
	stacks = dict()
	stacksCopy = []
	allstacks = []
	# For Active Stacks, where we *did* specify a fragment to find
	if desired_status == 'active' and not ('all' in fStackFragment or 'ALL' in fStackFragment or 'All' in fStackFragment):
		# Send back stacks that are active, check the fragment further down.
		stacks = client_cfn.list_stacks(StackStatusFilter=fStatus)
		allstacks.extend(stacks['StackSummaries'])
		while 'NextToken' in stacks.keys():
			stacks = client_cfn.list_stacks(StackStatusFilter=fStatus, NextToken=stacks['NextToken'])
			allstacks.extend(stacks['StackSummaries'])
		for stack in allstacks:
			for fragment in fStackFragment:
				if fragment in stack['StackName']:
					# Check the fragment now - only send back those that match
					logging.info(f"1-Found stack {stack['StackName']} in Account: {ocredentials['AccountNumber']} in "
					             f"Region: {fRegion} with Fragment: {fragment} and Status: {fStatus}")
					stacksCopy.append(stack)
	# For all stacks, where we *did not* specify a fragment to find
	elif 'all' in fStackFragment or 'ALL' in fStackFragment or 'All' in fStackFragment:
		# Send back all stacks.
		# TODO: Need paging here
		stacks = client_cfn.list_stacks(StackStatusFilter=fStatus)
		logging.info(f"Found {len(stacks['StackSummaries'])} stacks in Account: {ocredentials['AccountNumber']} in "
		             f"Region: {fRegion} with status of {fStatus}")
		stacksCopy = stacks['StackSummaries']
	# return stacks['StackSummaries']
	# For all active stacks where we want all stacks
	# TODO: This case will never be triggered, since "all" stacks will be covered by the case above.
	elif ('all' in fStackFragment or 'ALL' in fStackFragment or 'All' in fStackFragment) and desired_status == 'active':
		# Send back all stacks regardless of fragment, check the status further down.
		# TODO: Need paging here
		stacks = client_cfn.list_stacks(StackStatusFilter=fStatus)
		for stack in stacks['StackSummaries']:
			logging.info(f"Found stack {stack['StackName']} in Account: {ocredentials['AccountNumber']} in "
			             f"Region: {fRegion} with Fragment: {fStackFragment} and Status: {fStatus}")
			stacksCopy.append(stack)
	# In case we want *all* stacks, for all stack statuses
	elif desired_status == 'all':
		# Send back all stacks that match the fragment. Default is to only send active, so we have to specify ALL statuses, to get everything.
		stacks = client_cfn.list_stacks(StackStatusFilter=fStatus)
		for stack in stacks['StackSummaries']:

			for fragment in fStackFragment:
				if fragment in stack['StackName']:
					# Check the fragment now - only send back those that match, regardless of status
					logging.info(f"Found stack {stack['StackName']} in Account: {ocredentials['AccountNumber']} in "
					             f"Region: {fRegion} with Fragment: {fragment} and desired status: {desired_status}")
					stacksCopy.append(stack)
	# This is to capture stack statuses that aren't captured above (like specifically "deleted" or something like that)
	elif not desired_status == 'active':
		# Send back stacks that match the single status, check the fragment further down.
		try:
			logging.info(f"Looking for Status: {fStatus}")
			# TODO: Need paging here
			stacks = client_cfn.list_stacks(StackStatusFilter=fStatus)
		except Exception as my_Error:
			logging.error(f"Error: {my_Error}")
		if 'StackSummaries' in stacks.keys():
			for stack in stacks['StackSummaries']:
				for fragment in fStackFragment:
					for status in fStatus:
						if fragment in stack['StackName'] and status == stack['StackStatus']:
							# Check the fragment now - only send back those that match
							logging.info(f"Found stack {stack['StackName']} in Account: {ocredentials['AccountNumber']}"
							             f" in Region: {fRegion} with Fragment: {fragment} and Status: {fStatus}")
							stacksCopy.append(stack)
	for _ in stacksCopy:
		_['Region'] = fRegion
		_['AccountNumber'] = ocredentials['AccountNumber']
		_['MgmtAccount'] = ocredentials['MgmtAccount']
	return stacksCopy


def find_stacks3(faws_acct, fRegion: str, fStackFragment: list = None):
	"""
	fProfile refers to the name of the profile you're connecting to:
	fRegion refers to the region you're connecting to
	fStackFragment is a string fragment to match to filter stacks by name

	Returns a dict that looks like this:
		'StackId':
		'StackName':
		'TemplateDescription':
		'CreationTime': {
			'day':
			'fold':
			'hour':
			'max':
			'microsecond':
			'min':
			'minute':
			'month':
			'resolution':
			'min':
			'tzinfo':
			'year':
		}
		'StackStatus':
		'DriftInformation': {
			'StackDriftStatus': ['NOT_CHECKED']
		}

	"""
	import logging
	from botocore.config import Config

	my_config = Config(
		signature_version='v4',
		retries={
			'max_attempts': 6,
			'mode'        : 'standard'
			}
		)

	logging.info(f"Account Number: {faws_acct.acct_number} | Region: {fRegion} | Fragment: {fStackFragment}")
	client_cfn = faws_acct.session.client('cloudformation', config=my_config, region_name=fRegion)
	if fStackFragment is None:
		fStackFragment = ['all']
	elif isinstance(fStackFragment, str):
		fStackFragment = [fStackFragment]
	response = client_cfn.describe_stacks()
	AllStacks = response['Stacks']
	logging.info(f"Found {len(response['Stacks'])} stacks this time around")
	while 'NextToken' in response.keys():
		response = client_cfn.describe_stacks(NextToken=response['NextToken'])
		AllStacks.extend(response['Stacks'])
		logging.info(f"Found {len(response['Stacks'])} more stacks this time around")
	logging.info(f"Done with loops and found a total of {len(AllStacks)} stacks")
	AllStacks2 = []
	TheyWantEverything = 'all' in fStackFragment or 'ALL' in fStackFragment or 'All' in fStackFragment

	if TheyWantEverything:
		logging.info(f"All stacks requested - so all stacks being returned...")
		return AllStacks
	else:
		logging.info(f"Found {len(AllStacks)} stacks. Looking for fragment {fStackFragment}")
		for stack in AllStacks:
			# Check the fragment now - only send back those that match
			for fragment in fStackFragment:
				if stack['StackName'].find(fragment) > -1:
					logging.info(f"Found stack {stack['StackName']} in Account: {faws_acct.acct_number} in Region: {fRegion} with Fragment: {fragment}")
					AllStacks2.append(stack)
		return AllStacks2


def delete_stack(fprofile, fRegion, fStackName, **kwargs):
	"""
	fprofile is a string holding the name of the profile you're connecting to:
	fRegion is a string
	fStackName is a string
	RetainResources should be a boolean
	ResourcesToRetain should be a list
	"""
	import boto3
	import logging
	RetainResources = False
	ResourcesToRetain = []
	if "RetainResources" in kwargs:
		RetainResources = True
		ResourcesToRetain = kwargs['ResourcesToRetain']
	session_cfn = boto3.Session(profile_name=fprofile, region_name=fRegion)
	client_cfn = session_cfn.client('cloudformation')
	if RetainResources:
		logging.info("Profile: %s | Region: %s | StackName: %s", fprofile, fRegion, fStackName)
		logging.info("	Retaining Resources: %s", ResourcesToRetain)
		response = client_cfn.delete_stack(StackName=fStackName, RetainResources=ResourcesToRetain)
	else:
		logging.info("Profile: %s | Region: %s | StackName: %s", fprofile, fRegion, fStackName)
		response = client_cfn.delete_stack(StackName=fStackName)
	return response


def delete_stack2(ocredentials, fRegion, fStackName, **kwargs):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['AccountNumber'] holds the AccountId
		- ['Region'] holds the Region string
	fRegion is a string
	fStackName is a string
	RetainResources should be a boolean
	ResourcesToRetain should be a list
	"""
	import boto3
	import logging
	RetainResources = False
	ResourcesToRetain = []
	if "RetainResources" in kwargs:
		RetainResources = True
		ResourcesToRetain = kwargs['ResourcesToRetain']
	session_cfn = boto3.Session(region_name=fRegion,
	                            aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'])
	client_cfn = session_cfn.client('cloudformation')
	if RetainResources:
		logging.info("Account: %s | Region: %s | StackName: %s", ocredentials['AccountNumber'], fRegion, fStackName)
		logging.info("	Retaining Resources: %s", ResourcesToRetain)
		response = client_cfn.delete_stack(StackName=fStackName, RetainResources=ResourcesToRetain)
	else:
		logging.info("Account: %s | Region: %s | StackName: %s",
		             ocredentials['AccountNumber'],
		             fRegion,
		             fStackName)
		response = client_cfn.delete_stack(StackName=fStackName)
	return response


def find_stacks_in_acct3(faws_acct, fRegion, fStackFragment="all", fStatus="active"):
	"""
	faws_acct is an object of the aws_acct class:
	fRegion is a string
	fStackFragment is a string - default to "all"
	fStatus is a string - default to "active"

	4 scenarios here:
	1 - fragment string provided, and looking for "active" stacks
	2 - fragment either isn't provided, or they provided the string "all" and they're looking for active stacks
	4 - fragment either isn't provided, or they provided the string "all" and they're looking for ALL stacks (even deleted)
	3 - Send back all stacks (deleted too), regardless of fragment
	5 - Regardless of the fragment, they're looking for other than "active" stacks (which could still mean 'all')
	"""

	import logging

	logging.error(
		f"Acct ID #: {faws_acct.acct_number} | Region: {fRegion} | Fragment: {fStackFragment} | Status: {fStatus}")
	client_cfn = faws_acct.session.client('cloudformation')
	stacks = dict()
	stacksCopy = []
	StackStatusFilter_all = ['CREATE_IN_PROGRESS', 'CREATE_FAILED',
	                         'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS',
	                         'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE',
	                         'DELETE_IN_PROGRESS', 'DELETE_FAILED',
	                         'DELETE_COMPLETE', 'UPDATE_IN_PROGRESS',
	                         'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
	                         'UPDATE_COMPLETE', 'UPDATE_FAILED',
	                         'UPDATE_ROLLBACK_IN_PROGRESS',
	                         'UPDATE_ROLLBACK_FAILED',
	                         'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
	                         'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS',
	                         'IMPORT_IN_PROGRESS', 'IMPORT_COMPLETE',
	                         'IMPORT_ROLLBACK_IN_PROGRESS', 'IMPORT_ROLLBACK_FAILED',
	                         'IMPORT_ROLLBACK_COMPLETE']
	StackStatusFilter_active = ["CREATE_COMPLETE", "UPDATE_COMPLETE",
	                            "UPDATE_ROLLBACK_COMPLETE"]
	if fStatus.lower() == 'active' and not fStackFragment.lower() == 'all':
		# Send back stacks that are active, check the fragment further down.
		stacks = client_cfn.list_stacks(StackStatusFilter=StackStatusFilter_active)
		for stack in stacks['StackSummaries']:
			if fStackFragment in stack['StackName']:
				# Check the fragment now - only send back those that match
				logging.info(f"1-Found stack {stack['StackName']} in Account: {faws_acct.acct_number} in "
				             f"Region: {fRegion} with Fragment: {fStackFragment} and Status: {fStatus}")
				stacksCopy.append(stack)
	elif fStatus.lower() == 'active' and fStackFragment.lower() == 'all':
		# Send back all stacks regardless of fragment, check the status further down.
		# TODO: Need paging here
		stacks = client_cfn.list_stacks(StackStatusFilter=StackStatusFilter_active)
		for stack in stacks['StackSummaries']:
			logging.info(f"2-Found stack {stack['StackName']} in Account: {faws_acct.acct_number} in "
			             f"Region: {fRegion} with Fragment: {fStackFragment} and Status: {fStatus}")
			stacksCopy.append(stack)
	elif fStatus.lower() == 'all' and fStackFragment.lower() == 'all':
		# Send back all stacks.
		# TODO: Need paging here
		stacks = client_cfn.list_stacks(StackStatusFilter=StackStatusFilter_all)
		logging.info(f"4-Found {len(stacks)} stacks in Account: {faws_acct.acct_number} in "
		             f"Region: {fRegion}")
		return stacks['StackSummaries']
	elif fStatus.lower() == 'all':
		# Send back all stacks that match the fragment, including all statuses
		stacks = client_cfn.list_stacks(StackStatusFilter=StackStatusFilter_all)
		for stack in stacks['StackSummaries']:
			if fStackFragment in stack['StackName']:
				# Check the fragment now - only send back those that match, regardless of status
				logging.info(f"3-Found stack {stack['StackName']} in Account: {faws_acct.acct_number} in "
				             f"Region: {fRegion} with Fragment: {fStackFragment} and Status: {fStatus}")
				stacksCopy.append(stack)
	elif not fStatus.lower() == 'active':
		# Send back stacks that match the single status, check the fragment further down.
		try:
			logging.info(f"Looking for Status: {fStatus}")
			# TODO: Need paging here
			stacks = client_cfn.list_stacks(StackStatusFilter=[fStatus])
		except Exception as my_Error:
			logging.error(my_Error)
		if 'StackSummaries' in stacks.keys():
			for stack in stacks['StackSummaries']:
				if fStackFragment in stack['StackName'] and fStatus in stack['StackStatus']:
					# Check the fragment now - only send back those that match
					logging.info(f"5-Found stack {stack['StackName']} in Account: {faws_acct.acct_number}"
					             f" in Region: {fRegion} with Fragment: {fStackFragment} and Status: {fStatus}")
					stacksCopy.append(stack)
	return stacksCopy


def find_saml_components_in_acct2(ocredentials):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the region
		- ['AccountNumber'] holds the AccountId
	"""
	import boto3
	import logging
	logging.info(f"Acct ID #: {str(ocredentials['AccountNumber'])} | Region: {ocredentials['Region']}")
	session_aws = boto3.Session(region_name=ocredentials['Region'],
	                            aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'])
	iam_info = session_aws.client('iam')
	saml_providers = iam_info.list_saml_providers()['SAMLProviderList']
	return saml_providers


def find_stacksets2(ocredentials: dict, fRegion: str = 'us-east-1', fStackFragments: list = None, fStatus: str = None):
	"""
	credentials is a dictionary containing the credentials for a given account
	fRegion is a string
	fStackFragment is a list

	Returns a list that looks like this:
	[
	{'DriftStatus': 'NOT_CHECKED',
	 'StackSetId': 'AWS-Landing-Zone-GuardDutyMaster:48ce0116-2d67-45e2-9141-6c0bfd555363',
	 'StackSetName': 'AWS-Landing-Zone-GuardDutyMaster',
	 'Status': 'ACTIVE'
	},
	{'DriftStatus': 'NOT_CHECKED',
	 'StackSetId': 'AWS-Landing-Zone-GuardDutyMaster:48ce0116-2d67-45e2-9141-6c0bfd555363',
	 'StackSetName': 'AWS-Landing-Zone-GuardDutyMaster',
	 'Status': 'ACTIVE'
	},
	]
	"""
	import boto3
	import logging

	logging.info(f"Account ID: {ocredentials['AccountId']} | Region: {ocredentials['Region']} | Fragment: {fStackFragments} | Status: {fStatus}")
	session_aws = boto3.Session(region_name=ocredentials['Region'],
	                            aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'])
	client_cfn = session_aws.client('cloudformation')
	logging.info(f'Creds: {ocredentials}')
	if fStatus is None:
		fStatus = 'Active'
	if fStackFragments is None:
		fStackFragments = ['all']
	stacksets2 = []
	try:
		logging.info(f"Looking for stack sets in account {ocredentials['AccountId']} matching fragment {fStackFragments} with status {fStatus}")
		stacksets = client_cfn.list_stack_sets(Status=fStatus.upper())
		stacksets2.extend(stacksets['Summaries'])
		while 'NextToken' in stacksets.keys():
			stacksets = client_cfn.list_stack_sets(Status=fStatus.upper())
			stacksets2.extend(stacksets['Summaries'])
	except Exception as my_Error:
		logging.error(f"fstatus is {fStatus}")
		logging.error(f"A list of stacksets wasn't captured")
		print("We shouldn't get to this point")
		error_message = my_Error
		logging.error(f"Error: {error_message}")
	if ('all' in fStackFragments or 'ALL' in fStackFragments or 'All' in fStackFragments) and len(stacksets2) > 0:
		logging.info(f"Found all the stacksets in Account: {ocredentials['AccountNumber']} in Region: {ocredentials['Region']}")
		return stacksets2
	else:
		stacksetsCopy = []
		for stack in stacksets2:
			for stackfrag in fStackFragments:
				if stackfrag in stack['StackSetName']:
					logging.info(f"Found stackset {stack['StackSetName']} in account: {ocredentials['AccountId']} in Region: {ocredentials['Region']} with Fragment: {stackfrag}")
					stacksetsCopy.append(stack)
	return stacksetsCopy


def find_stacksets3(faws_acct, fRegion: str = None, fStackFragmentList: list = None, fExact: bool = False, fGetHealth: bool = False) -> dict:
	"""
	Description: returns a dict object with the list of stacksets if successful.
	faws_acct is a class containing the account information
	fRegion is a string
	fStackFragment is a list of strings
	fExact is a boolean to determine whether the fragment should represent the full name or just a fragment
	fGetHealth is a flag to determine whether we get additional health information for the stackset

	"""
	# import logging
	from time import time
	from botocore.exceptions import EndpointConnectionError, ClientError
	from botocore.config import Config

	begin_time = time()
	my_config = Config(
		signature_version='v4',
		retries={
			'max_attempts': 6,
			'mode'        : 'standard'
			}
		)
	MaxWorkerThreads = 8

	def get_stackset_attributes(fStackSetsCopy: dict):
		"""
		Description: To get the last operation's health status for the stackset
		@param fStackSetsCopy: The name of the stackset
		@return: An updated dictionary with the health status of each stackset updated
		"""
		from threading import Thread
		from queue import Queue
		from datetime import datetime
		from tqdm.auto import tqdm

		class GetStackSetStatus(Thread):

			def __init__(self, queue):
				Thread.__init__(self)
				self.queue = queue

			def run(self):
				while True:
					# Get the work from the queue and expand the tuple
					c_stackset, c_region, c_PlaceCount = self.queue.get()
					logging.info(f"De-queued info for stack set name {c_stackset['StackSetName']}")
					try:
						client_cfn = faws_acct.session.client('cloudformation', config=my_config)
						all_stack_set_operations = []
						stack_set_operations = client_cfn.list_stack_set_operations(StackSetName=c_stackset['StackSetName'])
						all_stack_set_operations.extend(stack_set_operations['Summaries'])
						# It's unclear if this operation returns sorted data, so we need to get ALL records,
						# so that we can always be certain on getting the most recent operation
						if 'NextToken' in stack_set_operations.keys():
							while 'NextToken' in stack_set_operations.keys():
								stack_set_operations = client_cfn.list_stack_set_operations(StackSetName=c_stackset['StackSetName'],
								                                                            NextToken=stack_set_operations['NextToken'])
								all_stack_set_operations.extend(stack_set_operations['Summaries'])
						all_stack_instances = []
						number_of_stack_instances_dict = client_cfn.list_stack_instances(StackSetName=c_stackset['StackSetName'])
						all_stack_instances.extend(number_of_stack_instances_dict['Summaries'])
						if 'NextToken' in number_of_stack_instances_dict.keys():
							while 'NextToken' in number_of_stack_instances_dict.keys():
								number_of_stack_instances_dict = client_cfn.list_stack_set_operations(StackSetName=c_stackset['StackSetName'],
								                                                                      NextToken=number_of_stack_instances_dict['NextToken'])
								all_stack_instances.extend(number_of_stack_instances_dict['Summaries'])

						sorted_operations = sorted(all_stack_set_operations, key=lambda d: (d['Status'], d.get('EndTimestamp', datetime.now())), reverse=True)
						logging.info(f"Found {len(all_stack_set_operations)} operations within the StackSet {c_stackset['StackSetName']}")
						if len(sorted_operations) == 0:
							operation_action = operation_status = operation_reason = operation_id = 'Never Run'
							# TODO: Replace this random date/time with something more interesting.
							operation_end_timestamp = float(1707926400.668982)
						else:
							operation_action = sorted_operations[0]['Action']
							operation_status = sorted_operations[0]['Status']
							operation_reason = sorted_operations[0]['StatusDetails']
							operation_id = sorted_operations[0]['OperationId']
							operation_end_timestamp = sorted_operations[0]['EndTimestamp']
						c_stackset.update({'Action'     : operation_action, 'Status': operation_status,
						                   'Reason'     : operation_reason, 'EndTimestamp': operation_end_timestamp,
						                   'OperationId': operation_id, 'Stack_Instances_number': len(all_stack_instances)})
					except ClientError as my_Error:
						logging.error(f"Error: Likely throttling errors from too much activity")
						logging.info(f"Actual Error: {my_Error}")
						logging.debug(f"Operations name: {my_Error.operation_name} | Response: {my_Error.response} | MSG TEMPLATE: {my_Error.MSG_TEMPLATE}")
						continue
					finally:
						pbar.update()
						self.queue.task_done()

		###########

		checkqueue = Queue()

		PlaceCount = 0
		WorkerThreads = min(len(fStackSetsCopy), MaxWorkerThreads)
		logging.info(f"Using {WorkerThreads} threads")

		pbar = tqdm(desc=f'Finding all Stacksets from {len(fStackSetsCopy)} stacksets',
		            total=len(fStackSetsCopy), unit=' stacksets'
		            )

		for x in range(WorkerThreads):
			worker = GetStackSetStatus(checkqueue)
			# Setting daemon to True will let the main thread exit even though the workers are blocking
			worker.daemon = True
			worker.start()

		for stackset in fStackSetsCopy:
			logging.debug(f"Beginning to queue data - starting with {stackset['StackSetName']}")
			try:
				# I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
				PlaceCount += 1
				# print(".", end='')
				checkqueue.put((stackset, fRegion, PlaceCount))
			except ClientError as my_Error:
				if "AuthFailure" in str(my_Error):
					logging.error(f"Authorization Failure accessing stack set {stackset['StackSetName']} in {fRegion} region")
					logging.warning(f"It's possible that the region {fRegion} hasn't been opted-into")
					pass
		checkqueue.join()
		logging.info(f"Getting the stackset operation data took {time() - begin_time:.2f} seconds")
		pbar.close()
		return fStackSetsCopy

	# Logging Settings
	# LOGGER = logging.getLogger()
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)
	# Set Log Level

	if fStackFragmentList is None:
		fStackFragmentList = ['all']
	if fRegion is None:
		fRegion = 'us-east-1'
	if isinstance(fStackFragmentList, str):
		fStackFragmentList = [fStackFragmentList]
	result = validate_region3(faws_acct, fRegion)
	if not result['Success']:  # Region failed to validate
		return result
	else:  # Region was validated
		logging.info(result['Message'])
	logging.info(f"Account: {faws_acct.acct_number} | Region: {fRegion} | Fragment: {fStackFragmentList}")
	client_cfn = faws_acct.session.client('cloudformation', region_name=fRegion, config=my_config)

	try:
		stacksets_prelim = client_cfn.list_stack_sets(Status='ACTIVE')
	# TODO: Need more error-handling here to handle different types of failures
	except EndpointConnectionError as myError:
		logging.info(f"Likely that the region passed in wasn't correct. Please check and try again: {myError}")
		return_response = {'Success': False, 'ErrorMessage': "Region Endpoint Failure"}
		return return_response
	stacksets = stacksets_prelim['Summaries']
	while 'NextToken' in stacksets_prelim.keys():  # Get all instance names
		stacksets_prelim = client_cfn.list_stack_sets(Status='ACTIVE', NextToken=stacksets_prelim['NextToken'])
		stacksets.extend(stacksets_prelim['Summaries'])

	stacksetsCopy = []
	# Because fStackFragment is a list, I need to write it this way
	if 'all' in fStackFragmentList or 'ALL' in fStackFragmentList or 'All' in fStackFragmentList:
		logging.info(f"Found all the stacksets in account: {faws_acct.acct_number} in Region: {fRegion} with Fragment: {fStackFragmentList}")
		stacksetsCopy = stacksets
	else:
		for stack in stacksets:
			for fragment in fStackFragmentList:
				if fExact:
					if fragment == stack['StackSetName']:
						stacksetsCopy.append(stack)
						logging.info(
							f"Found stackset {stack['StackSetName']} in Account: {faws_acct.acct_number} in Region: {fRegion} with Fragment: {fragment}")
				elif fragment in stack['StackSetName']:
					stacksetsCopy.append(stack)
					logging.info(
						f"Found stackset {stack['StackSetName']} in Account: {faws_acct.acct_number} in Region: {fRegion} with Fragment: {fragment}")
	stacksets_dict = {}
	if fGetHealth:
		updated_stacksets = get_stackset_attributes(stacksetsCopy)
	else:
		updated_stacksets = stacksetsCopy
	for stackset_name in updated_stacksets:
		stacksets_dict[stackset_name['StackSetName']] = stackset_name
	return_response = {'Success': True, 'StackSets': stacksets_dict}
	return return_response


def delete_stackset(fProfile, fRegion, fStackSetName):
	"""
	fProfile is a string holding the name of the profile you're connecting to:
	fRegion is a string
	fStackSetName is a string
	"""
	import boto3
	import logging

	session_cfn = boto3.Session(profile_name=fProfile, region_name=fRegion)
	client_cfn = session_cfn.client('cloudformation')
	logging.info(f"Profile: {fProfile} | Region: {fRegion} | StackSetName: {fStackSetName}")
	response = client_cfn.delete_stack_set(StackSetName=fStackSetName)
	return response


def delete_stackset3(faws_acct, fRegion, fStackSetName):
	"""
	faws_acct is an object representing the account we're working in
	fRegion is a string
	fStackSetName is a string
	"""
	import logging

	client_cfn = faws_acct.session.client('cloudformation')
	logging.info(f"Acct Number: {faws_acct.acct_number} | Region: {fRegion} | StackSetName: {fStackSetName}")
	return_response = {'Success': False}
	try:
		response = client_cfn.delete_stack_set(StackSetName=fStackSetName, CallAs='SELF')
		return_response['Success'] = True
	except client_cfn.exceptions.StackSetNotEmptyException as myError:
		logging.error(f"StackSet not empty: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except client_cfn.exceptions.OperationInProgressException as myError:
		logging.error(f"Operation in progress: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	except Exception as myError:
		logging.error(f"Other Error: {myError}")
		return_response['Success'] = False
		return_response['ErrorMessage'] = myError
	return return_response


def find_stack_instances(fProfile, fRegion, fStackSetName, fStatus='CURRENT'):
	"""
	fProfile is a string
	fRegion is a string
	fStackSetName is a string
	fStatus is a string, but isn't currently used.
	TODO: Decide whether to use fStatus, or not
	"""
	import boto3
	import logging

	logging.info("Profile: %s | Region: %s | StackSetName: %s", fProfile, fRegion, fStackSetName)
	session_cfn = boto3.Session(profile_name=fProfile, region_name=fRegion)
	client_cfn = session_cfn.client('cloudformation')
	stack_instances = client_cfn.list_stack_instances(StackSetName=fStackSetName)
	stack_instances_list = stack_instances['Summaries']
	while 'NextToken' in stack_instances.keys():  # Get all instance names
		stack_instances = client_cfn.list_stack_instances(StackSetName=fStackSetName,
		                                                  NextToken=stack_instances['NextToken'])
		stack_instances_list.extend(stack_instances['Summaries'])
	return stack_instances_list


def find_stack_instances2(ocredentials, fRegion, fStackSetName, fStatus='CURRENT'):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the Region where the authentication was done
		- ['AccountNumber'] holds the AccountId
	fRegion is a string
	fStackSetName is a string
	fStatus is a string, but isn't currently used.
	TODO: Decide whether to use fStatus, or not
	"""
	import boto3
	import logging
	logging.info(f"Acct ID #: {str(ocredentials['AccountNumber'])} | Region: {fRegion}")
	session_aws = boto3.Session(region_name=fRegion,
	                            aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'])
	client_cfn = session_aws.client('cloudformation')
	stack_instances = client_cfn.list_stack_instances(StackSetName=fStackSetName)
	stack_instances_list = stack_instances['Summaries']
	while 'NextToken' in stack_instances.keys():  # Get all instance names
		stack_instances = client_cfn.list_stack_instances(StackSetName=fStackSetName,
		                                                  NextToken=stack_instances['NextToken'])
		stack_instances_list.extend(stack_instances['Summaries'])
	return stack_instances_list


def find_stack_instances3(faws_acct, fRegion: str, fStackSetName: str, fStatus: str = 'CURRENT', faccountlist: list = None, fregionlist: list = None):
	"""
	faws_acct is a custom class containing the credentials
	fRegion is a string
	fStackSetName is a string
	fStatus is a string, but isn't currently used.
	faccountlist is a list of accounts that we may filter on
	TODO: Decide whether to use fStatus, or not
	"""
	import logging
	from botocore.config import Config
	from botocore.exceptions import ClientError

	config = Config(
		retries={
			'max_attempts': 6,
			'mode'        : 'standard'
			}
		)
	logging.info(f"Account: {faws_acct.acct_number} | Region: {fRegion} | StackSetName: {fStackSetName} | account list: {faccountlist}")
	client_cfn = faws_acct.session.client('cloudformation', region_name=fRegion, config=config)
	stack_instances = dict()
	stack_instances_list = list()
	try:
		stack_instances = client_cfn.list_stack_instances(StackSetName=fStackSetName)
		if faccountlist is None and fregionlist is None:
			stack_instances_list.extend(stack_instances['Summaries'])
		elif fregionlist is None:
			for stack_instance in stack_instances['Summaries']:
				if stack_instance['Account'] in faccountlist:
					stack_instances_list.append(stack_instance)
		elif faccountlist is None:
			for stack_instance in stack_instances['Summaries']:
				if stack_instance['Region'] in fregionlist:
					stack_instances_list.append(stack_instance)
		else:
			for stack_instance in stack_instances['Summaries']:
				if stack_instance['Region'] in fregionlist and stack_instance['Account'] in faccountlist:
					stack_instances_list.append(stack_instance)
		logging.debug(f"Found {len(stack_instances_list)} instances in {fStackSetName}")
	except ClientError as myError:
		logging.debug(f"Debug Error: {myError}")
		if myError.response['Error']['Code'] == 'LimitExceededException':
			logging.warning('API call limit exceeded; backing off and retrying...')
		else:
			raise myError
	while 'NextToken' in stack_instances.keys():  # Get all instance names
		try:
			stack_instances = client_cfn.list_stack_instances(StackSetName=fStackSetName,
			                                                  NextToken=stack_instances['NextToken'])
			if faccountlist is None and fregionlist is None:
				stack_instances_list.extend(stack_instances['Summaries'])
			elif fregionlist is None:
				for stack_instance in stack_instances['Summaries']:
					if stack_instance['Account'] in faccountlist:
						stack_instances_list.append(stack_instance)
			elif faccountlist is None:
				for stack_instance in stack_instances['Summaries']:
					if stack_instance['Region'] in fregionlist:
						stack_instances_list.append(stack_instance)
			else:
				for stack_instance in stack_instances['Summaries']:
					if stack_instance['Region'] in fregionlist and stack_instance['Account'] in faccountlist:
						stack_instances_list.append(stack_instance)
		except ClientError as myError:
			logging.debug(f"Debug Error: {myError}")
			if myError.response['Error']['Code'] == 'LimitExceededException':
				logging.warning('API call limit exceeded; backing off and retrying...')
			else:
				raise myError
	return stack_instances_list


def delete_stack_instances(fProfile, fRegion, lAccounts, lRegions, fStackSetName, fRetainStacks=False,
                           fOperationName="StackDelete"):
	"""
	fProfile is the Root Profile that owns the stackset
	fRegion is the region where the stackset resides
	lAccounts is a list of accounts
	lRegion is a list of regions
	fStackSetName is a string
	fOperationName is a string (to identify the operation)
	"""
	import boto3
	import logging

	logging.info(f"Deleting {fStackSetName} stackset over {len(lAccounts)} accounts across {len(lRegions)} regions")
	session_cfn = boto3.Session(profile_name=fProfile, region_name=fRegion)
	client_cfn = session_cfn.client('cloudformation')
	response = client_cfn.delete_stack_instances(StackSetName=fStackSetName, Accounts=lAccounts, Regions=lRegions,
	                                             RetainStacks=fRetainStacks, OperationId=fOperationName)
	return response  # There is no response to send back


def delete_stack_instances3(faws_acct, fRegion, lRegions, fStackSetName, fRetainStacks=False,
                            fOperationName=None, lAccounts=None, fPermissionModel='SELF_MANAGED', fDeploymentTarget=None):
	"""
	faws_acct is the Root account class object that owns the stackset (This function doesn't yet support Delegated Admin permissions)
	fRegion is the region where the stackset resides
	lAccounts is a list of accounts
	lRegion is a list of regions
	fStackSetName is a string
	fRetainStacks is a boolean
	fOperationName is a string (to identify the operation)
	lAccounts should be a list of accounts
	fPermissionModel is either "SELF_MANAGED" or "SERVICE_MANAGED"
	fDeploymentTarget is the Organizational Unit (or root) for the stackset to be associated to
	"""
	import logging
	from random import choices
	from string import ascii_letters
	from botocore.exceptions import ValidationError

	result = validate_region3(faws_acct, fRegion)
	response = {'Success': True, 'ErrorMessage': None, 'OperationId': None}
	errormessage = "Error hasn't been initialized yet"
	return_response = {'Success': False, 'ErrorMessage': errormessage}
	if not result['Success']:
		return result['Message']
	else:
		logging.info(result['Message'])
	if fOperationName is None:
		fOperationName = f"StackDelete-{choices(ascii_letters, k=6)}"
	logging.info(f"Deleting {fStackSetName} stackset over {len(lAccounts)} accounts across {len(lRegions)} regions")
	client_cfn = faws_acct.session.client('cloudformation', region_name=fRegion)
	# The following code is only valid for "Self-Managed StackSets"
	try:
		if fPermissionModel == 'SELF_MANAGED':
			response.update(client_cfn.delete_stack_instances(StackSetName=fStackSetName,
			                                                  Accounts=lAccounts,
			                                                  Regions=lRegions,
			                                                  RetainStacks=fRetainStacks,
			                                                  OperationPreferences={
				                                                  'RegionConcurrencyType'     : 'PARALLEL',
				                                                  'FailureTolerancePercentage': 0,
				                                                  'MaxConcurrentPercentage'   : 100
				                                                  },
			                                                  OperationId=fOperationName))

			return_response = {'Success': True, 'OperationId': response['OperationId']}
		elif fPermissionModel == 'SERVICE_MANAGED':
			response.update(client_cfn.delete_stack_instances(StackSetName=fStackSetName,
			                                                  DeploymentTargets=fDeploymentTarget,
			                                                  Regions=lRegions,
			                                                  RetainStacks=fRetainStacks,
			                                                  OperationPreferences={
				                                                  'RegionConcurrencyType'     : 'PARALLEL',
				                                                  'FailureTolerancePercentage': 0,
				                                                  'MaxConcurrentPercentage'   : 100
				                                                  },
			                                                  OperationId=fOperationName))
			return_response = {'Success': True, 'OperationId': response['OperationId']}
	except client_cfn.exceptions.StackSetNotFoundException as myError:
		errormessage = f"StackSet not found: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	except client_cfn.exceptions.OperationInProgressException as myError:
		errormessage = f"Operation in progress: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	except client_cfn.exceptions.OperationIdAlreadyExistsException as myError:
		errormessage = f"Operation Id already exists: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	except client_cfn.exceptions.StaleRequestException as myError:
		errormessage = f"Stale Request: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	except client_cfn.exceptions.InvalidOperationException as myError:
		errormessage = f"Invalid Operation: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	except ValidationError as myError:
		errormessage = f"Validation Error: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	except Exception as myError:
		errormessage = f"Other problem: {myError}"
		logging.error(errormessage)
		return_response = {'Success': False, 'ErrorMessage': errormessage}
	return return_response  # The response will be the Operation ID of the delete operation or an Error Message


def check_stack_set_status3(faws_acct, fStack_set_name, fOperationId=None):
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
		# or there were no stack instances to be deleted,
		# so we need to check the status of the stack-set creation, and not the operations that happen to the stackset
		try:
			response = client_cfn.describe_stack_set(StackSetName=fStack_set_name,
			                                         CallAs='SELF')['StackSet']
			return_response['StackSetStatus'] = response['Status']
			return_response['Success'] = True
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


def find_if_stack_set_exists3(faws_acct, fStack_set_name):
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


def find_sc_products(fProfile, fRegion, fStatus="ERROR", flimit=100):
	"""
	fProfile is the Root Profile that owns the Account we're interrogating
	fRegion is the region we're interrogating
	fStatus is the status of SC products we're looking for. Defaults to "ERROR"
	flimit is the max number of products to find. This is used for debugging, mainly

	Returned list looks like this:
	[
		{
			"Arn": "string",
			"CreatedTime": number,
			"Id": "string",
			"IdempotencyToken": "string",
			"LastRecordId": "string",
			"Name": "string",
			"PhysicalId": "string",
			"ProductId": "string",
			"ProvisioningArtifactId": "string",
			"Status": "string",
			"StatusMessage": "string",
			"Tags": [
				{
					"Key": "string",
					"Value": "string"
				}
			],
			"Type": "string",
			"UserArn": "string",
			"UserArnSession": "string"
		}
	]
	"""
	import boto3

	response2 = []
	session_sc = boto3.Session(profile_name=fProfile, region_name=fRegion)
	client_sc = session_sc.client('servicecatalog')
	if fStatus.lower() == 'all':
		response = client_sc.search_provisioned_products(PageSize=flimit)
		while 'NextPageToken' in response.keys():
			response2.extend(response['ProvisionedProducts'])
			response = client_sc.search_provisioned_products(PageToken=response['NextPageToken'], PageSize=flimit)
	else:  # We filter down to only the statuses asked for
		response = client_sc.search_provisioned_products(PageSize=flimit, Filters={
			'SearchQuery': [f"status:{fStatus}"]})
		while 'NextPageToken' in response.keys():
			response2.extend(response['ProvisionedProducts'])
			response = client_sc.search_provisioned_products(PageSize=flimit, Filters={
				'SearchQuery': [f"status:{fStatus}"]}, PageToken=response['NextPageToken'])
	response2.extend(response['ProvisionedProducts'])
	return response2


def find_sc_products3(faws_acct, fStatus="ERROR", flimit=100, fproductId=None):
	"""
	faws_acct is the Org account that we're interrogating
	fStatus is the status of SC products we're looking for. Defaults to "ERROR"
	flimit is the max number of products to find. This is used for debugging, mainly
	fproductId is the provisioned product ID that we can filter on to narrow down our search

	Returned list looks like this:
	[
		{
			"Arn": "string",
			"CreatedTime": number,
			"Id": "string",
			"IdempotencyToken": "string",
			"LastRecordId": "string",
			"Name": "string",
			"PhysicalId": "string",
			"ProductId": "string",
			"ProvisioningArtifactId": "string",
			"Status": "string",
			"StatusMessage": "string",
			"Tags": [
				{
					"Key": "string",
					"Value": "string"
				}
			],
			"Type": "string",
			"UserArn": "string",
			"UserArnSession": "string"
		}
	]
	"""

	response2 = []
	client_sc = faws_acct.session.client('servicecatalog')
	if fStatus.lower() == 'all' and fproductId is None:
		response = client_sc.search_provisioned_products(PageSize=flimit,
		                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'})
		while 'NextPageToken' in response.keys():
			response2.extend(response['ProvisionedProducts'])
			response = client_sc.search_provisioned_products(PageToken=response['NextPageToken'],
			                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
			                                                 PageSize=flimit)
	elif fStatus.lower() == 'all' and fproductId is not None:
		response = client_sc.search_provisioned_products(PageSize=flimit,
		                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
		                                                 Filters={'SearchQuery': [f"productId:{fproductId}"]})
		while 'NextPageToken' in response.keys():
			response2.extend(response['ProvisionedProducts'])
			response = client_sc.search_provisioned_products(PageToken=response['NextPageToken'],
			                                                 PageSize=flimit, AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
			                                                 Filters={'SearchQuery': [f"productId:{fproductId}"]})
	elif fproductId is not None:  # We filter down to only the statuses asked for and the productId
		response = client_sc.search_provisioned_products(PageSize=flimit,
		                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
		                                                 Filters={'SearchQuery': [f"status:{fStatus}", f"productId:{fproductId}"]})
		while 'NextPageToken' in response.keys():
			response2.extend(response['ProvisionedProducts'])
			response = client_sc.search_provisioned_products(PageSize=flimit,
			                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
			                                                 Filters={'SearchQuery': [f"status:{fStatus}", f"productId:{fproductId}"]},
			                                                 PageToken=response['NextPageToken'])
	else:  # We filter down to only the statuses asked for
		response = client_sc.search_provisioned_products(PageSize=flimit,
		                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
		                                                 Filters={'SearchQuery': [f"status:{fStatus}", f"productId:{fproductId}"]})
		while 'NextPageToken' in response.keys():
			response2.extend(response['ProvisionedProducts'])
			response = client_sc.search_provisioned_products(PageSize=flimit,
			                                                 AccessLevelFilter={'Key': 'Account', 'Value': 'self'},
			                                                 Filters={'SearchQuery': [f"status:{fStatus}", f"productId:{fproductId}"]},
			                                                 PageToken=response['NextPageToken'])
	response2.extend(response['ProvisionedProducts'])
	return response2


def find_ssm_parameters(fProfile, fRegion):
	"""
	fProfile is the Root Profile that owns the stackset
	fRegion is the region where the stackset resides

	Return Value is a list that looks like this:
	[
		{
			'Description': 'Contains the Local SNS Topic Arn for Landing Zone',
			'LastModifiedDate': datetime.datetime(2020, 2, 7, 12, 50, 2, 373000, tzinfo = tzlocal()),
			'LastModifiedUser': 'arn:aws:sts::517713657778:assumed-role/AWSCloudFormationStackSetExecutionRole/16b4abdd-1d1f-4aeb-8930-3e65dcef6bab',
			'Name': '/org/member/local_sns_arn',
			'Policies': [],
			'Tier': 'Standard',
			'Type': 'String',
			'Version': 1
		},
	]
	"""
	import boto3
	import logging
	from botocore.exceptions import ClientError
	ERASE_LINE = '\x1b[2K'

	logging.info(f"Finding ssm parameters for profile {fProfile} in Region {fRegion}")
	session_ssm = boto3.Session(profile_name=fProfile, region_name=fRegion)
	client_sts = session_ssm.client('sts')
	client_ssm = session_ssm.client('ssm')
	account_num = client_sts.get_caller_identity()['Account']
	response = {}
	response2 = []
	TotalParameters = 0

	try:
		response = client_ssm.describe_parameters(MaxResults=50)
	except ClientError as my_Error:
		logging.error(f"Error: {my_Error}")
	TotalParameters = TotalParameters + len(response['Parameters'])
	logging.info(f"Found another {len(response['Parameters'])} parameters, bringing the total up to {TotalParameters}")
	for param in response['Parameters']:
		response2.append({'AccountNum'      : account_num,
		                  'Region'          : session_ssm.region_name,
		                  'Profile'         : session_ssm.profile_name,
		                  'Description'     : param['Description'],
		                  'LastModifiedDate': param['LastModifiedDate'],
		                  'LastModifiedUser': param['LastModifiedUser'],
		                  'Name'            : param['Name'],
		                  'Policies'        : param['Policies'],
		                  'Tier'            : param['Tier'],
		                  'Type'            : param['Type'],
		                  'Version'         : param['Version']
		                  })
	while 'NextToken' in response.keys():
		response = client_ssm.describe_parameters(MaxResults=50, NextToken=response['NextToken'])
		TotalParameters = TotalParameters + len(response['Parameters'])
		logging.info(f"Found another {len(response['Parameters'])} parameters, bringing the total up to {TotalParameters}")
		for param in response['Parameters']:
			response2.append({'AccountNumber'   : account_num,
			                  'Region'          : session_ssm.region_name,
			                  'Profile'         : session_ssm.profile_name,
			                  'Description'     : param['Description'] if 'Description' in param.keys() else None,
			                  'LastModifiedDate': param['LastModifiedDate'],
			                  'LastModifiedUser': param['LastModifiedUser'],
			                  'Name'            : param['Name'],
			                  'Policies'        : param['Policies'],
			                  'Tier'            : param['Tier'],
			                  'Type'            : param['Type'],
			                  'Version'         : param['Version']
			                  })
		if (len(response2) % 500 == 0) and (logging.getLogger().getEffectiveLevel() > 20):
			print(f"{ERASE_LINE}Sorry this is taking a while - we've already found {len(response2)} parameters!", end="\r")

	logging.error(f"Found {len(response2)} parameters")
	return response2


def find_ssm_parameters2(ocredentials):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the Region where the authentication was done
		- ['MgmtAccount'] holds the AccountId
		- ['AccountNumber'] holds the AccountId

	Return Value is a list that looks like this:
	[
		{
			'Description': 'Contains the Local SNS Topic Arn for Landing Zone',
			'LastModifiedDate': datetime.datetime(2020, 2, 7, 12, 50, 2, 373000, tzinfo = tzlocal()),
			'LastModifiedUser': 'arn:aws:sts::517713657778:assumed-role/AWSCloudFormationStackSetExecutionRole/16b4abdd-1d1f-4aeb-8930-3e65dcef6bab',
			'Name': '/org/member/local_sns_arn',
			'Policies': [],
			'Tier': 'Standard',
			'Type': 'String',
			'Version': 1
		},
	]
	"""
	import logging
	import boto3
	from botocore.exceptions import ClientError
	ERASE_LINE = '\x1b[2K'

	region = ocredentials['Region']
	logging.info(f"Finding ssm parameters for account {ocredentials['AccountNumber']} in Region {region}")
	session_ssm = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_ssm = session_ssm.client('ssm')
	response = {}
	response2 = []
	TotalParameters = 0

	# TODO: Need to multi-thread this
	try:
		response = client_ssm.describe_parameters(MaxResults=50)
		TotalParameters = TotalParameters + len(response['Parameters'])
		logging.info(f"Found another {len(response['Parameters'])} parameters, bringing the total up to {TotalParameters}")
		for param in response['Parameters']:
			response2.append({'MgmtAcct'        : ocredentials['MgmtAccount'],
			                  'AccountNumber'   : ocredentials['AccountNumber'],
			                  'Region'          : region,
			                  'Profile'         : session_ssm.profile_name,
			                  'credentials'     : ocredentials,
			                  'Description'     : param['Description'] if 'Description' in param.keys() else None,
			                  'LastModifiedDate': param['LastModifiedDate'],
			                  'LastModifiedUser': param['LastModifiedUser'],
			                  'Name'            : param['Name'],
			                  'Policies'        : param['Policies'],
			                  'Tier'            : param['Tier'],
			                  'Type'            : param['Type'],
			                  'Version'         : param['Version']
			                  })
	except ClientError as my_Error:
		logging.error(f"Error: {my_Error}")
	while 'NextToken' in response.keys():
		response = client_ssm.describe_parameters(MaxResults=50, NextToken=response['NextToken'])
		TotalParameters = TotalParameters + len(response['Parameters'])
		logging.info(f"Found another {len(response['Parameters'])} parameters, bringing the total up to {TotalParameters}")
		for param in response['Parameters']:
			response2.append({'MgmtAcct'        : ocredentials['MgmtAccount'],
			                  'AccountNumber'   : ocredentials['AccountNumber'],
			                  'Region'          : session_ssm.region_name,
			                  'Profile'         : session_ssm.profile_name,
			                  'Description'     : param['Description'] if 'Description' in param.keys() else None,
			                  'LastModifiedDate': param['LastModifiedDate'],
			                  'LastModifiedUser': param['LastModifiedUser'],
			                  'Name'            : param['Name'],
			                  'Policies'        : param['Policies'],
			                  'Tier'            : param['Tier'],
			                  'Type'            : param['Type'],
			                  'Version'         : param['Version']
			                  })
		if (len(response2) % 500 == 0) and (logging.getLogger().getEffectiveLevel() > 20):
			print(f"{ERASE_LINE}Sorry this is taking a while - we've already found {len(response2)} parameters!", end="\r")

	if logging.getLogger().getEffectiveLevel() < 50:
		print(f"Found {len(response2)} parameters in account {ocredentials['AccountNumber']}")
	return response2


def find_ssm_parameters3(faws_acct, fregion=None):
	"""
	faws_acct is the class object from account_class.py
	fRegion is the region where the stackset resides

	Return Value is a list that looks like this:
	[
		{
			'Description': 'Contains the Local SNS Topic Arn for Landing Zone',
			'LastModifiedDate': datetime.datetime(2020, 2, 7, 12, 50, 2, 373000, tzinfo = tzlocal()),
			'LastModifiedUser': 'arn:aws:sts::517713657778:assumed-role/AWSCloudFormationStackSetExecutionRole/16b4abdd-1d1f-4aeb-8930-3e65dcef6bab',
			'Name': '/org/member/local_sns_arn',
			'Policies': [],
			'Tier': 'Standard',
			'Type': 'String',
			'Version': 1
		},
	]
	"""
	import logging
	from botocore.exceptions import ClientError
	ERASE_LINE = '\x1b[2K'

	if fregion is None:
		fregion = faws_acct.session.region_name
	logging.info(f"Finding ssm parameters for account {faws_acct.acct_number} in Region {fregion}")
	session_ssm = faws_acct.session
	client_ssm = session_ssm.client('ssm')
	response = {}
	response2 = []
	TotalParameters = 0

	try:
		response = client_ssm.describe_parameters(MaxResults=50)
		TotalParameters = TotalParameters + len(response['Parameters'])
		logging.info(f"Found another {len(response['Parameters'])} parameters, bringing the total up to {TotalParameters}")
		for param in response['Parameters']:
			response2.append({'MgmtAcct'        : faws_acct.MgmtAccount,
			                  'AccountNumber'   : faws_acct.acct_number,
			                  'Region'          : fregion,
			                  'Profile'         : session_ssm.profile_name,
			                  'Description'     : param['Description'] if 'Description' in param.keys() else None,
			                  'LastModifiedDate': param['LastModifiedDate'],
			                  'LastModifiedUser': param['LastModifiedUser'],
			                  'Name'            : param['Name'],
			                  'Policies'        : param['Policies'],
			                  'Tier'            : param['Tier'],
			                  'Type'            : param['Type'],
			                  'Version'         : param['Version']
			                  })
	except ClientError as my_Error:
		logging.error(f"Error: {my_Error}")
	while 'NextToken' in response.keys():
		response = client_ssm.describe_parameters(MaxResults=50, NextToken=response['NextToken'])
		TotalParameters = TotalParameters + len(response['Parameters'])
		logging.info(f"Found another {len(response['Parameters'])} parameters, bringing the total up to {TotalParameters}")
		for param in response['Parameters']:
			response2.append({'MgmtAcct'        : faws_acct.MgmtAccount,
			                  'AccountNumber'   : faws_acct.acct_number,
			                  'Region'          : session_ssm.region_name,
			                  'Profile'         : session_ssm.profile_name,
			                  'Description'     : param['Description'] if 'Description' in param.keys() else None,
			                  'LastModifiedDate': param['LastModifiedDate'],
			                  'LastModifiedUser': param['LastModifiedUser'],
			                  'Name'            : param['Name'],
			                  'Policies'        : param['Policies'],
			                  'Tier'            : param['Tier'],
			                  'Type'            : param['Type'],
			                  'Version'         : param['Version']
			                  })
		if (len(response2) % 500 == 0) and (logging.getLogger().getEffectiveLevel() > 20):
			print(f"{ERASE_LINE}Sorry this is taking a while - we've already found {len(response2)} parameters!", end="\r")

	if logging.getLogger().getEffectiveLevel() < 50:
		print(f"Found {len(response2)} parameters")
	return response2


def random_string(stringLength=10):
	"""
	Description: Generates a random string, to add to the session object when connecting to an account - to make the session unique
	@param stringLength: to determine the length of the random number generated
	@return: returns a random string of characters of length "stringlength"
	"""
	import random
	import string
	# Generate a random string of fixed length
	letters = string.ascii_lowercase
	randomstring = (''.join(random.choice(letters) for _ in range(stringLength)))
	return randomstring


def get_region_azs2(ocredentials):
	"""
	ocredentials is an object with the following structure:
		- ['AccessKeyId'] holds the AWS_ACCESS_KEY
		- ['SecretAccessKey'] holds the AWS_SECRET_ACCESS_KEY
		- ['SessionToken'] holds the AWS_SESSION_TOKEN
		- ['Region'] holds the Region where the authentication was done
		- ['MgmtAccount'] holds the AccountId
		- ['AccountNumber'] holds the AccountId

	Return Value is a list that looks like this:
	[
		{
			['AccountNumber'] holds the account number
			['Region'] holds the region name
			['Availability_Zone_Name'] holds the az *name*
			['Availability_Zone_id'] holds the az *id*
			'MgmtAccount'   : ocredentials['MgmtAccount'],
            'AccountNumber' : ocredentials['AccountNumber'],
            'Region'        : ocredentials['Region'],
            'Profile'       : ocredentials['Profile'],
            'ZoneName'      : az['ZoneName'],
            'ZoneId'        : az['ZoneId'],
            'OptInStatus'   : az['OptInStatus'],
            'ZoneType'      : az['ZoneType'],
            'State'         : az['State'],
            'ParentZoneName': az['ParentZoneName'] if 'ParentZoneName' in az.keys() else az['ZoneName'],
            'ParentZoneId'  : az['ParentZoneId'] if 'ParentZoneId' in az.keys() else az['ZoneId'],

		}
	]
	"""
	import logging
	import boto3
	from botocore.exceptions import ClientError

	logging.info(f"Finding available availability zones for account {ocredentials['AccountNumber']} in Region {ocredentials['Region']}")
	session_ec2 = boto3.Session(aws_access_key_id=ocredentials['AccessKeyId'],
	                            aws_secret_access_key=ocredentials['SecretAccessKey'],
	                            aws_session_token=ocredentials['SessionToken'],
	                            region_name=ocredentials['Region'])
	client_ec2 = session_ec2.client('ec2')
	return_response = []

	try:
		region_az_listing = client_ec2.describe_availability_zones(AllAvailabilityZones=True)
		for az in region_az_listing['AvailabilityZones']:
			if logging.getLogger().getEffectiveLevel() < 50:
				logging.info(f"Found another AZ called {az['ZoneName']} in region {az['RegionName']}")
			return_response.append({'MgmtAccount'   : ocredentials['MgmtAccount'],
			                        'AccountNumber' : ocredentials['AccountNumber'],
			                        'Region'        : ocredentials['Region'],
			                        'Profile'       : ocredentials['Profile'],
			                        'ZoneName'      : az['ZoneName'],
			                        'ZoneId'        : az['ZoneId'],
			                        'OptInStatus'   : az['OptInStatus'],
			                        'ZoneType'      : az['ZoneType'],
			                        'State'         : az['State'],
			                        'ParentZoneName': az['ParentZoneName'] if 'ParentZoneName' in az.keys() else az['ZoneName'],
			                        'ParentZoneId'  : az['ParentZoneId'] if 'ParentZoneId' in az.keys() else az['ZoneId'],
			                        })
	except ClientError as my_Error:
		logging.error(f"Error: {my_Error}")

	return return_response


############


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
			my_filename = f'{file_to_save}-{datetime.now().strftime("%y-%m-%d--%H-%M-%S")}'
			logging.info(f"Writing your data to: {my_filename}")
			with open(my_filename, 'w') as savefile:
				for field, value in sorted_display_dict.items():
					Heading += f"{value['Heading']}|"
				Heading += '\n'
				savefile.write(Heading)
				for result in results_list:
					row = ''
					for field, value in sorted_display_dict.items():
						data_format = 0
						if field not in result.keys():
							result[field] = defaultAction
						if result[field] is None:
							row += "|"
						elif isinstance(result[field], str):
							row += f"{result[field]:{data_format}s}|"
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
			print("If your data had a sub-display for additional data, it cannot be written to file yet... ")

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


def get_all_credentials(fProfiles: list = None, fTiming: bool = False, fSkipProfiles: list = None, fSkipAccounts: list = None, fRootOnly: bool = False, fAccounts: list = None, fRegionList: list = None, RoleList: list = None) -> list:
	"""
	Flow for this function:
		* DescribeRegion (to validate the region that's been provided)
		* GetCallerIdentity (to get the info from the profile(s) that's been provided - to determine if it's an Org account, the child accounts, etc.)
		* DescribeOrganization (Describes the Org for the profile that's been provided - so it understands whether it's an Org or a standalone account)
		* ListAccounts (to get information for the child/ member accounts within the Org)
		* xxxxx (One by one, it goes into each account to get STS credentials for each account, wihtin each region that's been provided)
		* Once it has all STS credentials, it arranges everything into a single list (of dicts) and returns the result.

	Note that this function returns the credentials of all the accounts in all the profiles passed to it

	Note that this function creates a new credential for every region, even though today - that's not necessary.
	However, some day accounts will be pegged to specific regions, and it will be necessary then.
	Description:
	@param fProfiles: list of profiles to look through (generally profiles of Organizations)
	@param fTiming: whether to display timings for functions
	@param fSkipProfiles: Profiles to skip (typically things like "_admin")
	@param fSkipAccounts: Accounts to skip over (like Core Accounts you want to avoid changing)
	@param fRootOnly: Whether you want to run for only the root account in the Org
	@param fAccounts: A list of specific accounts you're interested in, instead of all of them
	@param fRegionList: A list of regions you're interested in running this script against
	@param RoleList: A list of roles you want to use to gain access to child accounts
	@return: Returns a list of Credentials to the child accounts for use in many other functions
	"""
	import logging
	from account_class import aws_acct_access
	from time import time
	from colorama import init, Fore

	init()
	ERASE_LINE = '\x1b[2K'
	begin_time = time()
	print(f"{Fore.GREEN}Timing is enabled{Fore.RESET}") if fTiming else None

	AllCredentials = []
	if fSkipProfiles is None:
		fSkipProfiles = []
	if fSkipAccounts is None:
		fSkipAccounts = []
	if fAccounts is None:
		fAccounts = []
	if fRegionList is None:
		fRegionList = ['us-east-1']
	if fProfiles is None:  # Default use case from the classes
		print("Getting Accounts to check: ", end='')
		aws_acct = aws_acct_access()
		# This doesn't mean the profile "default", this is just what the label for the Org Name will be, since there's no other text
		profile = '-default-'
		RegionList = get_regions3(aws_acct, fRegionList)
		logging.info(f"No profile string passed in. Using string '-default-'")
		# This should populate the list "AllCreds" with the credentials for the relevant accounts.
		AllCredentials.extend(get_credentials_for_accounts_in_org(aws_acct, fSkipAccounts, fRootOnly, fAccounts, profile, RegionList, RoleList, fTiming))
	else:
		# This function gets the profiles that *match* fragments in the list
		ProfileList = get_profiles(fSkipProfiles=fSkipProfiles, fprofiles=fProfiles)

		logging.warning(f"These profiles are being checked {ProfileList}.")
		print(f"Getting Accounts to check across {len(ProfileList)} profile{'' if len(ProfileList) == 1 else 's'}")
		for profile in ProfileList:
			try:
				aws_acct = aws_acct_access(profile)
				if aws_acct.Success:
					pass
				else:
					continue
				RegionList = get_regions3(aws_acct, fRegionList)
				logging.warning(f"Looking at {profile} profile now across these regions {RegionList}... ")
				logging.debug(f"AWS account object: {aws_acct}\n"
				              f"Skip Accounts: {fSkipAccounts}\n"
				              f"Root Only flag: {fRootOnly}\n"
				              f"Account List passed in: {fAccounts}\n"
				              f"Profile: {profile}\n"
				              f"RegionList: {RegionList}\n"
				              f"RoleList: {RoleList}\n"
				              f"Timing Enabled: {fTiming}")
				# This should populate the list "AllCreds" with the credentials for the relevant accounts.
				AllCredentials.extend(get_credentials_for_accounts_in_org(aws_acct, fSkipAccounts, fRootOnly, fAccounts, profile, RegionList, RoleList, fTiming))
			except AttributeError as my_Error:
				error_message = f"Error in profile {profile}: {my_Error}"
				logging.error(error_message)
				continue
	return AllCredentials


def get_credentials_for_accounts_in_org(faws_acct, fSkipAccounts=None, fRootOnly=False, accountlist=None, fprofile="default", fregions=None, fRoleNames=None, fTiming=False, MaxThreads: int = 50):
	"""
	Note that this function returns the credentials of all the accounts underneath the Org passed to it.

	Note that this function creates a new credential for every region, even though today - that's not necessary.
	However, some day accounts will be pegged to specific regions, and it will be necessary then.
	"""
	import logging
	from tqdm.auto import tqdm
	from datetime import datetime
	from queue import Queue
	from threading import Thread
	from botocore.exceptions import ClientError
	from time import time
	from colorama import init, Fore

	init()
	begin_time = time()

	class AssembleCredentials(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_info, c_profile, c_region = self.queue.get()
				logging.info(f"De-queued info for account {c_account_info['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_info['AccountId']} using one of {fRoleNames}")
					faccount_credentials = get_child_access3(faws_acct, c_account_info['AccountId'], c_region, fRoleNames)
					if faccount_credentials['Success']:
						logging.info(f"Successfully connected to account {c_account_info['AccountId']}")
						faccount_credentials.update({'ParentProfile': c_profile,
						                             'RolesTried'   : fRoleNames})
					else:
						logging.error(f"Error connecting to account {c_account_info['AccountId']} in region {c_region}.\n"
						              f"Parent Profile was {c_profile}\n"
						              f"Error Message: {faccount_credentials['ErrorMessage']}")
						faccount_credentials.update({'MgmtAccount'  : c_account_info['MgmtAccount'],
						                             'AccountId'    : c_account_info['AccountId'],
						                             'AccountNumber': c_account_info['AccountId'],
						                             'ParentProfile': c_profile,
						                             'Region'       : c_region})
					AllCreds.append(faccount_credentials)
				except ClientError as my_Error:
					if "AuthFailure" in str(my_Error):
						logging.error(f"{account['AccountId']}: Authorization failure using role: {account_credentials['Role']}\n"
						              f"Error: {my_Error}")
					elif str(my_Error).find("AccessDenied") > 0:
						logging.error(f"{account['AccountId']}: Access Denied failure using role: {account_credentials['Role']}\n"
						              f"Error: {my_Error}")
					else:
						logging.error(f"{account['AccountId']}: Other kind of failure using role: {account_credentials['Role']}\n"
						              f"Error: {my_Error}")
					continue
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {account['AccountId']}\n"
					              f"Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles was wrong\n"
					              f"Error: {my_Error}")
					continue
				finally:
					pbar.update()
					self.queue.task_done()

	if fSkipAccounts is None:
		fSkipAccounts = []
	if accountlist is None:
		accountlist = []
	if fregions is None:
		fregions = ['us-east-1']

	if faws_acct.AccountType == 'Root':
		# Begin with all accounts within the org - we'll filter them out below.
		# This allows us to ensure that if they provided multiple profiles, with an account list,
		#   spanning both orgs, we're only considering accounts within the Org they specified.
		ChildAccounts = faws_acct.ChildAccounts
	elif faws_acct.AccountType == 'Child':
		logging.info(f"Account Type recognized as {faws_acct.AccountType}")
		if len(accountlist) == 0:
			# It's possible they ran with a profile that was a child account, but didn't specify an account list.
			ChildAccounts = faws_acct.ChildAccounts
		else:
			# Here we're assuming if they specified a child account in the profile, they're using delegated access to push out stacksets,
			# hence they need to specify the account list at the command prompt.
			# We should probably assume that all accounts are Active, but I'm not sure if that's a good idea yet, since we don't know.
			ChildAccounts = [{'AccountId': x, 'MgmtAccount': faws_acct.MgmtAccount} for x in accountlist]
		logging.info(f"There are {len(ChildAccounts)} accounts to gain credentials for...")
	else:
		# TODO: Eventually we'll need to raise an issue here, to point out that the account list needs to come from somewhere, if the profile isn't the Root,
		#  or the accounts being specified at the command line.
		# For now - we'll assume that if they provided a single account profile, with no listing, we should just use that single account.
		# They should only get to this point, if the account type was neither "Root" nor "Child", thus could be "StandAlone"
		ChildAccounts = faws_acct.ChildAccounts

	logging.debug(f"Account Passed in: {faws_acct.acct_number} | Child Accounts: {ChildAccounts} | Account Type: {faws_acct.AccountType} | Account Status: {faws_acct.AccountStatus} | RoleNames to try: {fRoleNames}")
	account_credentials = {'Role': 'Nothing'}
	AccountNum = RegionNum = 0
	AllCreds = []
	credqueue = Queue()

	# Defaults to 50, unless something more was passed in - which is only done for time testing.
	WorkerThreads = min(len(ChildAccounts) * len(fregions), MaxThreads)

	# Create x worker threads
	for x in range(WorkerThreads):
		worker = AssembleCredentials(credqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	pbar = tqdm(desc=f'Getting credentials for profile: {fprofile} with {len(ChildAccounts)} accounts in {len(fregions)} regions',
	            total=len(ChildAccounts) * len(fregions), unit=' credentials'
	            )

	logging.info(f"You asked to check {len(ChildAccounts) * len(fregions)} place{'s' if len(ChildAccounts) * len(fregions) > 1 else ''}... It's going to take a moment")
	logging.info(f"{Fore.GREEN}It's taken {time() - begin_time:.2f} seconds to prep WorkerThreads and such{Fore.RESET}") if fTiming else None
	for account in ChildAccounts:
		if account['AccountId'] in fSkipAccounts:
			continue
		elif fRootOnly and not account['AccountId'] == account['MgmtAccount']:
			continue
		elif accountlist and account['AccountId'] not in accountlist:
			continue
		AccountNum += 1
		logging.info(f"Queuing account info for {AccountNum} / {len(ChildAccounts)} accounts in profile {fprofile}")
		RegionNum = 0
		for region in fregions:
			RegionNum += 1
			logging.info(f"\t\tRegion {RegionNum} of {len(fregions)}")
			credqueue.put((account, fprofile, region))
			logging.info(f"Account / Region: {account} / {region} | {datetime.now()}")
			logging.info(f"Queue Size: {credqueue.qsize()}")
	print(f"{Fore.GREEN}Enumerating {AccountNum} account{'s' if len(ChildAccounts) * len(fregions) > 1 else ''} and {len(fregions)} regions "
	      f"took {time() - begin_time:.3f} seconds {Fore.RESET}") if fTiming else None
	credqueue.join()
	pbar.close()
	return AllCreds


def get_org_accounts_from_profiles(fProfileList):
	"""
	Note that this function returns account_class objects based on the list of profiles passed to it
	This function is fairly slow since it needs to call the aws_acct_access function for each profile.
	The linear function called "get_profiles" is much faster if you just want the list of profiles that match.
	"""
	import logging
	from queue import Queue
	from threading import Thread
	from tqdm.auto import tqdm
	from account_class import aws_acct_access
	from botocore.exceptions import ClientError, InvalidConfigError, NoCredentialsError

	class AssembleCredentials(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			Account = dict()
			while True:
				# Get the work from the queue and expand the tuple
				profile = self.queue.get()
				pbar.update()
				Account = {'ErrorFlag'   : False,
				           'Success'     : False,
				           'RootAcct'    : False,
				           'MgmtAccount' : None,
				           'profile'     : None,
				           'Email'       : None,
				           'ErrorMessage': None,
				           'OrgId'       : None}
				logging.info(f"De-queued info for account {profile}")
				try:
					logging.info(f"Trying profile {profile}")
					aws_acct = aws_acct_access(profile)
					Account['profile'] = profile
					Account['aws_acct'] = aws_acct
					if aws_acct.acct_number == 'Unknown':
						Account['ErrorFlag'] = True
						logging.info(f"Access to the profile {profile} has failed")
						pass
					elif aws_acct.AccountType.lower() == 'root':  # The Account is deemed to be a Management Account
						logging.info(f"AccountNumber: {aws_acct.acct_number}")
						Account['MgmtAccount'] = aws_acct.MgmtAccount
						Account['Email'] = aws_acct.MgmtEmail
						Account['OrgId'] = aws_acct.OrgID
						Account['Success'] = True
						Account['RootAcct'] = True
					elif aws_acct.AccountType.lower() in ['standalone', 'child']:
						Account['MgmtAccount'] = aws_acct.MgmtAccount
						Account['Email'] = aws_acct.MgmtEmail
						Account['OrgId'] = aws_acct.OrgID
						Account['Success'] = True
						Account['RootAcct'] = False
				except ClientError as my_Error:
					Account['ErrorFlag'] = True
					Account['ErrorMessage'] = my_Error
					if str(my_Error).find("AWSOrganizationsNotInUseException") > 0:
						Account['MgmtAcct'] = "Not an Org Account"
					elif str(my_Error).find("AccessDenied") > 0:
						Account['MgmtAcct'] = "Acct not auth for Org API."
					elif str(my_Error).find("InvalidClientTokenId") > 0:
						Account['MgmtAcct'] = "Credentials Invalid."
					elif str(my_Error).find("ExpiredToken") > 0:
						Account['MgmtAcct'] = "Token Expired."
					else:
						logging.error("Client Error")
						Account['ErrorMessage'] = my_Error
						logging.error(my_Error)
				except InvalidConfigError as my_Error:
					Account['ErrorFlag'] = True
					Account['ErrorMessage'] = my_Error
					if str(my_Error).find("does not exist") > 0:
						logging.error("Source profile error")
						logging.error(my_Error)
					else:
						logging.error("Credentials Error")
						logging.error(my_Error)
				except NoCredentialsError as my_Error:
					Account['ErrorFlag'] = True
					Account['ErrorMessage'] = my_Error
					if str(my_Error).find("Unable to locate credentials") > 0:
						Account['MgmtAcct'] = "This profile doesn't have credentials."
					else:
						logging.error("Credentials Error")
						logging.error(my_Error)
				except AttributeError or Exception as my_Error:
					Account['ErrorFlag'] = True
					Account['ErrorMessage'] = my_Error
					if str(my_Error).find("object has no attribute") > 0:
						Account['MgmtAcct'] = "This profile's credentials don't work."
						logging.error(my_Error)
					else:
						logging.error("Credentials Error")
						logging.error(my_Error)
				finally:
					self.queue.task_done()
				AllAccounts.append(Account)

	AllAccounts = []
	profilequeue = Queue()
	# WorkerThreads = len(fProfileList)
	WorkerThreads = 2

	# Create x worker threads
	for x in range(WorkerThreads):
		worker = AssembleCredentials(profilequeue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	pbar = tqdm(desc=f'Getting accounts from {len(fProfileList)} profiles',
	            total=len(fProfileList)
	            )

	for profile_item in fProfileList:
		logging.info(f"Queuing profile {profile_item} / {len(fProfileList)} profiles")
		profilequeue.put(profile_item)
	profilequeue.join()
	return AllAccounts
