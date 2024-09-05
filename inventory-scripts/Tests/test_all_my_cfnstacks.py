import pytest
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from pprint import pprint

# Import the functions you want to test
from all_my_cfnstacks import parse_args, setup_auth_accounts_and_regions, collect_cfnstacks, display_stacks, modify_stacks


class TestScriptFunctions(unittest.TestCase):
	def setUp(self):
		# This is the parameters provided.
		self.mock_profile = 'mock_profile'
		self.mock_regions = ['us-east-1', 'us-west-1']
		self.fragments = ['Stack']
		self.accounts = ['123456789012', '234567890123']
		self.exact = False
		self.timing = True
		self.SkipAccounts = None
		self.SkipProfiles = None
		self.loglevel = 50
		self.status = None
		self.stackid = False
		self.rootonly = False
		self.deletionrun = False
		# This is the parameters that will be passed to the script
		self.mock_args = ['-p', self.mock_profile, '-rs', self.mock_regions, '--time', '-f', self.fragments]
		# This is the parameters that have been instantiated within the script, including default values
		self.expected_args = {
			# 'AccessRoles' : None,
			'Accounts'    : self.accounts,
			'DeletionRun' : self.deletionrun,
			'Exact'       : self.exact,
			'Fragments'   : self.fragments,
			'Profile'     : self.mock_profile,
			'Regions'     : self.mock_regions,
			'RootOnly'    : self.rootonly,
			'SkipAccounts': self.SkipAccounts,
			'SkipProfiles': self.SkipProfiles,
			'Time'        : self.timing,
			'loglevel'    : self.loglevel,
			'stackid'     : self.stackid,
			'status'      : self.status,

			# Add other expected arguments as needed
			}

	def test_parse_args(self):
		with patch('sys.argv', self.mock_args):
			args = parse_args(sys.argv)
			for arg, value in self.expected_args.items():
				self.assertEqual(getattr(args, arg), value)

	@patch('all_my_cfnstacks.aws_acct_access')
	@patch('all_my_cfnstacks.Inventory_Modules.get_regions3')
	# @patch('all_my_cfnstacks.Inventory_Modules.RemoveCoreAccounts')
	# def test_setup_auth_accounts_and_regions(self, mock_remove_core_accounts, mock_get_regions3, mock_aws_acct_access):
	def test_setup_auth_accounts_and_regions(self, mock_get_regions3, mock_aws_acct):
		# Set up mock objects and data
		mock_aws_acct_access = MagicMock()
		mock_aws_acct_access.ChildAccounts = [{'AccountId': '123456789012'}, {'AccountId': '234567890123'}]
		mock_aws_acct.return_value = mock_aws_acct_access
		# mock_aws_acct.ChildAccounts = [{'AccountId': '123456789012'}, {'AccountId': '234567890123'}]
		mock_get_regions3.return_value = ['us-east-1', 'us-west-1']
		# mock_remove_core_accounts.return_value =
		# mock_remove_core_accounts.side_effect = lambda accounts, skip_accounts: accounts

		# Call the function
		aws_acct, account_list, region_list = setup_auth_accounts_and_regions(self.mock_profile, mock_get_regions3, self.accounts, self.SkipAccounts, self.fragments, self.exact, self.deletionrun)

		# Assert the results
		self.assertEqual(aws_acct, mock_aws_acct.return_value)
		self.assertEqual(account_list, ['123456789012', '234567890123'])
		self.assertEqual(region_list, mock_get_regions3.return_value)

	@patch('all_my_cfnstacks.Inventory_Modules.find_stacks2')
	def test_collect_cfnstacks(self, mock_find_stacks2):
		# Set up mock data
		mock_credential_list = [
			{'AccountId': '123456789012', 'Region': 'us-east-1', 'Success': True},
			{'AccountId': '234567890123', 'Region': 'us-west-1', 'Success': False}
			]
		mock_stacks = [
			{'StackName': 'my-stack-1', 'StackStatus': 'CREATE_COMPLETE', 'StackId': 'arn:aws:cloudformation:...', 'CreationTime': '2023-04-01T00:00:00Z'},
			{'StackName': 'my-stack-2', 'StackStatus': 'UPDATE_IN_PROGRESS', 'StackId': 'arn:aws:cloudformation:...', 'CreationTime': '2023-04-02T00:00:00Z'}
			]
		mock_find_stacks2.return_value = mock_stacks

		# Call the function
		all_stacks = collect_cfnstacks(mock_credential_list)

		# Assert the results
		expected_stacks = [
			{'Account'        : '123456789012',
			 'Region'         : 'us-east-1',
			 'AccessKeyId'    : None,
			 'SecretAccessKey': None,
			 'SessionToken'   : None,
			 'AccountNumber'  : None,
			 'StackName'      : 'my-stack-1',
			 'StackCreate'    : None}]

	# Need some asserts here

	@patch('script.display_results')
	@patch('builtins.print')
	def test_display_stacks(self, mock_print, mock_display_results):
		global AccountList, RegionList
		AccountList = ['111111111111', '222222222222']
		RegionList = ['us-east-1', 'us-west-2']
		all_stacks = [
			{
				'Account'    : '111111111111',
				'Region'     : 'us-east-1',
				'StackStatus': 'CREATE_COMPLETE',
				'StackCreate': '2023-04-01',
				'StackName'  : 'stack1',
				'StackArn'   : 'arn:aws:cloudformation:us-east-1:111111111111:stack/stack1/abcd1234'
				},
			{
				'Account'    : '222222222222',
				'Region'     : 'us-west-2',
				'StackStatus': 'UPDATE_COMPLETE',
				'StackCreate': '2023-03-15',
				'StackName'  : 'stack2',
				'StackArn'   : 'arn:aws:cloudformation:us-west-2:222222222222:stack/stack2/efgh5678'
				}
			]

		display_stacks(all_stacks)

		mock_display_results.assert_called_once()
		expected_print_calls = [
			mock.call('\x1b[2K'),
			mock.call('\x1b[31mFound 2 stacks across 2 accounts across 2 regions\x1b[0m'),
			mock.call(),
			mock.call('The list of accounts and regions:'),
			mock.ANY  # Skipping the pprint call
			]
		mock_print.assert_has_calls(expected_print_calls)

	@patch('builtins.input', return_value='y')
	@patch('all_my_cfnstacks.Inventory_Modules.delete_stack2')
	def test_modify_stacks(self, mock_delete_stack2, mock_input):
		global pStackfrag, DeletionRun
		pStackfrag = 'my-stack'
		DeletionRun = True

		stack_found1 = {
			'Account'    : '111111111111',
			'Region'     : 'us-east-1',
			'StackName'  : 'stack1',
			'StackStatus': 'CREATE_COMPLETE'
			}
		stack_found2 = {
			'Account'    : '222222222222',
			'Region'     : 'us-west-2',
			'StackName'  : 'stack2',
			'StackStatus': 'DELETE_FAILED'
			}
		stacks_found = [stack_found1, stack_found2]

		mock_delete_stack2.side_effect = ['delete_response1', 'delete_response2']

		modify_result = modify_stacks(stacks_found)

		self.assertEqual(modify_result, ['delete_response1', 'delete_response2'])
		mock_input.assert_called_once_with('Deletion of stacks has been requested, are you still sure? (y/n): ')
		mock_delete_stack2.assert_any_call(stack_found1, 'us-east-1', 'stack1')
		mock_delete_stack2.assert_any_call(stack_found2, 'us-west-2', 'stack2', RetainResources=True, )


if __name__ == '__main__':
	unittest.main()
