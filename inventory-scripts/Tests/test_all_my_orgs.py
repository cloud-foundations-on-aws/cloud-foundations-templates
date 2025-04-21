from botocore import client
import pytest
from datetime import datetime

from all_my_orgs import all_my_orgs
from common_test_data import cli_provided_parameters1, cli_provided_parameters2, get_all_my_orgs_test_result_dict
from common_test_functions import _amend_make_api_call, _amend_make_api_call_orig, AWSAccount_from_AWSKeyID


@pytest.mark.parametrize(
	"parameters,test_value_dict",
	[
		(cli_provided_parameters1, get_all_my_orgs_test_result_dict),
		(cli_provided_parameters2, get_all_my_orgs_test_result_dict),
		# str(1993),
		# json.dumps({"SecretString": "my-secret"}),
		# json.dumps([2, 3, 5, 7, 11, 13, 17, 19]),
		# KeyError("How dare you touch my secret!"),
		# ValueError("Oh my goodness you even have the guts to repeat it!!!"),
	],
)
def test_get_account_data(parameters, test_value_dict, mocker):
	pProfiles = parameters['pProfiles']
	pSkipProfiles = parameters['pSkipProfiles']
	pAccountList = parameters['pAccountList']
	pTiming = parameters['pTiming']
	pRootOnly = parameters['pRootOnly']
	pSaveFilename = parameters['pSaveFilename']
	pShortform = parameters['pShortform']
	pverbose = parameters['pverbose']
	test_data = {'FunctionName'   : 'all_my_orgs',
	             'AccountSpecific': True,
	             'RegionSpecific' : True
	             }
	# _amend_make_api_call_orig(pProfiles[0], test_value, mocker)
	_amend_make_api_call(test_data, test_value_dict, pverbose, mocker)

	# if isinstance(test_value_dict, Exception):
	# 	print("Expected Error...")
	# 	with pytest.raises(type(test_value_dict)) as error:
	# 		all_my_orgs(pProfiles, pSkipProfiles, pAccountList, pTiming, pRootOnly, pSaveFilename, pShortform, pverbose)
	# 	result = error
	# else:

	# During the run of this test, the profile provided MUST match something real on the user's desktop,
	# otherwise the script thinks the profile is unmatched and doesn't try to use it.
	# In further testing, I'll have to figure out how to mock the session call, since it's not being caught by the "make_api_call" function...
	result = all_my_orgs(pProfiles, pSkipProfiles, pAccountList, pTiming, pRootOnly, pSaveFilename, pShortform, pverbose)

	print("Result:", result)
