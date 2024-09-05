import boto3
from account_class import aws_acct_access

sendgrid_api_key_arn = "some_name"
region_name = "us-east-1"
credentials = {'profile_name': 'LZ1'}


def do_stuff():
	# aws_acct = aws_acct_access()
	# session = boto3.session.Session(**credentials)
	# client = session.client(service_name="organizations", region_name=region_name)
	# response1 = client.list_accounts()
	# response2 = client.list_roots()
	# responsedict = {'response1': response1, 'response2': response2, 'response3': aws_acct}
	# # responsedict = {'response1': response1, 'response2': response2}
	# return responsedict
	print("Hello World")