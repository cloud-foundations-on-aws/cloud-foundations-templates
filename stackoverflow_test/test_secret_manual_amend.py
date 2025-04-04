import botocore
import json
import pytest
from datetime import datetime

from src import do_stuff, sendgrid_api_key_arn

def _amend_get_account_data(test_key, test_value, mocker):
	orig = botocore.client.BaseClient._make_api_call

	def amend_make_api_call(self, operation_name, kwargs):
		# Intercept boto3 operations for <secretsmanager.get_secret_value>. Optionally, you can also
		# check on the argument <SecretId> and control how you want the response would be. This is
		# a very flexible solution as you have full control over the whole process of fetching a
		# secret.
		if operation_name == 'ListAccounts':
			if isinstance(test_value, Exception):
				raise test_value
			# Implied break and exit of the function here...
			print(f"OperationName: {operation_name}\n"
			      f"Key Name: {test_key}\n"
			      f"kwargs: {kwargs}")
			# return test_value
			return test_value

		return_response = orig(self, operation_name, kwargs)
		print(f"OperationName: {operation_name}\n"
		      f"kwargs: {kwargs}")
		return return_response

	mocker.patch('botocore.client.BaseClient._make_api_call', new=amend_make_api_call)


list_accounts_test_data = {
	'Accounts' : [
		{
			'Id'             : '073323372301',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/073323372301',
			'Email'          : 'paulbaye+Demo1@amazon.com',
			'Name'           : 'Demo-Acct-1',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': datetime(2015, 1, 1)
		},
		{
			'Id'             : '517713657778',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/517713657778',
			'Email'          : 'paulbaye+LZRoot@amazon.com',
			'Name'           : 'LZRoot2',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': datetime(2018, 7, 19, 23, 32, 57, 676000, )
		},
		{
			'Id'             : '733277908732',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/733277908732',
			'Email'          : 'paulbaye+LZ2FSA@amazon.com',
			'Name'           : 'fsa-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-12-05T04:02:39.398000-05:00'
		},
		{
			'Id'             : '708614565779',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/708614565779',
			'Email'          : 'paulbaye+LZ_SS@amazon.com',
			'Name'           : 'shared-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-10-30T17:23:31.965000-04:00'
		},
		{
			'Id'             : '723919836827',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/723919836827',
			'Email'          : 'paulbaye+LZ_Demo3@amazon.com',
			'Name'           : 'Test-Demo3',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': '2020-09-08T18:32:01.416000-04:00'
		},
		{
			'Id'             : '574255301951',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/574255301951',
			'Email'          : 'paulbaye+LZ_Sec@amazon.com',
			'Name'           : 'security',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-10-30T17:12:14.078000-04:00'
		},
		{
			'Id'             : '858216852750',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/858216852750',
			'Email'          : 'paulbaye+LZ4-Log@amazon.com',
			'Name'           : 'logging',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': '2021-02-17T15:10:24.597000-05:00'
		},
		{
			'Id'             : '814274863958',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/814274863958',
			'Email'          : 'paulbaye+LZ2Sec@amazon.com',
			'Name'           : 'LZRoot/',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-07-19T23:33:04.281000-04:00'
		},
		{
			'Id'             : '268784212676',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/268784212676',
			'Email'          : 'paulbaye+LZ4-SS@amazon.com',
			'Name'           : 'shared-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'INVITED',
			'JoinedTimestamp': '2021-02-17T15:10:46.390000-05:00'
		},
		{
			'Id'             : '073323372301',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/073323372301',
			'Email'          : 'paulbaye+Demo1@amazon.com',
			'Name'           : 'Demo-Acct-1',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-12-04T00:37:35.851000-05:00'
		},
		{
			'Id'             : '938847804469',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/938847804469',
			'Email'          : 'paulbaye+LZ_Demo23@amazon.com',
			'Name'           : 'Test-Demo23',
			'Status'         : 'SUSPENDED',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2020-07-23T18:16:52.900000-04:00'
		},
		{
			'Id'             : '786463113543',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/786463113543',
			'Email'          : 'paulbaye+LZ_Log@amazon.com',
			'Name'           : 'logging',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-10-30T17:17:51.248000-04:00'
		},
		{
			'Id'             : '728530570730',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/728530570730',
			'Email'          : 'paulbaye+LZ2SS@amazon.com',
			'Name'           : 'shared-services',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-10-26T23:27:11.350000-04:00'
		},
		{
			'Id'             : '906348505515',
			'Arn'            : 'arn:aws:organizations::517713657778:account/o-ykfx0legmn/906348505515',
			'Email'          : 'paulbaye+Demo2@amazon.com',
			'Name'           : 'Demo2',
			'Status'         : 'ACTIVE',
			'JoinedMethod'   : 'CREATED',
			'JoinedTimestamp': '2018-12-04T10:15:06.149000-05:00'
		}
	],
	# 'NextToken': 'NextTokenString'
}


@pytest.mark.parametrize(
	'test_value',
	[
		list_accounts_test_data,
		# str(1993),
		# json.dumps({"SecretString": "my-secret"}),
		# json.dumps([2, 3, 5, 7, 11, 13, 17, 19]),
		# KeyError("How dare you touch my secret!"),
		# ValueError("Oh my goodness you even have the guts to repeat it!!!"),
	],
)
def test_get_account_data(test_value, mocker):
	_amend_get_account_data(sendgrid_api_key_arn, test_value, mocker)

	if isinstance(test_value, Exception):
		print("Expected Error...")
		with pytest.raises(type(test_value)) as error:
			do_stuff()
		result = error
	else:
		result = do_stuff()

	print("Result:", result)
