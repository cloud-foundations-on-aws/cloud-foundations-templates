import pytest

from common_test_data import CredentialResponseData, get_all_my_functions_test_result_dict
from common_test_functions import _amend_make_api_call, _amend_create_boto3_session, _amend_make_api_call_specific
from all_my_functions import collect_all_my_functions, fix_my_functions

# CredentialList = test_get_all_credentials()
# This is what the response from the tested function should look like, given the parameters supplied

"""
Pass in the parameters as dictionary with operation names and what test results I should get back
"""
function_parameters = {
	'CredentialList': CredentialResponseData,
	'pFragments'    : ['python3.9', 'Metric'],
	'pverbose'      : 20
}


@pytest.mark.parametrize(
	"parameters, test_value_dict",
	[
		(function_parameters, get_all_my_functions_test_result_dict),
		# (RootOnlyParams, ),
		# str(1993),
		# json.dumps({"SecretString": "my-secret"}),
		# json.dumps([2, 3, 5, 7, 11, 13, 17, 19]),
		# KeyError("How dare you touch my secret!"),
		# ValueError("Oh my goodness you even have the guts to repeat it!!!"),
	],
)
def test_all_my_functions(parameters, test_value_dict, mocker):
	"""
	Description:
	@param parameters: the expected parameters into the function
	@param mocker: the mock object
	@return:
	"""
	CredentialList = parameters['CredentialList']
	pFragments = parameters['pFragments']
	verbose = parameters['pverbose']
	test_data = {'FunctionName'   : 'all_my_functions',
	             'AccountSpecific': True,
	             'RegionSpecific' : True
	             }
	# _amend_create_boto3_session(test_data, mocker)
	# pass
	# _amend_make_api_call(test_data, test_value_dict, mocker)
	_amend_make_api_call_specific(test_data, test_value_dict, mocker)

	# if isinstance(test_value, Exception):
	# 	print("Expected Error...")
	# 	with pytest.raises(type(test_value)) as error:
	# 		all_my_functions(CredentialList, pFragments, verbose)
	# 	result = error
	# else:
	result = collect_all_my_functions(CredentialList, pFragments, verbose)

	print("Result:", result)
	print()

'''
import boto3
from unittest.mock import patch, MagicMock


# Your application code
def get_lambda_functions():
	session = boto3.Session('LZ1', region_name='us-east-2')
	lambda_client = session.client('lambda')
	return lambda_client.list_functions()


# Your mock method
def mock_list_functions(*args, **kwargs):
	print("Inside the mocked function!")
	# Access the session info here (if it's passed or globally accessible)
	print()
	creds = args[1]['test'].get_credentials()
	return {'Functions': [{'FunctionName': 'mocked_function_1'}, {'FunctionName': 'mocked_function_2'}]}


# Your test code
def test_get_lambda_functions():
	with patch.object(boto3.Session, 'client') as mock_client:
		mock_lambda_client = MagicMock()
		addl_params = {'test': boto3.Session(), 'account': '11111'}
		mock_lambda_client.list_functions = mock_list_functions('lambda', addl_params)
		mock_client.return_value = mock_lambda_client

		result = get_lambda_functions()
		assert result == {'Functions': [{'FunctionName': 'mocked_function_1'}, {'FunctionName': 'mocked_function_2'}]}
'''