from datetime import datetime
from dateutil.tz import tzutc, tzlocal

ListAccountsResponseData = {
	'Accounts': [
		{
			'Id'             : '111122223333',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/111122223333',
			'Email'          : 'example+LZRoot@notreal.com',
			'Name'           : 'LZRoot2',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': datetime(2018,
			                            7,
			                            19,
			                            23,
			                            32,
			                            57,
			                            676000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '777777777777',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykEXAMPLEmn/777777777777',
			'Email'          : 'example+LZ2FSA@notreal.com',
			'Name'           : 'fsa-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2018,
			                            12,
			                            5,
			                            4,
			                            2,
			                            39,
			                            398000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '333333333333',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/333333333333',
			'Email'          : 'example+LZ_Demo3@notreal.com',
			'Name'           : 'Test-Demo3',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': datetime(2020,
			                            9,
			                            8,
			                            18,
			                            32,
			                            1,
			                            416000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '555555555555',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/555555555555',
			'Email'          : 'example+LZ_Sec@notreal.com',
			'Name'           : 'security',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2018,
			                            10,
			                            30,
			                            17,
			                            12,
			                            14,
			                            78000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '888888888888',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/888888888888',
			'Email'          : 'example+LZ4-Log@notreal.com',
			'Name'           : 'logging',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': datetime(2021,
			                            2,
			                            17,
			                            15,
			                            10,
			                            24,
			                            597000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '222222222222',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/222222222222',
			'Email'          : 'example+LZ4-SS@notreal.com',
			'Name'           : 'shared-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': datetime(2021,
			                            2,
			                            17,
			                            15,
			                            10,
			                            46,
			                            390000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '999999999999',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/999999999999',
			'Email'          : 'example+LZ_Demo23@notreal.com',
			'Name'           : 'Test-Demo23',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2020,
			                            7,
			                            23,
			                            18,
			                            16,
			                            52,
			                            900000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '444444444444',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/444444444444',
			'Email'          : 'example+LZ_Log@notreal.com',
			'Name'           : 'logging',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2018,
			                            10,
			                            30,
			                            17,
			                            17,
			                            51,
			                            248000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '666666666666',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/666666666666',
			'Email'          : 'example+LZ2SS@notreal.com',
			'Name'           : 'shared-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2018,
			                            10,
			                            26,
			                            23,
			                            27,
			                            11,
			                            350000,
			                            tzinfo=tzlocal())
			},
		{
			'Id'             : '111111111111',
			'Arn'            : 'arn:aws:organizations::111122223333:account/o-ykfx0legmn/111111111111',
			'Email'          : 'example+Demo2@notreal.com',
			'Name'           : 'Demo2',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2018,
			                            12,
			                            4,
			                            10,
			                            15,
			                            6,
			                            149000,
			                            tzinfo=tzlocal())
			}
		]
	}
DescribeRegionsResponseData = {
	'Regions': [
		{
			'Endpoint'   : 'ec2.af-south-1.amazonaws.com',
			'RegionName' : 'af-south-1',
			'OptInStatus': 'opted-in'
			},
		{
			'Endpoint'   : 'ec2.ap-south-1.amazonaws.com',
			'RegionName' : 'ap-south-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.eu-north-1.amazonaws.com',
			'RegionName' : 'eu-north-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.eu-west-3.amazonaws.com',
			'RegionName' : 'eu-west-3',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.eu-south-1.amazonaws.com',
			'RegionName' : 'eu-south-1',
			'OptInStatus': 'opted-in'
			},
		{
			'Endpoint'   : 'ec2.eu-west-2.amazonaws.com',
			'RegionName' : 'eu-west-2',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.eu-west-1.amazonaws.com',
			'RegionName' : 'eu-west-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.ap-northeast-3.amazonaws.com',
			'RegionName' : 'ap-northeast-3',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.ap-northeast-2.amazonaws.com',
			'RegionName' : 'ap-northeast-2',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.me-south-1.amazonaws.com',
			'RegionName' : 'me-south-1',
			'OptInStatus': 'opted-in'
			},
		{
			'Endpoint'   : 'ec2.ap-northeast-1.amazonaws.com',
			'RegionName' : 'ap-northeast-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.il-central-1.amazonaws.com',
			'RegionName' : 'il-central-1',
			'OptInStatus': 'opted-in'
			},
		{
			'Endpoint'   : 'ec2.ca-central-1.amazonaws.com',
			'RegionName' : 'ca-central-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.sa-east-1.amazonaws.com',
			'RegionName' : 'sa-east-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.ap-southeast-1.amazonaws.com',
			'RegionName' : 'ap-southeast-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.ap-southeast-2.amazonaws.com',
			'RegionName' : 'ap-southeast-2',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.eu-central-1.amazonaws.com',
			'RegionName' : 'eu-central-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.eu-central-2.amazonaws.com',
			'RegionName' : 'eu-central-2',
			'OptInStatus': 'opted-in'
			},
		{
			'Endpoint'   : 'ec2.us-east-1.amazonaws.com',
			'RegionName' : 'us-east-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.us-east-2.amazonaws.com',
			'RegionName' : 'us-east-2',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.us-west-1.amazonaws.com',
			'RegionName' : 'us-west-1',
			'OptInStatus': 'opt-in-not-required'
			},
		{
			'Endpoint'   : 'ec2.us-west-2.amazonaws.com',
			'RegionName' : 'us-west-2',
			'OptInStatus': 'opt-in-not-required'
			}
		]
	}
DescribeOrganizationsResponseData = {
	'Organization': {
		'Id'                  : 'o-ykEXAMPLEmn',
		'Arn'                 : 'arn:aws:organizations::111122223333:organization/o-ykEXAMPLEmn',
		'FeatureSet'          : 'ALL',
		'MasterAccountArn'    : 'arn:aws:organizations::111122223333:account/o-ykEXAMPLEmn/111122223333',
		'MasterAccountId'     : '111122223333',
		'MasterAccountEmail'  : 'me+LZRoot@notreal.com',
		'AvailablePolicyTypes': [
			{
				'Type'  : 'SERVICE_CONTROL_POLICY',
				'Status': 'ENABLED'
				}
			]
		}
	}
GetCallerIdentity = {
	'UserId' : 'xxxx111122223333xxxxx',
	'Account': '111122223333',
	'Arn'    : 'arn:aws:iam::111122223333:user/Paul'
	}
cli_provided_parameters1 = {
	'pProfiles'    : ['LZRoot14'],
	'pRegionList'  : ['us-east-1',
	                  'eu-west-1'],
	'pSkipProfiles': [],
	'pSkipAccounts': [],
	'pRoleList'    : [],
	'pAccountList' : [],
	'pTiming'      : True,
	'pRootOnly'    : False,
	'pSaveFilename': None,
	'pShortform'   : False,
	'pverbose'     : 20}
cli_provided_parameters2 = {
	'pProfiles'    : ['LZRoot'],
	'pSkipProfiles': [],
	'pAccountList' : [],
	'pTiming'      : True,
	'pRootOnly'    : True,
	'pSaveFilename': None,
	'pShortform'   : False,
	'pverbose'     : 50}

# Below is 10 Credentials
CredentialResponseData = [
	# Management Account Credentials
	{'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Root',
	 'AccessKeyId'    : 'xxxx111122223333xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : None,
	 'AccountNumber'  : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'Use Profile',
	 'Profile'        : 'mock_profile',
	 'AccessError'    : False,
	 'Success'        : True,
	 'ErrorMessage'   : None,
	 'ParentProfile'  : 'mock_profile_1'},
	# Child Accounts Credentials
	{'AccessKeyId'    : 'xxxx444455556666xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '444455556666',
	 'AccountId'      : '444455556666',
	 'Region'         : 'us-east-2',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_2'},
	{'AccessKeyId'    : 'xxxx555566667777xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '555566667777',
	 'AccountId'      : '555566667777',
	 'Region'         : 'us-west-2',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_3'},
	{'AccessKeyId'    : 'xxxx555566667777xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, 18, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '555566667777',
	 'AccountId'      : '555566667777',
	 'Region'         : 'eu-west-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_4'},
	{'AccessKeyId'    : 'xxxx666677775555xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '666677775555',
	 'AccountId'      : '666677775555',
	 'Region'         : 'eu-central-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_5'},
	{'AccessKeyId'    : 'xxxx777755556666xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '777755556666',
	 'AccountId'      : '777755556666',
	 'Region'         : 'eu-north-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_6'},
	{'AccessKeyId'    : 'xxxx777755556666xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '777755556666',
	 'AccountId'      : '777755556666',
	 'Region'         : 'eu-west-2',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_7'},
	{'AccessKeyId'    : 'xxxx666677778888xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '666677778888',
	 'AccountId'      : '666677778888',
	 'Region'         : 'ap-south-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_8'},
	{'AccessKeyId'    : 'xxxx777788886666xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '777788886666',
	 'AccountId'      : '777788886666',
	 'Region'         : 'il-central-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_9'},
	{'AccessKeyId'    : 'xxxx888866667777xxxxx',
	 'SecretAccessKey': '*****SecretAccessKeyHere*****',
	 'SessionToken'   : '*****SessionTokenHere*****',
	 'Expiration'     : datetime(2023, 9, 8, 1, 30, tzinfo=tzutc()),
	 'ParentAcctId'   : '111122223333',
	 'MgmtAccount'    : '111122223333',
	 'OrgType'        : 'Child',
	 'AccountNumber'  : '888866667777',
	 'AccountId'      : '888866667777',
	 'Region'         : 'af-south-1',
	 'AccountStatus'  : 'ACTIVE',
	 'RolesTried'     : None,
	 'Role'           : 'AWSCloudFormationStackSetExecutionRole',
	 'Profile'        : None,
	 'AccessError'    : False,
	 'ErrorMessage'   : None,
	 'Success'        : True,
	 'ParentProfile'  : 'mock_profile_10'}]

AssumeRoleResponseData = {'Credentials': {
	'AccessKeyId'    : 'xxxxAccountNumberxxxxx',
	'SecretAccessKey': '*****SecretAccessKeyHere*****',
	'SessionToken'   : '*****SessionTokenHere*****',
	'Expiration'     : datetime(2023,
	                            9,
	                            24,
	                            0,
	                            3,
	                            4,
	                            tzinfo=tzutc())}}
# 20 functions below - all meeting the filter criteria of either being runtime 'python3.9' or with the fragment 'Metric' in the name, all within one account, within one region (us-east-1).
# Function response data from the Inventory_Scripts function, and not boto3.
t = [
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111111111111:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111111111111:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-10GM1SS21LPJ4',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-14R9E4I39TMGH',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111111111111:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-14R9E4I39TMGH',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-1ROC6UIWPU7BM',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'CloudFormationApply',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:CloudFormationApply',
	 'Role'           : 'service-role/myLambdaRunCode_Role',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZone',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZone',
	 'Role'           : 'LandingZoneLambdaRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZoneAddonPublisher',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneAddonPublisher',
	 'Role'           : 'LZ-Initiation-PublisherLambdaRole-1U2ELSGH61W55',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZoneDeploymentLambda',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneDeploymentLambda',
	 'Role'           : 'LandingZoneDeploymentLambdaRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZoneHandshakeSMLambda',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneHandshakeSMLambda',
	 'Role'           : 'LandingZoneHandshakeSMLambdaRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1J4CB75JBXNYO',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZoneStateMachineLambda',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneStateMachineLambda',
	 'Role'           : 'StateMachineLambdaRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'LandingZoneStateMachineTriggerLambda',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneStateMachineTriggerLambda',
	 'Role'           : 'StateMachineTriggerLambdaRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'SC-111122223333-pp-n6374w-LandingZoneAddOnDeployme-3vcpGQMxeWXT',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:SC-111122223333-pp-n6374w-LandingZoneAddOnDeployme-3vcpGQMxeWXT',
	 'Role'           : 'LandingZoneDeploymentLambdaRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-UF2T2MKY3NJF',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-UF2T2MKY3NJF',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-RVDISB3T58RV',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'org-dep-checker-OrgDependencyCheckerFunction-LOoXu13rmtpr',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:111122223333:function:org-dep-checker-OrgDependencyCheckerFunction-LOoXu13rmtpr',
	 'Role'           : 'org-dep-checker-OrgDependencyCheckerFunctionRole-Q70Z1POVGX9S',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : None},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:292902349725:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '292902349725',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:292902349725:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1B95P1B7Y1U3H',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '292902349725',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-E3EYVN9PTV7I',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:292902349725:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-E3EYVN9PTV7I',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-4TLTYE61OQRU',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '292902349725',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:222222222222:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:222222222222:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-ZB120L4B39DW',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '222222222222',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-6KP78QBS1J5L',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:222222222222:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-6KP78QBS1J5L',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-YKAMOJLAYNZV',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:333333333333:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:333333333333:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1CI5HVHBI7WKR',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-166N622Y1F1D8',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:333333333333:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-166N622Y1F1D8',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-14NLLL8TQ2AIO',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'GetStartedLambdaProxyIntegration',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:GetStartedLambdaProxyIntegration',
	 'Role'           : 'service-role/GetStartedLambdaBasicExecutionRole',
	 'Runtime'        : 'nodejs10.x',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'InvokeCloudFormation',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:InvokeCloudFormation',
	 'Role'           : 'service-role/InvokeCloudFormation-role-03z41yeg',
	 'Runtime'        : 'nodejs10.x',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LambdaAuthorizerExample',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:LambdaAuthorizerExample',
	 'Role'           : 'service-role/LambdaAuthorizerExample-role-03sn3n1k',
	 'Runtime'        : 'python2.7',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LambdaAuthorizerRequestTypeCustom',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:LambdaAuthorizerRequestTypeCustom',
	 'Role'           : 'service-role/LambdaAuthorizerRequestTypeCustom-role-iiyuxrue',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '444444444444',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1WSZCDKENGDSH',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'SagemakerInvokerBlazingText',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:SagemakerInvokerBlazingText',
	 'Role'           : 'service-role/SagemakerInvokerBlazingText-role-kkbzh050',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-A3VSMQU7FRMR',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-A3VSMQU7FRMR',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-16O26U382TMXG',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Telemetry_LogCleaup',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:Telemetry_LogCleaup',
	 'Role'           : 'service-role/Telemetry_LogCleaup-role-aomd82zq',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'dotnetcorelambda',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:dotnetcorelambda',
	 'Role'           : 'service-role/dotnetcorelambda-role-qk445824',
	 'Runtime'        : 'dotnetcore2.1',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'hellonodejs',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:hellonodejs',
	 'Role'           : 'service-role/hellonodejs-role-2nvxxxy7',
	 'Runtime'        : 'nodejs8.10',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'secretrotationfunction',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:444444444444:function:secretrotationfunction',
	 'Role'           : 'service-role/secretrotationfunction-role-4v03rkfq',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:555555555555:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:555555555555:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-WCIU8QEBAZGA',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '555555555555',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-NC3Z57YQ4VF3',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:555555555555:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-NC3Z57YQ4VF3',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-1U8PG0E7R57HS',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:666666666666:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:666666666666:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-E599EO74LGXA',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '666666666666',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-HRX910NRFLLR',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:666666666666:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-HRX910NRFLLR',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-JSXKBH9MQ0CV',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:777777777777:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:777777777777:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1UVK1I2XFTK92',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-9SUEVBGP134A',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:777777777777:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-9SUEVBGP134A',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-1SVZOOUOCKDFR',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'Create_CW_Metrics',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:888888888888:function:Create_CW_Metrics',
	 'Role'           : 'Create_CW_MetricsRole',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneGuardDutyNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:888888888888:function:LandingZoneGuardDutyNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1LL63QEBS7M0O',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'LandingZoneLocalSNSNotificationForwarder',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:888888888888:function:LandingZoneLocalSNSNotificationForwarder',
	 'Role'           : 'StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-7STAM9IH9WC1',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '888888888888',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-8PPP3LFKM4C4',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:888888888888:function:StackSet-AWS-Landing-Zone-IamPasswordPolicyCustomR-8PPP3LFKM4C4',
	 'Role'           : 'StackSet-AWS-Landing-Zone-Baseline-IamP-LambdaRole-RG7FX3KV68EL',
	 'Runtime'        : 'python3.8',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'CheckPipelineStatus',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:999999999999:function:CheckPipelineStatus',
	 'Role'           : 'adf-lambda-role',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'PipelinesCreateInitialCommitFunction',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:999999999999:function:PipelinesCreateInitialCommitFunction',
	 'Role'           : 'adf-global-base-deploymen-InitialCommitHandlerRole-21R8IK57XL0X',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '999999999999',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'SendSlackNotification',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:999999999999:function:SendSlackNotification',
	 'Role'           : 'adf-lambda-role',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'},
	{'FunctionName'   : 'UpdateCrossAccountIAM',
	 'FunctionArn'    : 'arn:aws:lambda:us-east-1:999999999999:function:UpdateCrossAccountIAM',
	 'Role'           : 'adf-lambda-role',
	 'Runtime'        : 'python3.9',
	 'MgmtAccount'    : '111122223333',
	 'AccountId'      : '111122223333',
	 'Region'         : 'us-east-1',
	 'AccessKeyId'    : '***AccessKeyIdHere***',
	 'SecretAccessKey': '***SecretAccessKeyHere***',
	 'SessionToken'   : '***SessionTokenHere***'}]

mock_profile_list_1 = ['default', 'mock_profile_1']
mock_profile_list_2 = ['default', 'mock_profile_2']
mock_profile_list_3 = ['default', 'mock_profile_3']
mock_profile_list_4 = ['default', 'mock_profile_4']
mock_region_list_1 = ['us-east-1']
mock_region_list_2 = ['us-east-1', 'us-east-2']
mock_region_list_3 = ['eu-west-1', 'eu-central-1']
mock_region_list_4 = ['all']
mock_region_list_5 = ['global']

"""
all_my_functions Test Data
"""
account_and_region_specific_function_response_data = [
	{
		'Account'        : '111122223333',
		'Region'         : 'us-east-1',
		'mocked_response': {
			'Functions': [
				{
					'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyValidate-tziul2Otm32F',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyValidate-tziul2Otm32F',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-ValidateSpokeAccountAccess',
					'Handler'         : 'resource_based_policy/step_functions_lambda/validate_account_access.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 900,
					'MemorySize'      : 1024,
					'LastModified'    : '2023-04-14T15:01:53.312+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'SPOKE_ROLE_NAME'        : 'paulbaye-us-east-1-AccountAssessment-Spoke-ExecutionRole',
							'POWERTOOLS_SERVICE_NAME': 'ScanResourceBasedPolicy',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'TIME_TO_LIVE_IN_DAYS'   : '90',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
							'LOG_LEVEL'              : 'INFO',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '6e9ec792-08c6-491d-aa19-aad57aeab78d',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-TrustedAccessStartScan70308-LfEGZM07HEP6',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-TrustedAccessStartScan70308-LfEGZM07HEP6',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-TrustedAccess',
					'Handler'         : 'trusted_access_enabled_services/scan_for_trusted_services.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 120,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:53.914+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME' : 'ScanTrustedAccess',
							'SEND_ANONYMOUS_DATA'     : 'Yes',
							'ORG_MANAGEMENT_ROLE_NAME': 'paulbaye-us-east-1-AccountAssessment-OrgMgmtStackRole',
							'TIME_TO_LIVE_IN_DAYS'    : '90',
							'STACK_ID'                : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'              : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'         : 'AccountAssessmentStack-TrustedAccessTable495B447A-GTR0RYDUJU5Q',
							'LOG_LEVEL'               : 'INFO',
							'SOLUTION_VERSION'        : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '943aca8c-3984-45cb-97ce-fd3e2a8f7c03',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'lock_down_stacks_sets_role',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:lock_down_stacks_sets_role',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/service-role/lock_down_stacks_sets_role-role-pgehgfag',
					'Handler'         : 'lambda_function.lambda_handler',
					'CodeSize'        : 299,
					'Description'     : '',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T15:50:05.000+0000',
					'CodeSha256'      : 'fI06ZlRH/KN6Ra3twvdRllUYaxv182Tjx0qNWNlKIhI=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'ec0a7b23-c892-4dc8-935c-954bf6990bf5',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'PrintOutEvents_Function',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:PrintOutEvents_Function',
					'Runtime'         : 'python3.8',
					'Role'            : 'arn:aws:iam::111122223333:role/service-role/PrintOutEvents_Function-role-p29wwswh',
					'Handler'         : 'lambda_function.lambda_handler',
					'CodeSize'        : 309,
					'Description'     : '',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2023-02-03T20:41:15.016+0000',
					'CodeSha256'      : 'O3OGwvaAIbPJr4rqhF1OZuuDThX1qcaCGGEekuse8OY=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'cfeb671f-f08d-4217-8263-b5110101baf9',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyFinishAs-n8TanL9sDr9r',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyFinishAs-n8TanL9sDr9r',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-ResourceBasedPolicyFinishAs-1RO9MOHKM92VA',
					'Handler'         : 'resource_based_policy/finish_scan.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 60,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:53.878+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME': 'FinishScanForResourceBasedPolicies',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'TIME_TO_LIVE_IN_DAYS'   : '90',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : 'e422e2e3-de5b-4a1d-b1f1-09b6125d230e',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-DelegatedAdminsStartScanE7D-Qk14ANSD75ay',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-DelegatedAdminsStartScanE7D-Qk14ANSD75ay',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-DelegatedAdmin',
					'Handler'         : 'delegated_admins/scan_for_delegated_admins.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 120,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:52.995+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME' : 'ScanDelegatedAdmin',
							'SEND_ANONYMOUS_DATA'     : 'Yes',
							'ORG_MANAGEMENT_ROLE_NAME': 'paulbaye-us-east-1-AccountAssessment-OrgMgmtStackRole',
							'TIME_TO_LIVE_IN_DAYS'    : '90',
							'STACK_ID'                : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'              : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'         : 'AccountAssessmentStack-DelegatedAdminsTable29E80916-F34FK4FZGFP5',
							'LOG_LEVEL'               : 'INFO',
							'SOLUTION_VERSION'        : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : 'd3fdc6a8-35b5-44b6-ae21-a533eea3f478',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'UpsertDNSNameLambda',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:UpsertDNSNameLambda',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/UpsertDNSNameToSQSQueueLambdaRole',
					'Handler'         : 'Route53PHZLambdaUpdate.lambda_handler',
					'CodeSize'        : 2164,
					'Description'     : 'Lambda to to update DNS Hosted Zone for EC2 starts',
					'Timeout'         : 20,
					'MemorySize'      : 256,
					'LastModified'    : '2023-02-04T02:25:54.603+0000',
					'CodeSha256'      : 'RC3e1d8z3DRLwxRK32sVJ+VoPpsBCRNZLPWzKLgqoHE=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'HOSTED_ZONE_ID': 'Z06954483PM26JFJ0ET4L',
							'CENTRAL_ACCT'  : '444444444444',
							'QUEUE_NAME'    : 'myDNSUpsertQueue',
							'TIME_TO_LIVE'  : '300',
							'LOG_LEVEL'     : 'INFO'
							}
						},
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'bbfc8a57-67de-426f-a63d-08996b688bd8',
					'Layers'          : [
						{
							'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:DistributedBoto3Library:9',
							'CodeSize': 12119917
							}
						],
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyScanSpok-xWlINDye4FUd',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyScanSpok-xWlINDye4FUd',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-ScanSpokeResource',
					'Handler'         : 'resource_based_policy/step_functions_lambda/scan_policy_all_services_router.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 900,
					'MemorySize'      : 512,
					'LastModified'    : '2023-04-14T15:01:54.774+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'SPOKE_ROLE_NAME'        : 'paulbaye-us-east-1-AccountAssessment-Spoke-ExecutionRole',
							'POWERTOOLS_SERVICE_NAME': 'ScanResourceBasedPolicyInSpokeAccount',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'TIME_TO_LIVE_IN_DAYS'   : '90',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
							'LOG_LEVEL'              : 'INFO',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '5d2d6891-e38f-4038-a5c6-fd0be145f34e',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'vpc-mappings-111122223333',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:vpc-mappings-111122223333',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AZ-Mapping-LambdaIAMRole-1MWVK82KVY9O5',
					'Handler'         : 'index.lambda_handler',
					'CodeSize'        : 1711,
					'Description'     : 'Stores VPC mappings into parameter store',
					'Timeout'         : 5,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T16:44:28.000+0000',
					'CodeSha256'      : 'H1vz9hfL3eHL/GigRMwy5E7ngxFl1XHzaSP5Dai3M8Y=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : '14153c9e-b5d0-4e0a-9d18-93868f7dd1ae',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyReadDC5D-4fhaK4485acJ',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyReadDC5D-4fhaK4485acJ',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-ResourceBasedPolicyReadServ-12WZ14XZFTC18',
					'Handler'         : 'resource_based_policy/read_resource_based_policies.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 60,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:53.924+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME': 'ReadResourceBasedPolicy',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : 'fe607630-2342-4d09-98d2-cee63552cb05',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'Fix_Default_SGs',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:Fix_Default_SGs',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/service-role/Fix_Default_SGs-role-qc5pamya',
					'Handler'         : 'lambda_function.lambda_handler',
					'CodeSize'        : 740,
					'Description'     : '',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T16:33:20.000+0000',
					'CodeSha256'      : 'XZF1c2Xfl/YT+twYFVmlAGGuuNTO7i3J2FTCMoqFVew=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'c60151c0-f460-4dfe-98b5-47f6710447b8',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyStartSca-RU8utlGVjJyc',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyStartSca-RU8utlGVjJyc',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-ResourceBasedPolicy',
					'Handler'         : 'resource_based_policy/start_state_machine_execution_to_scan_services.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 120,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:02:10.418+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME'               : 'ScanResourceBasedPolicy',
							'SEND_ANONYMOUS_DATA'                   : 'Yes',
							'ORG_MANAGEMENT_ROLE_NAME'              : 'paulbaye-us-east-1-AccountAssessment-OrgMgmtStackRole',
							'SCAN_RESOURCE_POLICY_STATE_MACHINE_ARN': 'arn:aws:states:us-east-1:111122223333:stateMachine:ResourceBasedPolicyScanAllSpokeAccounts38C6FB6E-hEkgjewVuwLc',
							'TIME_TO_LIVE_IN_DAYS'                  : '90',
							'STACK_ID'                              : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'                            : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'                       : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
							'LOG_LEVEL'                             : 'INFO',
							'SOLUTION_VERSION'                      : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '4d80914c-9423-435d-b1fe-d48125ea064d',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyReadScan-DbzA0NZGeTb3',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyReadScan-DbzA0NZGeTb3',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-ResourceBasedPolicyReadScan-14UZV70G67KSO',
					'Handler'         : 'resource_based_policy/supported_configuration/scan_configurations.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 600,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:54.572+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME': 'ReadScanConfigs',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
							'LOG_LEVEL'              : 'INFO',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : 'b0f59e30-6d16-4368-80b2-27ed25d16d1e',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-WebUIDeployerDeployWebUIC2B-ZL1H4n2W05xe',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-WebUIDeployerDeployWebUIC2B-ZL1H4n2W05xe',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-WebUIDeployerDeployWebUISer-SXOS38SBZPWQ',
					'Handler'         : 'deploy_webui/deploy_webui.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 300,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:06:17.107+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'CONFIG'                 : '{"SrcBucket":"solutions-us-east-1","SrcPath":"account-assessment-for-aws-organizations/v1.0.3/webui/","WebUIBucket":"accountassessmentstack-s3bucket07682993-1qnr9dfvuvn8m","awsExports":{"API":{"endpoints":[{"name":"AccountAssessmentApi","endpoint":"https://5ugessads8.execute-api.us-east-1.amazonaws.com/prod"}]},"loggingLevel":"INFO","Auth":{"region":"us-east-1","userPoolId":"us-east-1_4y5EH6RX3","userPoolWebClientId":"10hrrgcdjum45c4jmre3kv7r7d","mandatorySignIn":true,"oauth":{"domain":"paulbaye-amzn.auth.us-east-1.amazoncognito.com","scope":["openid","profile","email","aws.cognito.signin.user.admin"],"redirectSignIn":"https://d12i33hlb8s7se.cloudfront.net/","redirectSignOut":"https://d12i33hlb8s7se.cloudfront.net/","responseType":"code","clientId":"10hrrgcdjum45c4jmre3kv7r7d"}}}}',
							'POWERTOOLS_SERVICE_NAME': 'DeployWebUI',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'LOG_LEVEL'              : 'INFO',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : 'b79766f8-4e8d-438c-a5b5-8d5e656a165e',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'orgformation-EmptyS3BucketOnDeletionLambdaFunction-W98Id8S5pK33',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:orgformation-EmptyS3BucketOnDeletionLambdaFunction-W98Id8S5pK33',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/orgformation-EmptyS3BucketOnDeletionLambdaExecutio-1SLZXRGG2YUT5',
					'Handler'         : 'index.handler',
					'CodeSize'        : 1412,
					'Description'     : '',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T16:44:28.000+0000',
					'CodeSha256'      : 'kK3SVtC1I7ezvKPsNwno7YY9AfCKV3kkA56RV8kD3DE=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'c5d3cf2d-8a26-41d0-a0e8-60a36bca1103',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-JobHistoryJobsHandler060579-EShvGJzftPCt',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-JobHistoryJobsHandler060579-EShvGJzftPCt',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-JobHistoryJobsHandlerServic-HXRBGBPC98KW',
					'Handler'         : 'assessment_runner/api_router.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 60,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:53.918+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_LOGGER_LOG_EVENT': 'True',
							'POWERTOOLS_SERVICE_NAME'    : 'JobsApiHandler',
							'SEND_ANONYMOUS_DATA'        : 'Yes',
							'TABLE_TRUSTED_ACCESS'       : 'AccountAssessmentStack-TrustedAccessTable495B447A-GTR0RYDUJU5Q',
							'TABLE_DELEGATED_ADMIN'      : 'AccountAssessmentStack-DelegatedAdminsTable29E80916-F34FK4FZGFP5',
							'TIME_TO_LIVE_IN_DAYS'       : '90',
							'STACK_ID'                   : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'                 : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'SOLUTION_VERSION'           : 'v1.0.3',
							'TABLE_RESOURCE_BASED_POLICY': 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '4ebd1e01-2898-4dab-8fb2-a42bad2bb1df',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'CreateidpProvider',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:CreateidpProvider',
					'Runtime'         : 'python2.7',
					'Role'            : 'arn:aws:iam::111122223333:role/service-role/CreateidpProvider-role-o7h6t6no',
					'Handler'         : 'lambda_function.lambda_handler',
					'CodeSize'        : 886,
					'Description'     : '',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2019-05-02T15:03:42.436+0000',
					'CodeSha256'      : 'QvxbS4ZbI9bivuDn5kp7ARuHikbV5Xf3/SN3bKCcQdY=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : '42c3c4df-fe81-4dfd-9cd8-827a478407b7',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'P9E-a8ba4fea-1856-49ca-8aa4-2b7e9b58d7a6',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:P9E-a8ba4fea-1856-49ca-8aa4-2b7e9b58d7a6',
					'Runtime'         : 'python3.7',
					'Role'            : 'arn:aws:iam::111122223333:role/aws-perspective-51771365777-LambdaEdgeFunctionRole-15OZK21LEUC5O',
					'Handler'         : 'append_headers.handler',
					'CodeSize'        : 1039,
					'Description'     : 'Lambda@Edge for secure headers',
					'Timeout'         : 5,
					'MemorySize'      : 128,
					'LastModified'    : '2020-09-22T15:54:23.904+0000',
					'CodeSha256'      : 'tZMc1X5ewz2jkq2rML6VPQgb3x4T9wnYvnMacZHO65I=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'ffa243e9-dbe5-4424-970a-96ecfb5e4a3b',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-TrustedAccessRead96AB6071-NKktqhxZ7fTz',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-TrustedAccessRead96AB6071-NKktqhxZ7fTz',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-TrustedAccessReadServiceRol-1RC8YXWIAP9YN',
					'Handler'         : 'trusted_access_enabled_services/read_trusted_services.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 60,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:53.616+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME': 'ReadTrustedAccess',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-TrustedAccessTable495B447A-GTR0RYDUJU5Q',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '41db914e-32ea-4b7c-8a05-a78def9856b1',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'AccountAssessmentStack-DelegatedAdminsRead591DCC7E-AyGSKEOHKNm2',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-DelegatedAdminsRead591DCC7E-AyGSKEOHKNm2',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-DelegatedAdminsReadServiceR-NA50GOH53141',
					'Handler'         : 'delegated_admins/read_delegated_admins.lambda_handler',
					'CodeSize'        : 17578832,
					'Description'     : '',
					'Timeout'         : 60,
					'MemorySize'      : 128,
					'LastModified'    : '2023-04-14T15:01:54.770+0000',
					'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'POWERTOOLS_SERVICE_NAME': 'ReadDelegatedAdmin',
							'SEND_ANONYMOUS_DATA'    : 'Yes',
							'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
							'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
							'COMPONENT_TABLE'        : 'AccountAssessmentStack-DelegatedAdminsTable29E80916-F34FK4FZGFP5',
							'SOLUTION_VERSION'       : 'v1.0.3'
							}
						},
					'TracingConfig'   : {
						'Mode': 'Active'
						},
					'RevisionId'      : '677f7ad5-f7d2-44d7-a3dd-c026e022b2fb',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					}
				]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'eu-west-1',
		'mocked_response': {
			'Functions': [
				{
					'FunctionName'    : 'Create_CW_Metrics',
					'FunctionArn'     : 'arn:aws:lambda:eu-west-1:111122223333:function:Create_CW_Metrics',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/Create_CW_MetricsRole',
					'Handler'         : 'index.lambda_handler',
					'CodeSize'        : 674,
					'Description'     : 'A Lambda that will create CW Metrics on a scheduled basis',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-07T19:23:12.000+0000',
					'CodeSha256'      : 'UJo4+gH5c0/a1WobLUsxZ94YsPdIC79bO/v8fuxkwtc=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'c5416966-cb79-4f43-bea5-c0286ad1630c',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					}
				]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'us-west-2',
		'mocked_response': {
			'Functions': [
				{
					'FunctionName'    : 'Create_CW_Metrics',
					'FunctionArn'     : 'arn:aws:lambda:us-west-2:111122223333:function:Create_CW_Metrics',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/Create_CW_MetricsRole',
					'Handler'         : 'index.lambda_handler',
					'CodeSize'        : 674,
					'Description'     : 'A Lambda that will create CW Metrics on a scheduled basis',
					'Timeout'         : 3,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T17:03:16.000+0000',
					'CodeSha256'      : 'oawy0iWCmQk0hCy7/E5p9sv4x40Ydt2sVGuno/zwiuw=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : '4a4dbdc0-3ee9-4213-aaea-a831efc6bc44',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					}
				]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'us-east-2',
		'mocked_response': {
			'Functions': [
				{
					'FunctionName'    : 'UpdateCrossAccountIAM',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:UpdateCrossAccountIAM',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/adf-lambda-role',
					'Handler'         : 'enable_cross_account_access.lambda_handler',
					'CodeSize'        : 16141,
					'Description'     : 'ADF Lambda Function - EnableCrossAccountAccess',
					'Timeout'         : 900,
					'MemorySize'      : 1024,
					'LastModified'    : '2023-09-06T16:44:28.000+0000',
					'CodeSha256'      : 'YgXP/qmhV8xisT3UnKrMHUFlgDNrM5rcqphh+cGGDvY=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'KMS_KEY_ID'    : '54b48e47-0df6-4730-8077-37575b2152a0',
							'S3_BUCKET_NAME': 'adf-global-base-deployment-pipelinebucket-x5m8zmy1i1sc',
							'ADF_LOG_LEVEL' : 'INFO'
							}
						},
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : '242037fc-bfc8-4b87-8190-0a163f27be4a',
					'Layers'          : [
						{
							'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:shared_layer:1',
							'CodeSize': 85865
							}
						],
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'CheckPipelineStatus',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:CheckPipelineStatus',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/adf-lambda-role',
					'Handler'         : 'update_pipelines.lambda_handler',
					'CodeSize'        : 16141,
					'Description'     : 'ADF Lambda Function - CheckPipelineStatus',
					'Timeout'         : 120,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T16:44:28.000+0000',
					'CodeSha256'      : 'YgXP/qmhV8xisT3UnKrMHUFlgDNrM5rcqphh+cGGDvY=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'KMS_KEY_ID'    : '54b48e47-0df6-4730-8077-37575b2152a0',
							'S3_BUCKET_NAME': 'adf-global-base-deployment-pipelinebucket-x5m8zmy1i1sc',
							'ADF_LOG_LEVEL' : 'INFO'
							}
						},
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'e2ce6ebf-63e9-441d-84a6-d3c6619a157c',
					'Layers'          : [
						{
							'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:shared_layer:1',
							'CodeSize': 85865
							}
						],
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'PipelinesCreateInitialCommitFunction',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:PipelinesCreateInitialCommitFunction',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/adf-global-base-deploymen-InitialCommitHandlerRole-1E34VR3WCI8XG',
					'Handler'         : 'handler.lambda_handler',
					'CodeSize'        : 7048112,
					'Description'     : 'ADF Lambda Function - PipelinesCreateInitialCommitFunction',
					'Timeout'         : 300,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T16:44:28.000+0000',
					'CodeSha256'      : 'ZI5r8+iomRDZ3rUBBQYj8p9MMFkc0Pgg6hR1kk7QtvM=',
					'Version'         : '$LATEST',
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : 'd8eba506-0e28-4bab-9ffb-788683448210',
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					},
				{
					'FunctionName'    : 'SendSlackNotification',
					'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:SendSlackNotification',
					'Runtime'         : 'python3.9',
					'Role'            : 'arn:aws:iam::111122223333:role/adf-lambda-role',
					'Handler'         : 'slack.lambda_handler',
					'CodeSize'        : 16141,
					'Description'     : 'ADF Lambda Function - Send Slack Notification',
					'Timeout'         : 10,
					'MemorySize'      : 128,
					'LastModified'    : '2023-09-06T16:44:28.000+0000',
					'CodeSha256'      : 'YgXP/qmhV8xisT3UnKrMHUFlgDNrM5rcqphh+cGGDvY=',
					'Version'         : '$LATEST',
					'Environment'     : {
						'Variables': {
							'ADF_PIPELINE_PREFIX': 'adf-pipeline-',
							'ADF_LOG_LEVEL'      : 'INFO'
							}
						},
					'TracingConfig'   : {
						'Mode': 'PassThrough'
						},
					'RevisionId'      : '52d17768-98a6-4645-acb3-4152ea94eb05',
					'Layers'          : [
						{
							'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:shared_layer:1',
							'CodeSize': 85865
							}
						],
					'PackageType'     : 'Zip',
					'Architectures'   : [
						'x86_64'
						],
					'EphemeralStorage': {
						'Size': 512
						},
					'SnapStart'       : {
						'ApplyOn'           : 'None',
						'OptimizationStatus': 'Off'
						}
					}
				]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'eu-central-1',
		'mocked_response': {'Functions': [
			{
				'FunctionName'    : 'FixRogueSG',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:FixRogueSG',
				'Runtime'         : 'python3.8',
				'Role'            : 'arn:aws:iam::111122223333:role/FixRogueSGRole',
				'Handler'         : 'lambda_function.lambda_handler',
				'CodeSize'        : 3683,
				'Description'     : 'This function finds and remediates unwanted open Security Groups',
				'Timeout'         : 60,
				'MemorySize'      : 128,
				'LastModified'    : '2021-02-18T00:20:49.838+0000',
				'CodeSha256'      : 'qKuJuyHhubBQ5/CjtwhKPIiBtmm93fAhQ3Bkna+ZTV4=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'badcidr' : '0.0.0.0/0',
						'DryRun'  : 'false',
						'SNSTopic': 'arn:aws:sns:us-east-1:111122223333:OpenSG-Updated',
						'LogLevel': 'INFO'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'cfa69c09-2a79-4c94-a6e0-1b233a281a0e',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				}
			]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'eu-north-1',
		'mocked_response': {'Functions': [
			{
				'FunctionName'    : 'LandingZoneGuardDutyNotificationForwarder',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:LandingZoneGuardDutyNotificationForwarder',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/StackSet-AWS-Landing-Zone-ForwardSnsNotificationLa-1XDDEMJLM5D3V',
				'Handler'         : 'index.lambda_handler',
				'CodeSize'        : 449,
				'Description'     : 'AWS Landing Zone SNS message forwarding function for aggregating GuardDuty notifications.',
				'Timeout'         : 60,
				'MemorySize'      : 128,
				'LastModified'    : '2023-09-06T16:44:28.000+0000',
				'CodeSha256'      : 'Idy/BLkIMTQXmBP7KKF925spvEwvNfHzYRvjQgG/Qvo=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'sns_arn': 'arn:aws:sns:us-east-1:111122223333:AWS-Landing-Zone-Aggregate-Security-Notifications'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'b8e1386c-4952-4cd9-b728-3192d326cdff',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				}
			]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'eu-west-2',
		'mocked_response': {'Functions': [
			{
				'FunctionName'    : 'Create_CW_Metrics',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:Create_CW_Metrics',
				'Runtime'         : 'python3.8',
				'Role'            : 'arn:aws:iam::111122223333:role/Create_CW_MetricsRole',
				'Handler'         : 'index.lambda_handler',
				'CodeSize'        : 674,
				'Description'     : 'A Lambda that will create CW Metrics on a scheduled basis',
				'Timeout'         : 3,
				'MemorySize'      : 128,
				'LastModified'    : '2023-09-06T17:02:42.000+0000',
				'CodeSha256'      : '6POPE8gLVb0uEDhso9QBwqnA4M1BPXHl+AAEm6skvvc=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '402e6eb2-daed-4bd9-889d-b59372b6d33d',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				}
			]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'ap-south-1',
		'mocked_response': {'Functions': [
			{
				'FunctionName'    : 'aws-perspective-CleanupBucketFunction-OVD656MF7UGS',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:aws-perspective-CleanupBucketFunction-OVD656MF7UGS',
				'Runtime'         : 'python3.8',
				'Role'            : 'arn:aws:iam::111122223333:role/aws-perspective-CleanupBucketFunctionRole-1RMMRZIDYZGDC',
				'Handler'         : 'cleanup_bucket.handler',
				'CodeSize'        : 8739685,
				'Description'     : 'Custom Lambda resource for emptying S3 buckets on stack deletion',
				'Timeout'         : 900,
				'MemorySize'      : 128,
				'LastModified'    : '2020-11-20T18:08:50.108+0000',
				'CodeSha256'      : 'bSvNEY11c9BJwbDu8CWhAsD6mlScygSDkPUCvrx1iQg=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'VERSION': '1.0'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '78f6c15d-33ad-46e0-a969-06347872c087',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'Service-Catalog-Factory-StartInstallLambda-1G5SWLOMPKBJV',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:Service-Catalog-Factory-StartInstallLambda-1G5SWLOMPKBJV',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/servicecatalog-factory/StartFactoryInstallRole',
				'Handler'         : 'index.handler',
				'CodeSize'        : 950,
				'Description'     : 'Lambda for starting Factory CodeBuild Job',
				'Timeout'         : 900,
				'MemorySize'      : 128,
				'LastModified'    : '2023-09-06T16:44:28.000+0000',
				'CodeSha256'      : 'bTm2hPFMB+4kZ5krm5sgIyf6Ye0prQfPeu/TWnHsyMs=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '15888c75-70d6-4205-a642-8eb0d81c0399',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'UpsertDNSNameFromCentralQueueLambda',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:UpsertDNSNameFromCentralQueueLambda',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/ReadQueueAndInsertRecordLambdaRole',
				'Handler'         : 'Route53PHZLambdaUpdateFromSQS.lambda_handler',
				'CodeSize'        : 1588,
				'Description'     : 'Lambda to to update DNS Hosted Zone for EC2 starts',
				'Timeout'         : 20,
				'MemorySize'      : 256,
				'LastModified'    : '2023-02-04T01:22:58.307+0000',
				'CodeSha256'      : '4CAgGZsVB+IiGAlH7+hpUBhg4kczTcU8fR2Scc8/Qnk=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'HOSTED_ZONE_ID': 'Z06954483PM26JFJ0ET4L',
						'LOG_LEVEL'     : 'INFO'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'd82459b2-8fa8-41e8-a842-5484d144755a',
				'Layers'          : [
					{
						'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:CentralBoto3Library:1',
						'CodeSize': 12119917
						}
					],
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'puppet-initialization-stack-StartInstallLambda-1HOFEXKEJ59NO',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:puppet-initialization-stack-StartInstallLambda-1HOFEXKEJ59NO',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/servicecatalog-puppet/StartPuppetInstallRole',
				'Handler'         : 'index.handler',
				'CodeSize'        : 950,
				'Description'     : 'Lambda for starting Puppet CodeBuild Job',
				'Timeout'         : 900,
				'MemorySize'      : 128,
				'LastModified'    : '2023-09-06T16:44:28.000+0000',
				'CodeSha256'      : 'EM64/ein7tutFhlnadFsmZgemV55QCbwxKLYvxY5IT8=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '49c3f461-70c8-4104-aa04-c9837a7bb2c4',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'aws-perspective-444444444444-PerspectiveCostLambda-WI000XT4UESL',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:aws-perspective-444444444444-PerspectiveCostLambda-WI000XT4UESL',
				'Runtime'         : 'nodejs12.x',
				'Role'            : 'arn:aws:iam::111122223333:role/aws-perspective-444444444444-u-PerspectiveCostRole-CRI7RCP68JB8',
				'Handler'         : 'costParser.handler',
				'CodeSize'        : 542111,
				'Description'     : '',
				'Timeout'         : 600,
				'MemorySize'      : 3008,
				'LastModified'    : '2020-11-20T18:22:45.622+0000',
				'CodeSha256'      : 'VUEyOf479zbGHCuWE3mIziOT7VAM1zKteXtKdr1uS2Y=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'DynamoCostTable': 'aws-perspective-444444444444-us-east-1-CostAndUsage-102XQ0DR9RGNL-PerspectiveCostDBTable-140FMMWXZJMF8'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '84c22e96-d9d7-4c99-8141-36de2c9b2788',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'aws-perspective-LambdaSetup-XVRTM8O9Z664',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:aws-perspective-LambdaSetup-XVRTM8O9Z664',
				'Runtime'         : 'nodejs12.x',
				'Role'            : 'arn:aws:iam::111122223333:role/aws-perspective-LambdaExecutionRole-1N5A6ABWHD3R5',
				'Handler'         : 'index.handler',
				'CodeSize'        : 8426320,
				'Description'     : 'Custom Lambda resource for the Perspective Cloudformation Stack',
				'Timeout'         : 900,
				'MemorySize'      : 256,
				'LastModified'    : '2020-11-20T18:09:09.002+0000',
				'CodeSha256'      : 'RsEPUZi7qMfo0qbyLqj23ZMNEuA/Mxjp608Q+myXDWM=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'APPSYNC_API_ARN'                : 'arn:aws:appsync:us-east-1:111122223333:apis/er5ovzqoxzgerkyzdegvedw5c4',
						'API_GATEWAY'                    : 'https://c4v9hpopf7.execute-api.us-east-1.amazonaws.com/Prod',
						'ACCOUNT_ID'                     : '444444444444',
						'IMAGE_VERSION'                  : 'aws-perspective-9',
						'COGNITO_IDENTITY_POOL'          : 'us-east-1:a0a7678a-1a47-4624-99ee-fcbd2b58db37',
						'AMPLIFY_STORAGE_BUCKET'         : 'aws-perspective-amplifystoragebucket-1396hpmwj23ce',
						'CREATE_READ_REPLICA'            : 'No',
						'EXISTING_CONFIG'                : 'Yes',
						'DEPLOYMENT_BUCKET'              : 'solutions-us-east-1',
						'ACCESS_LOGS'                    : 'aws-perspective-accesslogsbucket-2c037k0cbson',
						'COGNITO_USER_POOL_WEB_CLIENT_ID': '7mo4b172nsaknbmrmbp5uk688i',
						'NEPTUNE_INSTANCE_CLASS'         : 'db.r5.large',
						'APPSYNC_API_ID'                 : 'er5ovzqoxzgerkyzdegvedw5c4',
						'CREATE_ES_SERVICE_ROLE'         : 'Yes',
						'DISCOVERY_ARN'                  : 'arn:aws:iam::111122223333:role/aws-perspective-PerspectiveDiscoveryRole-4WRCUSFIC57L',
						'COGNITO_USER_POOL_ID'           : 'us-east-1_Smd5UZGpA',
						'SERVER_API_GATEWAY'             : 'https://u0hehot23d.execute-api.us-east-1.amazonaws.com/Prod/',
						'REGION'                         : 'us-east-1',
						'APPSYNC_API_GRAPHQL_URL'        : 'https://fg2svcng4vhzfiqmcntcshzx74.appsync-api.us-east-1.amazonaws.com/graphql',
						'DRAWIO_API_GATEWAY'             : 'https://4zj2y1f819.execute-api.us-east-1.amazonaws.com/Prod/',
						'CONFIG_AGGREGATOR'              : 'aws-perspective-us-east-1-444444444444-aggregator',
						'VERSION'                        : '1.0',
						'ANONYMOUS_METRIC_OPT_OUT'       : 'No',
						'DEPLOYMENT_BUCKET_KEY'          : 'aws-perspective/v1.0.1',
						'DISCOVERY_BUCKET'               : 'aws-perspective-discoverybucket-qjlwypzo5eg1',
						'WEBUI_BUCKET'                   : 'aws-perspective-webuibucket-1xylrsdi5wwn2'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '139255c9-441e-4b20-8539-14b004e1e206',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'HostedZone',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:HostedZone',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/HostedZoneInsertRecordLambdaRole-us-east-1',
				'Handler'         : 'index.lambda_handler',
				'CodeSize'        : 1491,
				'Description'     : 'Lambda to to update DNS Hosted Zone for EC2 starts.',
				'Timeout'         : 300,
				'MemorySize'      : 256,
				'LastModified'    : '2023-09-06T16:44:28.000+0000',
				'CodeSha256'      : 'aIwcVl+3PQeHKi3MUZb+RuCgXWPRCe+K2vfCTVhFjr0=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'HOSTED_ZONE_ID': 'Z2J1SZB1XTWUJO',
						'LOG_LEVEL'     : 'INFO'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'd587b479-9327-491a-9073-dec709c1b4a1',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'aws-perspective-444444444444-DrawIOExportFunction-18FOVGK1O4NA0',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:aws-perspective-444444444444-DrawIOExportFunction-18FOVGK1O4NA0',
				'Runtime'         : 'python3.8',
				'Role'            : 'arn:aws:iam::111122223333:role/aws-perspective-073323372-DrawIOExportFunctionRole-5B4KIP43PXJ1',
				'Handler'         : 'main.handler',
				'CodeSize'        : 3687,
				'Description'     : 'Converts cytoscape JSON to a Draw IO URL',
				'Timeout'         : 5,
				'MemorySize'      : 256,
				'LastModified'    : '2020-11-20T18:22:05.714+0000',
				'CodeSha256'      : 'bbd5/t5Liymrhn4tCUWI4VV+TzYpayvH49SC/lk3UYA=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'df5e70fb-a745-40a4-9e87-b91b3e58974e',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'UpsertDNSNameLambda',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:UpsertDNSNameLambda',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/UpsertDNSNameToSQSQueueLambdaRole',
				'Handler'         : 'Route53PHZLambdaUpdate.lambda_handler',
				'CodeSize'        : 2164,
				'Description'     : 'Lambda to to update DNS Hosted Zone for EC2 starts',
				'Timeout'         : 20,
				'MemorySize'      : 256,
				'LastModified'    : '2023-02-04T02:27:19.108+0000',
				'CodeSha256'      : 'RC3e1d8z3DRLwxRK32sVJ+VoPpsBCRNZLPWzKLgqoHE=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'HOSTED_ZONE_ID': 'Z06954483PM26JFJ0ET4L',
						'CENTRAL_ACCT'  : '444444444444',
						'QUEUE_NAME'    : 'myDNSUpsertQueue',
						'TIME_TO_LIVE'  : '300',
						'LOG_LEVEL'     : 'INFO'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'bb7c57a0-6d00-4e4a-809c-95f24c273f70',
				'Layers'          : [
					{
						'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:DistributedBoto3Library:1',
						'CodeSize': 12119917
						}
					],
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				}
			]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'il-central-1',
		'mocked_response': {'Functions': [
			{
				'FunctionName'    : 'amplify-login-custom-message-5e485fcf',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:amplify-login-custom-message-5e485fcf',
				'Runtime'         : 'nodejs12.x',
				'Role'            : 'arn:aws:iam::111122223333:role/amplify-login-lambda-5e485fcf',
				'Handler'         : 'index.handler',
				'CodeSize'        : 2256,
				'Description'     : '',
				'Timeout'         : 15,
				'MemorySize'      : 256,
				'LastModified'    : '2022-02-24T17:48:51.449+0000',
				'CodeSha256'      : 'CVYd49nBtCF35xpP9NBL6L7MCPAxrspnQ13ddPEXT9Q=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '2808976d-75cc-4103-aa40-a0356b9b0953',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'amplify-login-verify-auth-challenge-5e485fcf',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:amplify-login-verify-auth-challenge-5e485fcf',
				'Runtime'         : 'nodejs12.x',
				'Role'            : 'arn:aws:iam::111122223333:role/amplify-login-lambda-5e485fcf',
				'Handler'         : 'index.handler',
				'CodeSize'        : 2559,
				'Description'     : '',
				'Timeout'         : 15,
				'MemorySize'      : 256,
				'LastModified'    : '2022-02-24T17:51:39.000+0000',
				'CodeSha256'      : 'qsFlXXjffUdlFhVBVyhe0Cp1R+MZvVmTugVpU6YzFlg=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'ENDPOINT': 'https://amplifybackend.us-east-1.amazonaws.com'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '5926189a-f77b-41e8-ae85-5e45907a3eec',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'amplify-login-create-auth-challenge-5e485fcf',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:amplify-login-create-auth-challenge-5e485fcf',
				'Runtime'         : 'nodejs12.x',
				'Role'            : 'arn:aws:iam::111122223333:role/amplify-login-lambda-5e485fcf',
				'Handler'         : 'index.handler',
				'CodeSize'        : 1176,
				'Description'     : '',
				'Timeout'         : 15,
				'MemorySize'      : 256,
				'LastModified'    : '2022-02-24T17:48:51.405+0000',
				'CodeSha256'      : 'cxqJx8dz/lhOW3wipOg/XdcHXrdt3DYACxcHn4PxSUM=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '6679dcef-6683-46be-968e-358e02f60aba',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'UpsertDNSNameLambda',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:UpsertDNSNameLambda',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/UpsertDNSNameToSQSQueueLambdaRole',
				'Handler'         : 'Route53PHZLambdaUpdate.lambda_handler',
				'CodeSize'        : 2164,
				'Description'     : 'Lambda to to update DNS Hosted Zone for EC2 starts',
				'Timeout'         : 20,
				'MemorySize'      : 256,
				'LastModified'    : '2023-02-04T02:27:13.213+0000',
				'CodeSha256'      : 'RC3e1d8z3DRLwxRK32sVJ+VoPpsBCRNZLPWzKLgqoHE=',
				'Version'         : '$LATEST',
				'Environment'     : {
					'Variables': {
						'HOSTED_ZONE_ID': 'Z06954483PM26JFJ0ET4L',
						'CENTRAL_ACCT'  : '444444444444',
						'QUEUE_NAME'    : 'myDNSUpsertQueue',
						'TIME_TO_LIVE'  : '300',
						'LOG_LEVEL'     : 'INFO'
						}
					},
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'ee442990-2ae2-48af-864b-b56673ae9e47',
				'Layers'          : [
					{
						'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:DistributedBoto3Library:2',
						'CodeSize': 12119917
						}
					],
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				},
			{
				'FunctionName'    : 'amplify-login-define-auth-challenge-5e485fcf',
				'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:amplify-login-define-auth-challenge-5e485fcf',
				'Runtime'         : 'nodejs12.x',
				'Role'            : 'arn:aws:iam::111122223333:role/amplify-login-lambda-5e485fcf',
				'Handler'         : 'index.handler',
				'CodeSize'        : 1770,
				'Description'     : '',
				'Timeout'         : 15,
				'MemorySize'      : 256,
				'LastModified'    : '2022-02-24T17:48:51.355+0000',
				'CodeSha256'      : 'AKie0bn94HCWMRXS7Vm/vvQj9o0yLo6Co5x+iLWmXMs=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : '3146106e-59e1-4504-b113-ee532f3e6273',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				}
			]}
		},
	{
		'Account'        : '111122223333',
		'Region'         : 'af-south-1',
		'mocked_response': {'Functions': [
			{
				'FunctionName'    : 'Create_CW_Metrics',
				'FunctionArn'     : 'arn:aws:lambda:us-east-2:111122223333:function:Create_CW_Metrics',
				'Runtime'         : 'python3.9',
				'Role'            : 'arn:aws:iam::111122223333:role/Create_CW_MetricsRole',
				'Handler'         : 'index.lambda_handler',
				'CodeSize'        : 674,
				'Description'     : 'A Lambda that will create CW Metrics on a scheduled basis',
				'Timeout'         : 3,
				'MemorySize'      : 128,
				'LastModified'    : '2023-09-06T17:03:16.000+0000',
				'CodeSha256'      : 'j5kjegM5DVh/rsE9d22tHzaUOWJJrZrlW7jzMpvVAA0=',
				'Version'         : '$LATEST',
				'TracingConfig'   : {
					'Mode': 'PassThrough'
					},
				'RevisionId'      : 'd62b2adb-dde6-48a8-b63c-4e760ea9dc86',
				'PackageType'     : 'Zip',
				'Architectures'   : [
					'x86_64'
					],
				'EphemeralStorage': {
					'Size': 512
					},
				'SnapStart'       : {
					'ApplyOn'           : 'None',
					'OptimizationStatus': 'Off'
					}
				}
			]}
		},
	]
function_response_data = {
	'Functions': [
		{
			'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyValidate-tziul2Otm32F',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyValidate-tziul2Otm32F',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-ValidateSpokeAccountAccess',
			'Handler'         : 'resource_based_policy/step_functions_lambda/validate_account_access.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 900,
			'MemorySize'      : 1024,
			'LastModified'    : '2023-04-14T15:01:53.312+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'SPOKE_ROLE_NAME'        : 'paulbaye-us-east-1-AccountAssessment-Spoke-ExecutionRole',
					'POWERTOOLS_SERVICE_NAME': 'ScanResourceBasedPolicy',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'TIME_TO_LIVE_IN_DAYS'   : '90',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
					'LOG_LEVEL'              : 'INFO',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '6e9ec792-08c6-491d-aa19-aad57aeab78d',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-TrustedAccessStartScan70308-LfEGZM07HEP6',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-TrustedAccessStartScan70308-LfEGZM07HEP6',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-TrustedAccess',
			'Handler'         : 'trusted_access_enabled_services/scan_for_trusted_services.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 120,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:53.914+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME' : 'ScanTrustedAccess',
					'SEND_ANONYMOUS_DATA'     : 'Yes',
					'ORG_MANAGEMENT_ROLE_NAME': 'paulbaye-us-east-1-AccountAssessment-OrgMgmtStackRole',
					'TIME_TO_LIVE_IN_DAYS'    : '90',
					'STACK_ID'                : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'              : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'         : 'AccountAssessmentStack-TrustedAccessTable495B447A-GTR0RYDUJU5Q',
					'LOG_LEVEL'               : 'INFO',
					'SOLUTION_VERSION'        : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '943aca8c-3984-45cb-97ce-fd3e2a8f7c03',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'lock_down_stacks_sets_role',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:lock_down_stacks_sets_role',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/service-role/lock_down_stacks_sets_role-role-pgehgfag',
			'Handler'         : 'lambda_function.lambda_handler',
			'CodeSize'        : 299,
			'Description'     : '',
			'Timeout'         : 3,
			'MemorySize'      : 128,
			'LastModified'    : '2023-09-06T15:50:05.000+0000',
			'CodeSha256'      : 'fI06ZlRH/KN6Ra3twvdRllUYaxv182Tjx0qNWNlKIhI=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : 'ec0a7b23-c892-4dc8-935c-954bf6990bf5',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'PrintOutEvents_Function',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:PrintOutEvents_Function',
			'Runtime'         : 'python3.8',
			'Role'            : 'arn:aws:iam::111122223333:role/service-role/PrintOutEvents_Function-role-p29wwswh',
			'Handler'         : 'lambda_function.lambda_handler',
			'CodeSize'        : 309,
			'Description'     : '',
			'Timeout'         : 3,
			'MemorySize'      : 128,
			'LastModified'    : '2023-02-03T20:41:15.016+0000',
			'CodeSha256'      : 'O3OGwvaAIbPJr4rqhF1OZuuDThX1qcaCGGEekuse8OY=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : 'cfeb671f-f08d-4217-8263-b5110101baf9',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyFinishAs-n8TanL9sDr9r',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyFinishAs-n8TanL9sDr9r',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-ResourceBasedPolicyFinishAs-1RO9MOHKM92VA',
			'Handler'         : 'resource_based_policy/finish_scan.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 60,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:53.878+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME': 'FinishScanForResourceBasedPolicies',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'TIME_TO_LIVE_IN_DAYS'   : '90',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : 'e422e2e3-de5b-4a1d-b1f1-09b6125d230e',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-DelegatedAdminsStartScanE7D-Qk14ANSD75ay',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-DelegatedAdminsStartScanE7D-Qk14ANSD75ay',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-DelegatedAdmin',
			'Handler'         : 'delegated_admins/scan_for_delegated_admins.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 120,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:52.995+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME' : 'ScanDelegatedAdmin',
					'SEND_ANONYMOUS_DATA'     : 'Yes',
					'ORG_MANAGEMENT_ROLE_NAME': 'paulbaye-us-east-1-AccountAssessment-OrgMgmtStackRole',
					'TIME_TO_LIVE_IN_DAYS'    : '90',
					'STACK_ID'                : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'              : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'         : 'AccountAssessmentStack-DelegatedAdminsTable29E80916-F34FK4FZGFP5',
					'LOG_LEVEL'               : 'INFO',
					'SOLUTION_VERSION'        : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : 'd3fdc6a8-35b5-44b6-ae21-a533eea3f478',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'UpsertDNSNameLambda',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:UpsertDNSNameLambda',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/UpsertDNSNameToSQSQueueLambdaRole',
			'Handler'         : 'Route53PHZLambdaUpdate.lambda_handler',
			'CodeSize'        : 2164,
			'Description'     : 'Lambda to to update DNS Hosted Zone for EC2 starts',
			'Timeout'         : 20,
			'MemorySize'      : 256,
			'LastModified'    : '2023-02-04T02:25:54.603+0000',
			'CodeSha256'      : 'RC3e1d8z3DRLwxRK32sVJ+VoPpsBCRNZLPWzKLgqoHE=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'HOSTED_ZONE_ID': 'Z06954483PM26JFJ0ET4L',
					'CENTRAL_ACCT'  : '444444444444',
					'QUEUE_NAME'    : 'myDNSUpsertQueue',
					'TIME_TO_LIVE'  : '300',
					'LOG_LEVEL'     : 'INFO'
					}
				},
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : 'bbfc8a57-67de-426f-a63d-08996b688bd8',
			'Layers'          : [
				{
					'Arn'     : 'arn:aws:lambda:us-east-1:111122223333:layer:DistributedBoto3Library:9',
					'CodeSize': 12119917
					}
				],
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyScanSpok-xWlINDye4FUd',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyScanSpok-xWlINDye4FUd',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-ScanSpokeResource',
			'Handler'         : 'resource_based_policy/step_functions_lambda/scan_policy_all_services_router.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 900,
			'MemorySize'      : 512,
			'LastModified'    : '2023-04-14T15:01:54.774+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'SPOKE_ROLE_NAME'        : 'paulbaye-us-east-1-AccountAssessment-Spoke-ExecutionRole',
					'POWERTOOLS_SERVICE_NAME': 'ScanResourceBasedPolicyInSpokeAccount',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'TIME_TO_LIVE_IN_DAYS'   : '90',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
					'LOG_LEVEL'              : 'INFO',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '5d2d6891-e38f-4038-a5c6-fd0be145f34e',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'vpc-mappings-111122223333',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:vpc-mappings-111122223333',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AZ-Mapping-LambdaIAMRole-1MWVK82KVY9O5',
			'Handler'         : 'index.lambda_handler',
			'CodeSize'        : 1711,
			'Description'     : 'Stores VPC mappings into parameter store',
			'Timeout'         : 5,
			'MemorySize'      : 128,
			'LastModified'    : '2023-09-06T16:44:28.000+0000',
			'CodeSha256'      : 'H1vz9hfL3eHL/GigRMwy5E7ngxFl1XHzaSP5Dai3M8Y=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : '14153c9e-b5d0-4e0a-9d18-93868f7dd1ae',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyReadDC5D-4fhaK4485acJ',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyReadDC5D-4fhaK4485acJ',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-ResourceBasedPolicyReadServ-12WZ14XZFTC18',
			'Handler'         : 'resource_based_policy/read_resource_based_policies.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 60,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:53.924+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME': 'ReadResourceBasedPolicy',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : 'fe607630-2342-4d09-98d2-cee63552cb05',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'Fix_Default_SGs',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:Fix_Default_SGs',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/service-role/Fix_Default_SGs-role-qc5pamya',
			'Handler'         : 'lambda_function.lambda_handler',
			'CodeSize'        : 740,
			'Description'     : '',
			'Timeout'         : 3,
			'MemorySize'      : 128,
			'LastModified'    : '2023-09-06T16:33:20.000+0000',
			'CodeSha256'      : 'XZF1c2Xfl/YT+twYFVmlAGGuuNTO7i3J2FTCMoqFVew=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : 'c60151c0-f460-4dfe-98b5-47f6710447b8',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyStartSca-RU8utlGVjJyc',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyStartSca-RU8utlGVjJyc',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/paulbaye-us-east-1-ResourceBasedPolicy',
			'Handler'         : 'resource_based_policy/start_state_machine_execution_to_scan_services.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 120,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:02:10.418+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME'               : 'ScanResourceBasedPolicy',
					'SEND_ANONYMOUS_DATA'                   : 'Yes',
					'ORG_MANAGEMENT_ROLE_NAME'              : 'paulbaye-us-east-1-AccountAssessment-OrgMgmtStackRole',
					'SCAN_RESOURCE_POLICY_STATE_MACHINE_ARN': 'arn:aws:states:us-east-1:111122223333:stateMachine:ResourceBasedPolicyScanAllSpokeAccounts38C6FB6E-hEkgjewVuwLc',
					'TIME_TO_LIVE_IN_DAYS'                  : '90',
					'STACK_ID'                              : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'                            : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'                       : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
					'LOG_LEVEL'                             : 'INFO',
					'SOLUTION_VERSION'                      : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '4d80914c-9423-435d-b1fe-d48125ea064d',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-ResourceBasedPolicyReadScan-DbzA0NZGeTb3',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-ResourceBasedPolicyReadScan-DbzA0NZGeTb3',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-ResourceBasedPolicyReadScan-14UZV70G67KSO',
			'Handler'         : 'resource_based_policy/supported_configuration/scan_configurations.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 600,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:54.572+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME': 'ReadScanConfigs',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB',
					'LOG_LEVEL'              : 'INFO',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : 'b0f59e30-6d16-4368-80b2-27ed25d16d1e',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-WebUIDeployerDeployWebUIC2B-ZL1H4n2W05xe',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-WebUIDeployerDeployWebUIC2B-ZL1H4n2W05xe',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-WebUIDeployerDeployWebUISer-SXOS38SBZPWQ',
			'Handler'         : 'deploy_webui/deploy_webui.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 300,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:06:17.107+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'CONFIG'                 : '{"SrcBucket":"solutions-us-east-1","SrcPath":"account-assessment-for-aws-organizations/v1.0.3/webui/","WebUIBucket":"accountassessmentstack-s3bucket07682993-1qnr9dfvuvn8m","awsExports":{"API":{"endpoints":[{"name":"AccountAssessmentApi","endpoint":"https://5ugessads8.execute-api.us-east-1.amazonaws.com/prod"}]},"loggingLevel":"INFO","Auth":{"region":"us-east-1","userPoolId":"us-east-1_4y5EH6RX3","userPoolWebClientId":"10hrrgcdjum45c4jmre3kv7r7d","mandatorySignIn":true,"oauth":{"domain":"paulbaye-amzn.auth.us-east-1.amazoncognito.com","scope":["openid","profile","email","aws.cognito.signin.user.admin"],"redirectSignIn":"https://d12i33hlb8s7se.cloudfront.net/","redirectSignOut":"https://d12i33hlb8s7se.cloudfront.net/","responseType":"code","clientId":"10hrrgcdjum45c4jmre3kv7r7d"}}}}',
					'POWERTOOLS_SERVICE_NAME': 'DeployWebUI',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'LOG_LEVEL'              : 'INFO',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : 'b79766f8-4e8d-438c-a5b5-8d5e656a165e',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'orgformation-EmptyS3BucketOnDeletionLambdaFunction-W98Id8S5pK33',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:orgformation-EmptyS3BucketOnDeletionLambdaFunction-W98Id8S5pK33',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/orgformation-EmptyS3BucketOnDeletionLambdaExecutio-1SLZXRGG2YUT5',
			'Handler'         : 'index.handler',
			'CodeSize'        : 1412,
			'Description'     : '',
			'Timeout'         : 3,
			'MemorySize'      : 128,
			'LastModified'    : '2023-09-06T16:44:28.000+0000',
			'CodeSha256'      : 'kK3SVtC1I7ezvKPsNwno7YY9AfCKV3kkA56RV8kD3DE=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : 'c5d3cf2d-8a26-41d0-a0e8-60a36bca1103',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-JobHistoryJobsHandler060579-EShvGJzftPCt',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-JobHistoryJobsHandler060579-EShvGJzftPCt',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-JobHistoryJobsHandlerServic-HXRBGBPC98KW',
			'Handler'         : 'assessment_runner/api_router.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 60,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:53.918+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_LOGGER_LOG_EVENT': 'True',
					'POWERTOOLS_SERVICE_NAME'    : 'JobsApiHandler',
					'SEND_ANONYMOUS_DATA'        : 'Yes',
					'TABLE_TRUSTED_ACCESS'       : 'AccountAssessmentStack-TrustedAccessTable495B447A-GTR0RYDUJU5Q',
					'TABLE_DELEGATED_ADMIN'      : 'AccountAssessmentStack-DelegatedAdminsTable29E80916-F34FK4FZGFP5',
					'TIME_TO_LIVE_IN_DAYS'       : '90',
					'STACK_ID'                   : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'                 : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'SOLUTION_VERSION'           : 'v1.0.3',
					'TABLE_RESOURCE_BASED_POLICY': 'AccountAssessmentStack-ResourceBasedPolicyTable7277C643-13R1K510AXFDB'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '4ebd1e01-2898-4dab-8fb2-a42bad2bb1df',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'CreateidpProvider',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:CreateidpProvider',
			'Runtime'         : 'python2.7',
			'Role'            : 'arn:aws:iam::111122223333:role/service-role/CreateidpProvider-role-o7h6t6no',
			'Handler'         : 'lambda_function.lambda_handler',
			'CodeSize'        : 886,
			'Description'     : '',
			'Timeout'         : 3,
			'MemorySize'      : 128,
			'LastModified'    : '2019-05-02T15:03:42.436+0000',
			'CodeSha256'      : 'QvxbS4ZbI9bivuDn5kp7ARuHikbV5Xf3/SN3bKCcQdY=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : '42c3c4df-fe81-4dfd-9cd8-827a478407b7',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'P9E-a8ba4fea-1856-49ca-8aa4-2b7e9b58d7a6',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:P9E-a8ba4fea-1856-49ca-8aa4-2b7e9b58d7a6',
			'Runtime'         : 'python3.7',
			'Role'            : 'arn:aws:iam::111122223333:role/aws-perspective-51771365777-LambdaEdgeFunctionRole-15OZK21LEUC5O',
			'Handler'         : 'append_headers.handler',
			'CodeSize'        : 1039,
			'Description'     : 'Lambda@Edge for secure headers',
			'Timeout'         : 5,
			'MemorySize'      : 128,
			'LastModified'    : '2020-09-22T15:54:23.904+0000',
			'CodeSha256'      : 'tZMc1X5ewz2jkq2rML6VPQgb3x4T9wnYvnMacZHO65I=',
			'Version'         : '$LATEST',
			'TracingConfig'   : {
				'Mode': 'PassThrough'
				},
			'RevisionId'      : 'ffa243e9-dbe5-4424-970a-96ecfb5e4a3b',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-TrustedAccessRead96AB6071-NKktqhxZ7fTz',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-TrustedAccessRead96AB6071-NKktqhxZ7fTz',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-TrustedAccessReadServiceRol-1RC8YXWIAP9YN',
			'Handler'         : 'trusted_access_enabled_services/read_trusted_services.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 60,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:53.616+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME': 'ReadTrustedAccess',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-TrustedAccessTable495B447A-GTR0RYDUJU5Q',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '41db914e-32ea-4b7c-8a05-a78def9856b1',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			},
		{
			'FunctionName'    : 'AccountAssessmentStack-DelegatedAdminsRead591DCC7E-AyGSKEOHKNm2',
			'FunctionArn'     : 'arn:aws:lambda:us-east-1:111122223333:function:AccountAssessmentStack-DelegatedAdminsRead591DCC7E-AyGSKEOHKNm2',
			'Runtime'         : 'python3.9',
			'Role'            : 'arn:aws:iam::111122223333:role/AccountAssessmentStack-DelegatedAdminsReadServiceR-NA50GOH53141',
			'Handler'         : 'delegated_admins/read_delegated_admins.lambda_handler',
			'CodeSize'        : 17578832,
			'Description'     : '',
			'Timeout'         : 60,
			'MemorySize'      : 128,
			'LastModified'    : '2023-04-14T15:01:54.770+0000',
			'CodeSha256'      : 'W3RrpSLyvPWK2fMWGtTwyhNlX/MgiEmi4J4S56uv6qs=',
			'Version'         : '$LATEST',
			'Environment'     : {
				'Variables': {
					'POWERTOOLS_SERVICE_NAME': 'ReadDelegatedAdmin',
					'SEND_ANONYMOUS_DATA'    : 'Yes',
					'STACK_ID'               : 'arn:aws:cloudformation:us-east-1:111122223333:stack/AccountAssessmentStack/bc6befc0-dacb-11ed-921f-0a41af233cd7',
					'TABLE_JOBS'             : 'AccountAssessmentStack-JobHistoryTableE4B293DD-1QRBBBDKUU8G9',
					'COMPONENT_TABLE'        : 'AccountAssessmentStack-DelegatedAdminsTable29E80916-F34FK4FZGFP5',
					'SOLUTION_VERSION'       : 'v1.0.3'
					}
				},
			'TracingConfig'   : {
				'Mode': 'Active'
				},
			'RevisionId'      : '677f7ad5-f7d2-44d7-a3dd-c026e022b2fb',
			'PackageType'     : 'Zip',
			'Architectures'   : [
				'x86_64'
				],
			'EphemeralStorage': {
				'Size': 512
				},
			'SnapStart'       : {
				'ApplyOn'           : 'None',
				'OptimizationStatus': 'Off'
				}
			}
		]
	}

get_all_my_functions_test_result_dict = [
	{'operation_name': 'ListFunctions',
	 'test_result'   : account_and_region_specific_function_response_data}, ]

"""
all_my_orgs Test Data
"""
get_all_my_orgs_test_result_dict = [
	{'operation_name': 'DescribeRegions',
	 'test_result'   : DescribeRegionsResponseData},
	{'operation_name': 'GetCallerIdentity',
	 'test_result'   : GetCallerIdentity},
	{'operation_name': 'DescribeOrganization',
	 'test_result'   : DescribeOrganizationsResponseData},
	{'operation_name': 'ListAccounts',
	 'test_result'   : ListAccountsResponseData}]

"""
all_my_instances Test Data
"""
mock_instances_1 = {
	'Reservations': [
		{
			'Instances': [
				{
					'InstanceType'    : 't2.micro',
					'InstanceId'      : 'i-1234567890abcdef',
					"Placement"       : {"AvailabilityZone": "us-east-1b"},
					'PublicDnsName'   : 'ec2-1-2-3-4.us-east-1.compute.amazonaws.com',
					"PrivateIpAddress": "10.205.90.201",
					'State'           : {'Name': 'running'},
					'Tags'            : [{'Key': 'Name', 'Value': 'Instance1'},
					                     {'Key': 'Account', 'Value': '111122223333'}]
					}
				]
			}
		]
	}
mock_instances_2 = {
	'Reservations': [
		{
			"Instances": [
				{
					"InstanceId"      : "i-5f6e7d8e9b",
					"InstanceType"    : "m5.2xlarge",
					"Placement"       : {"AvailabilityZone": "us-east-2a"},
					"PublicIpAddress" : "98.76.54.32",
					"PrivateIpAddress": "10.0.5.6",
					"State"           : {"Name": "running"},
					'Tags'            : [{'Key': 'Name', 'Value': 'Instance1'},
					                     {'Key': 'Account', 'Value': '444455556666'},
					                     {"Key": "Environment", "Value": "Staging"}
					                     ]
					},
				{
					"InstanceId"      : "i-939fhik0jf",
					"InstanceType"    : "m5.4xlarge",
					"Placement"       : {"AvailabilityZone": "us-east-2b"},
					"PublicIpAddress" : "198.6.82.16",
					"PrivateIpAddress": "11.2.71.109",
					"State"           : {"Name": "running"},
					'Tags'            : [{'Key': 'Name', 'Value': 'Instance2'},
					                     {'Key': 'Account', 'Value': '444455556666'},
					                     {"Key": "Environment", "Value": "Development"}
					                     ]
					}
				]
			}
		]
	}
mock_instances_3 = {
	'Reservations': [
		{
			'Instances': [
				{
					"InstanceId"      : "i-5f6e7d8e9d",
					"InstanceType"    : "c5d.9xlarge",
					"Placement"       : {"AvailabilityZone": "us-west-2b"},
					"PublicIpAddress" : "22.23.24.25",
					'PublicDnsName'   : 'ec2-22-23-24-25.us-west-2.compute.amazonaws.com',
					"PrivateIpAddress": "10.0.9.1",
					"State"           : {"Name": "running"},
					"Tags"            : [{"Key": "Account", "Value": "555566667777"},
					                     {"Key": "Name", "Value": "Instance_3a"},
					                     {"Key": "Environment", "Value": "Production"},
					                     {"Key": "Project", "Value": "HighPerformanceComputing"}]
					}
				]
			}
		]
	}
mock_instances_4 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId": "i-0f1e2d3c4c", "InstanceType": "t3.small", "Placement": {"AvailabilityZone": "eu-west-1c"}, "PublicIpAddress": "54.123.45.69", "PrivateIpAddress": "10.0.0.6", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "555566667777"}, {"Key": "Name", "Value": "Instance_4a"}, {"Key": "Environment", "Value": "Production"}]},
			{"InstanceId": "i-5f6e7d8e9k", "InstanceType": "m5.2xlarge", "Placement": {"AvailabilityZone": "eu-west-1d"}, "PublicIpAddress": "34.56.78.92", "PrivateIpAddress": "10.0.1.9", "State": {"Name": "stopped"},
			 "Tags"      : [{"Key": "Account", "Value": "555566667777"}, {"Key": "Name", "Value": "Instance_4b"}, {"Key": "Environment", "Value": "Development"}]},
			{"InstanceId": "i-0a9b8c7d6h", "InstanceType": "t2.large", "Placement": {"AvailabilityZone": "eu-west-1c"}, "PublicIpAddress": "65.43.21.100", "PrivateIpAddress": "10.0.2.5", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "555566667777"}, {"Key": "Name", "Value": "Instance_4c"}, {"Key": "Project", "Value": "DataAnalytics"}]}]},
		]
	}
mock_instances_5 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId": "i-5f6e7d8e9l", "InstanceType": "c5.4xlarge", "Placement": {"AvailabilityZone": "eu-central-1a"}, "PublicIpAddress": "87.65.43.23", "PrivateIpAddress": "10.0.3.11", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "666677775555"}, {"Key": "Name", "Value": "Instance_5a"}, {"Key": "Environment", "Value": "Production"}, {"Key": "Project", "Value": "WebApplication"}]},
			{"InstanceId": "i-0a9b8c7d6i", "InstanceType": "r5.8xlarge", "Placement": {"AvailabilityZone": "eu-central-1b"}, "PublicIpAddress": "12.34.56.80", "PrivateIpAddress": "10.0.4.4", "State": {"Name": "stopped"},
			 "Tags"      : [{"Key": "Account", "Value": "666677775555"}, {"Key": "Name", "Value": "Instance_5b"}]}]},
		]
	}
mock_instances_6 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId": "i-5f6e7d8e9m", "InstanceType": "m5.8xlarge", "Placement": {"AvailabilityZone": "eu-north-1c"}, "PublicIpAddress": "98.76.54.34", "PrivateIpAddress": "10.0.5.8", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "777755556666"}, {"Key": "Name", "Value": "Instance_6a"}, {"Key": "Environment", "Value": "Staging"}]},
			{"InstanceId": "i-0a9b8c7d6j", "InstanceType": "t3.large", "Placement": {"AvailabilityZone": "eu-north-1c"}, "PublicIpAddress": "10.11.12.15", "PrivateIpAddress": "10.0.6.10", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "777755556666"}, {"Key": "Name", "Value": "Instance_6b"}, {"Key": "Project", "Value": "DataPipeline"}]},
			{"InstanceId": "i-5f6e7d8e9n", "InstanceType": "g4dn.4xlarge", "Placement": {"AvailabilityZone": "eu-north-1d"}, "PublicIpAddress": "14.15.16.19", "PrivateIpAddress": "10.0.7.7", "State": {"Name": "stopped"},
			 "Tags"      : [{"Key": "Account", "Value": "777755556666"}, {"Key": "Name", "Value": "Instance_6c"}]}]},

		]
	}
mock_instances_7 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId": "i-0a9b8c7d6k", "InstanceType": "m5a.2xlarge", "Placement": {"AvailabilityZone": "eu-west-2c"}, "PublicIpAddress": "18.19.20.23", "PrivateIpAddress": "10.0.8.5", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "777755556666"}, {"Key": "Name", "Value": "Instance_7a"}, {"Key": "Environment", "Value": "Production"}, {"Key": "Project", "Value": "MonitoringSystem"}]},
			{"InstanceId": "i-5f6e7d8e9o", "InstanceType": "c5d.18xlarge", "Placement": {"AvailabilityZone": "eu-west-2a"}, "PublicIpAddress": "22.23.24.27", "PrivateIpAddress": "10.0.9.3", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "777755556666"}, {"Key": "Name", "Value": "Instance_7b"}, {"Key": "Environment", "Value": "Production"}, {"Key": "Project", "Value": "HighPerformanceComputing"}]}]},

		]
	}
mock_instances_8 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId"      : "i-0f1e2d3c4d", "InstanceType": "t3.xlarge",
			 "Placement"       : {"AvailabilityZone": "ap-south-1d"},
			 "PublicIpAddress" : "54.123.45.70",
			 "PrivateIpAddress": "10.0.0.7",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "666677778888"},
			                      {"Key": "Name", "Value": "Instance_8a"},
			                      {"Key": "Environment", "Value": "Production"}]},
			{"InstanceId"      : "i-5f6e7d8e9p", "InstanceType": "m5.4xlarge",
			 "Placement"       : {"AvailabilityZone": "ap-south-1d"},
			 "PublicIpAddress" : "34.56.78.93",
			 "PrivateIpAddress": "10.0.1.10",
			 "State"           : {"Name": "stopped"},
			 "Tags"            : [{"Key": "Account", "Value": "666677778888"},
			                      {"Key": "Name", "Value": "Instance_8b"},
			                      {"Key": "Environment", "Value": "Development"}]},
			]}
		]
	}
mock_instances_9 = {
	'Reservations': [
		{
			"Instances": [
				{"InstanceId"      : "i-0f1e2d3c4b",
				 "InstanceType"    : "t3.micro",
				 "Placement"       : {"AvailabilityZone": "il-central-1a"},
				 "PublicIpAddress" : "54.123.45.68",
				 "PrivateIpAddress": "10.0.0.5",
				 "State"           : {"Name": "running"},
				 "Tags"            : [{"Key": "Account", "Value": "777788886666"},
				                      {"Key": "Name", "Value": "Instance_9a"},
				                      {"Key": "Environment", "Value": "Production"}]},
				{"InstanceId"      : "i-5f6e7d8e9e",
				 "InstanceType"    : "m5.xlarge",
				 "Placement"       : {"AvailabilityZone": "il-central-1a"},
				 "PublicIpAddress" : "34.56.78.91",
				 "PrivateIpAddress": "10.0.1.8",
				 "State"           : {"Name": "stopped"},
				 "Tags"            : [{"Key": "Account", "Value": "777788886666"},
				                      {"Key": "Name", "Value": "Instance_9b"},
				                      {"Key": "Environment", "Value": "Development"}]},
				{"InstanceId"      : "i-0a9b8c7d6f",
				 "InstanceType"    : "t2.medium",
				 "Placement"       : {"AvailabilityZone": "il-central-1a"},
				 "PublicIpAddress" : "65.43.21.99",
				 "PrivateIpAddress": "10.0.2.4",
				 "State"           : {"Name": "running"},
				 "Tags"            : [{"Key": "Account", "Value": "777788886666"},
				                      {"Key": "Name", "Value": "Instance_9c"},
				                      {"Key": "Project", "Value": "DataAnalytics"}]}]},
		]
	}
mock_instances_10 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId"      : "i-5f6e7d8e9f",
			 "InstanceType"    : "c5.2xlarge",
			 "Placement"       : {"AvailabilityZone": "af-south-1c"},
			 "PublicIpAddress" : "87.65.43.22",
			 "PrivateIpAddress": "10.0.3.10",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "888866667777"},
			                      {"Key": "Name", "Value": "Instance_10a"},
			                      {"Key": "Environment", "Value": "Production"},
			                      {"Key": "Project", "Value": "WebApplication"}]},
			{"InstanceId"      : "i-0a9b8c7d6g",
			 "InstanceType"    : "r5.4xlarge",
			 "Placement"       : {"AvailabilityZone": "af-south-1b"},
			 "PublicIpAddress" : "12.34.56.79",
			 "PrivateIpAddress": "10.0.4.3",
			 "State"           : {"Name": "stopped"},
			 "Tags"            : [{"Key": "Account", "Value": "888866667777"},
			                      {"Key": "Name", "Value": "Instance_10b"}]}]},
		]
	}
mock_instances_11 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId"      : "i-0a9b8c7d6i",
			 "InstanceType"    : "m5a.xlarge",
			 "Placement"       : {"AvailabilityZone": "us-east-2b"},
			 "PublicIpAddress" : "18.19.20.22",
			 "PrivateIpAddress": "10.0.8.4",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "111122223333"},
			                      {"Key": "Name", "Value": "Instance_11a"},
			                      {"Key": "Environment", "Value": "Production"},
			                      {"Key": "Project", "Value": "MonitoringSystem"}]},
			{"InstanceId"      : "i-5f6e7d8e9j",
			 "InstanceType"    : "c5d.12xlarge",
			 "Placement"       : {"AvailabilityZone": "us-east-2c"},
			 "PublicIpAddress" : "22.23.24.26",
			 "PrivateIpAddress": "10.0.9.2",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "111122223333"},
			                      {"Key": "Name", "Value": "Instance_11b"},
			                      {"Key": "Environment", "Value": "Production"},
			                      {"Key": "Project", "Value": "HighPerformanceComputing"}]}]},
		]
	}
mock_instances_12 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId"      : "i-5f6e7d8e9g",
			 "InstanceType"    : "m5.4xlarge",
			 "Placement"       : {"AvailabilityZone": "us-west-2b"},
			 "PublicIpAddress" : "98.76.54.33",
			 "PrivateIpAddress": "10.0.5.7",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "444455556666"},
			                      {"Key": "Name", "Value": "Instance_12q"},
			                      {"Key": "Environment", "Value": "Staging"}]},
			{"InstanceId"      : "i-0a9b8c7d6h",
			 "InstanceType"    : "t3.medium",
			 "Placement"       : {"AvailabilityZone": "us-west-2b"},
			 "PublicIpAddress" : "10.11.12.14",
			 "PrivateIpAddress": "10.0.6.9",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "444455556666"},
			                      {"Key": "Name", "Value": "Instance_12b"},
			                      {"Key": "Project", "Value": "DataPipeline"}]},
			{"InstanceId"      : "i-5f6e7d8e9i",
			 "InstanceType"    : "g4dn.2xlarge",
			 "Placement"       : {"AvailabilityZone": "us-west-2c"},
			 "PublicIpAddress" : "14.15.16.18",
			 "PrivateIpAddress": "10.0.7.6",
			 "State"           : {"Name": "stopped"},
			 "Tags"            : [{"Key": "Account", "Value": "444455556666"},
			                      {"Key": "Name", "Value": "Instance_12c"}]
			 }]},
		]
	}
mock_instances_13 = {
	'Reservations': [
		{
			"InstanceId"      : "i-0f1e2d3c4d",
			"InstanceType"    : "t3.xlarge",
			"Placement"       : {"AvailabilityZone": "me-south-1a"},
			"PublicIpAddress" : "54.123.45.70",
			"PrivateIpAddress": "10.0.0.7",
			"State"           : {"Name": "running"},
			"Tags"            : [{"Key": "Account", "Value": "555566667777"},
			                     {"Key": "Name", "Value": "Instance_13c"},
			                     {"Key": "Environment", "Value": "Production"}]
			}
		]
	}
mock_instances_14 = {
	'Reservations': [
		{
			'Instances': [
				{
					"InstanceId"      : "i-0a1b2c3d4e",
					"InstanceType"    : "t3.micro",
					"Placement"       : {"AvailabilityZone": "eu-central-1a"},
					"PublicIpAddress" : "54.123.45.67",
					"PrivateIpAddress": "10.0.0.4",
					"State"           : {"Name": "running"},
					"Tags"            : [{"Key": "Account", "Value": "555566667777"}, {"Key": "Name", "Value": "Instance_14c"}, {"Key": "Environment", "Value": "Production"}]
					},
				]
			}
		]
	}
mock_instances_15 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId": "i-0f1e2d3c4b", "InstanceType": "t3.micro", "Placement": {"AvailabilityZone": "eu-central-1b"}, "PublicIpAddress": "54.123.45.68", "PrivateIpAddress": "10.0.0.5", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "666677775555"}, {"Key": "Name", "Value": "Instance_15a"}, {"Key": "Environment", "Value": "Production"}]},
			{"InstanceId": "i-5f6e7d8e9e", "InstanceType": "m5.xlarge", "Placement": {"AvailabilityZone": "eu-central-1c"}, "PublicIpAddress": "34.56.78.91", "PrivateIpAddress": "10.0.1.8", "State": {"Name": "stopped"},
			 "Tags"      : [{"Key": "Account", "Value": "666677775555"}, {"Key": "Name", "Value": "Instance_15b"}, {"Key": "Environment", "Value": "Development"}]},
			{"InstanceId": "i-0a9b8c7d6f", "InstanceType": "t2.medium", "Placement": {"AvailabilityZone": "eu-central-1b"}, "PublicIpAddress": "65.43.21.99", "PrivateIpAddress": "10.0.2.4", "State": {"Name": "running"},
			 "Tags"      : [{"Key": "Account", "Value": "666677775555"}, {"Key": "Name", "Value": "Instance_15c"}, {"Key": "Project", "Value": "DataAnalytics"}]}]},

		]
	}
mock_instances_16 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId"      : "i-5f6e7d8e9g",
			 "InstanceType"    : "m5.4xlarge",
			 "Placement"       : {"AvailabilityZone": "af-south-1b"},
			 "PublicIpAddress" : "98.76.54.33",
			 "PrivateIpAddress": "10.0.5.7",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "777755556666"},
			                      {"Key": "Name", "Value": "Instance_16a"},
			                      {"Key": "Environment", "Value": "Staging"}]},
			{"InstanceId"      : "i-0a9b8c7d6h",
			 "InstanceType"    : "t3.medium",
			 "Placement"       : {"AvailabilityZone": "af-south-1b"},
			 "PublicIpAddress" : "10.11.12.14",
			 "PrivateIpAddress": "10.0.6.9",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "777755556666"},
			                      {"Key": "Name", "Value": "Instance_16b"},
			                      {"Key": "Project", "Value": "DataPipeline"}]},
			{"InstanceId"      : "i-5f6e7d8e9i",
			 "InstanceType"    : "g4dn.2xlarge",
			 "Placement"       : {"AvailabilityZone": "af-south-1c"},
			 "PublicIpAddress" : "14.15.16.18",
			 "PrivateIpAddress": "10.0.7.6",

			 "State"           : {"Name": "stopped"},
			 "Tags"            : [{"Key": "Account", "Value": "777755556666"},
			                      {"Key": "Name", "Value": "Instance_16c"}]}]},

		]
	}
mock_instances_17 = {
	'Reservations': [
		{"Instances": [
			{"InstanceId"      : "i-5f6e7d8e9f", "InstanceType": "c5.2xlarge",
			 "Placement"       : {"AvailabilityZone": "me-south-1c"},
			 "PublicIpAddress" : "87.65.43.22",
			 "PrivateIpAddress": "10.0.3.10",
			 "State"           : {"Name": "running"},
			 "Tags"            : [{"Key": "Account", "Value": "777755556666"},
			                      {"Key": "Name", "Value": "Instance_17c"},
			                      {"Key": "Environment", "Value": "Production"},
			                      {"Key": "Project", "Value": "WebApplication"}]},
			{"InstanceId"      : "i-0a9b8c7d6g", "InstanceType": "r5.4xlarge",
			 "Placement"       : {"AvailabilityZone": "me-south-1d"},
			 "PublicIpAddress" : "12.34.56.79",
			 "PrivateIpAddress": "10.0.4.3",
			 "State"           : {"Name": "stopped"},
			 "Tags"            : [{"Key": "Account", "Value": "777755556666"},
			                      {"Key": "Name", "Value": "Instance_17c"}]}]},

		]
	}
mock_instances_18 = {
	'Reservations': [
		{
			"Instances": [

				{
					"InstanceId"      : "i-5f6e7d8e9f",
					"InstanceType"    : "m5.large",
					"Placement"       : {"AvailabilityZone": "eu-west-1b"},
					"PublicIpAddress" : "34.56.78.90",
					"PrivateIpAddress": "10.0.1.7",
					"State"           : {"Name": "stopped"},
					"Tags"            : [{"Key": "Account", "Value": "666677778888"},
					                     {"Key": "Name", "Value": "Instance_18c"},
					                     {"Key": "Environment", "Value": "Development"}]
					},
				{
					"InstanceId"      : "i-0a9b8c7d6e",
					"InstanceType"    : "t2.small",
					"Placement"       : {"AvailabilityZone": "ap-southeast-1a"},
					"PublicIpAddress" : "65.43.21.98",
					"PrivateIpAddress": "10.0.2.3",
					"State"           : {"Name": "running"},
					"Tags"            : [{"Key": "Account", "Value": "666677778888"},
					                     {"Key": "Name", "Value": "Instance_18bc"},
					                     {"Key"  : "Project",
					                      "Value": "DataAnalytics"}]
					},
				{
					"InstanceId"      : "i-5f6e7d8e9a",
					"InstanceType"    : "c5.xlarge",
					"Placement"       : {"AvailabilityZone": "eu-west-1b"},
					"PublicIpAddress" : "87.65.43.21",
					"PrivateIpAddress": "10.0.3.9",
					"State"           : {"Name": "running"},
					"Tags"            : [{"Key": "Account", "Value": "666677778888"}, {"Key": "Name", "Value": "Instance_18a"},
					                     {"Key": "Environment", "Value": "Production"},
					                     {"Key": "Project", "Value": "WebApplication"}]
					},
				{
					"InstanceId"      : "i-0a9b8c7d6f",
					"InstanceType"    : "r5.2xlarge",
					"Placement"       : {"AvailabilityZone": "us-east-2c"},
					"PublicIpAddress" : "12.34.56.78",
					"PrivateIpAddress": "10.0.4.2",
					"State"           : {"Name": "stopped"},
					"Tags"            : [{"Key": "Account", "Value": "666677778888"},
					                     {"Key": "Name", "Value": "Instance_18d"}]
					}
				]
			},
		]
	}
mock_instances_19 = {'Reservations': []}
mock_instances_20 = {
	'Reservations': [
		{
			"Instances": [
				{
					"InstanceId"      : "i-5f6e7d8e9q",
					"InstanceType"    : "c5.8xlarge",
					"Placement"       : {"AvailabilityZone": "af-south-1e"},
					"PublicIpAddress" : "87.65.43.24",
					"PrivateIpAddress": "10.0.3.12",
					"State"           : {"Name": "running"},
					"Tags"            : [{"Key": "Account", "Value": "888866667777"},
					                     {"Key": "Name", "Value": "Instance_20d"},
					                     {"Key": "Environment", "Value": "Production"},
					                     {"Key": "Project", "Value": "WebApplication"}]
					},
				{
					"InstanceId"      : "i-0a9b8c7d6m",
					"InstanceType"    : "r5.12xlarge",
					"Placement"       : {"AvailabilityZone": "af-south-2a"},
					"PublicIpAddress" : "12.34.56.81",
					"PrivateIpAddress": "10.0.4.5",
					"State"           : {"Name": "stopped"},
					"Tags"            : [{"Key": "Account", "Value": "888866667777"},
					                     {"Key": "Name", "Value": "Instance_20a"}, ]
					}
				]
			}
		]
	}

All_Instances_Response_Data = [
	{'mock_profile' : 'mock_profile_1',
	 'AccountNumber': '111122223333',
	 'Region'       : 'us-east-1',
	 'instance_data': mock_instances_1},
	{'mock_profile' : 'mock_profile_2',
	 'AccountNumber': '444455556666',
	 'Region'       : 'us-east-2',
	 'instance_data': mock_instances_2},
	{'mock_profile' : 'mock_profile_3',
	 'AccountNumber': '555566667777',
	 'Region'       : 'us-west-2',
	 'instance_data': mock_instances_3},
	{'mock_profile' : 'mock_profile_4',
	 'AccountNumber': '555566667777',
	 'Region'       : 'eu-west-1',
	 'instance_data': mock_instances_4},
	{'mock_profile' : 'mock_profile_5',
	 'AccountNumber': '666677775555',
	 'Region'       : 'eu-central-1',
	 'instance_data': mock_instances_5},
	{'mock_profile' : 'mock_profile_6',
	 'AccountNumber': '777755556666',
	 'Region'       : 'eu-north-1',
	 'instance_data': mock_instances_6},
	{'mock_profile' : 'mock_profile_7',
	 'AccountNumber': '777755556666',
	 'Region'       : 'eu-west-2',
	 'instance_data': mock_instances_7},
	{'mock_profile' : 'mock_profile_8',
	 'AccountNumber': '666677778888',
	 'Region'       : 'ap-south-1',
	 'instance_data': mock_instances_8},
	{'mock_profile' : 'mock_profile_9',
	 'AccountNumber': '777788886666',
	 'Region'       : 'il-central-1',
	 'instance_data': mock_instances_9},
	{'mock_profile' : 'mock_profile_10',
	 'AccountNumber': '888866667777',
	 'Region'       : 'af-south-1',
	 'instance_data': mock_instances_10},
	{'mock_profile' : 'mock_profile_11',
	 'AccountNumber': '111122223333',
	 'Region'       : 'us-east-2',
	 'instance_data': mock_instances_11},
	{'mock_profile' : 'mock_profile_12',
	 'AccountNumber': '444455556666',
	 'Region'       : 'us-west-2',
	 'instance_data': mock_instances_12},
	{'mock_profile' : 'mock_profile_13',
	 'AccountNumber': '555566667777',
	 'Region'       : 'me-south-1',
	 'instance_data': mock_instances_13},
	{'mock_profile' : 'mock_profile_14',
	 'AccountNumber': '555566667777',
	 'Region'       : 'eu-central-1',
	 'instance_data': mock_instances_14},
	{'mock_profile' : 'mock_profile_15',
	 'AccountNumber': '666677775555',
	 'Region'       : 'eu-central-1',
	 'instance_data': mock_instances_15},
	{'mock_profile' : 'mock_profile_16',
	 'AccountNumber': '777755556666',
	 'Region'       : 'af-south-1',
	 'instance_data': mock_instances_16},
	{'mock_profile' : 'mock_profile_17',
	 'AccountNumber': '777755556666',
	 'Region'       : 'me-south-1',
	 'instance_data': mock_instances_17},
	{'mock_profile' : 'mock_profile_18',
	 'AccountNumber': '666677778888',
	 'Region'       : 'eu-west-1',
	 'instance_data': mock_instances_18},
	{'mock_profile' : 'mock_profile_19',
	 'AccountNumber': '777788886666',
	 'Region'       : 'us-east-1',
	 # mock_instance data will be empty
	 'instance_data': mock_instances_19},
	{'mock_profile' : 'mock_profile_20',
	 'AccountNumber': '888866667777',
	 'Region'       : 'af-south-1',
	 'instance_data': mock_instances_20},
	]
