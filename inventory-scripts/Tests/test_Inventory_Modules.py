import pytest

from common_test_data import cli_provided_parameters1, ListAccountsResponseData, GetCallerIdentity, DescribeRegionsResponseData, DescribeOrganizationsResponseData, AssumeRoleResponseData
from common_test_functions import _amend_make_api_call
from Inventory_Modules import get_all_credentials


get_all_credentials_test_result_dict = [
	{'operation_name': 'GetCallerIdentity',
	 'test_result'   : GetCallerIdentity},
	{'operation_name': 'DescribeOrganization',
	 'test_result'   : DescribeOrganizationsResponseData},
	{'operation_name': 'AssumeRole',
	 'test_result'   : AssumeRoleResponseData},
	{'operation_name': 'ListAccounts',
	 'test_result'   : ListAccountsResponseData},
	{'operation_name': 'DescribeRegions',
	 'test_result'   : DescribeRegionsResponseData}
]

# Skipped for now, since I know the get_credential testing needs more work
@pytest.mark.skip
@pytest.mark.parametrize(
	"parameters, test_value_dict",
	[
		(cli_provided_parameters1, get_all_credentials_test_result_dict),
	],
)
def test_get_all_credentials(parameters, test_value_dict, mocker):
	pProfiles = parameters['pProfiles']
	pRegionList = parameters['pRegionList']
	pSkipProfiles = parameters['pSkipProfiles']
	pSkipAccounts = parameters['pSkipAccounts']
	pAccountList = parameters['pAccountList']
	pTiming = parameters['pTiming']
	pRootOnly = parameters['pRootOnly']
	pRoleList = parameters['pRoleList']
	verbose = parameters['pverbose']
	test_data = {'FunctionName'   : 'get_all_credentials',
	             'AccountSpecific': True,
	             'RegionSpecific' : True
	             }
	_amend_make_api_call(test_data, test_value_dict, verbose, mocker)

	# if isinstance(test_value, Exception):
	# 	print("Expected Error...")
	# 	with pytest.raises(type(test_value)) as error:
	# 		get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccountList, pRegionList, pRoleList)
	# 	result = error
	# else:
	result = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccountList, pRegionList, pRoleList)
	for cred in result:
		assert cred['Success']
	print("Result:", result)

	return result
