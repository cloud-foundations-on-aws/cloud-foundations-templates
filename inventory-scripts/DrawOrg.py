import sys
from os.path import split

import boto3
import logging
from graphviz import Digraph
from time import time
from colorama import init, Fore
from ArgumentsClass import CommonArguments

__version__ = '2024.10.29'

init()

account_fillcolor = 'orange'
suspended_account_fillcolor = 'red'
account_shape = 'ellipse'
policy_fillcolor = 'azure'  # Pretty color - nothing to do with the Azure Cloud...
policy_linecolor = 'red'
policy_shape = 'hexagon'
ou_fillcolor = 'burlywood'
ou_shape = 'box'
aws_policy_type_list = ['SERVICE_CONTROL_POLICY', 'TAG_POLICY', 'BACKUP_POLICY',
                        'AISERVICES_OPT_OUT_POLICY', 'CHATBOT_POLICY', 'RESOURCE_CONTROL_POLICY']


#####################
# Function Definitions
#####################


def parse_args(f_args):
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.my_parser.description = "To draw the Organization and its policies."
	parser.singleprofile()
	parser.verbosity()
	parser.timing()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--policy",
		dest='policy',
		action="store_true",
		help="Include the various policies within the Organization in the diagram")
	local.add_argument(
		"--aws", "--managed",
		dest='aws_managed',
		action="store_true",
		help="Use this parameter to SHOW the AWS Managed SCPs as well, otherwise they're hidden")
	local.add_argument(
		"--ou", "--start",
		dest="starting_place",
		metavar="OU ID",
		default=None,
		help="Use this parameter to specify where to start from (Defaults to the root)")
	return parser.my_parser.parse_args(f_args)


def round_up(number):
	return int(number) + (number % 1 > 0)


def get_root_OUS(root_id):
	AllChildOUs = []
	try:
		ChildOUs = org_client.list_children(ParentId=root_id, ChildType='ORGANIZATIONAL_UNIT')
		AllChildOUs.extend(ChildOUs['Children'])
		logging.info(f"Found {len(AllChildOUs)} children from parent {root_id}")
		while 'NextToken' in ChildOUs.keys():
			ChildOUs = org_client.list_children(ParentId=root_id, ChildType='ORGANIZATIONAL_UNIT', NextToken=ChildOUs['NextToken'])
			AllChildOUs.extend(ChildOUs['Children'])
			logging.info(f"Found {len(AllChildOUs)} children from parent {root_id}")
		return AllChildOUs
	except (org_client.exceptions.AccessDeniedException,
	        org_client.exceptions.AWSOrganizationsNotInUseException,
	        org_client.exceptions.InvalidInputException,
	        org_client.exceptions.ParentNotFoundException,
	        org_client.exceptions.ServiceException,
	        org_client.exceptions.TooManyRequestsException) as myError:
		logging.error(f"Error: {myError}")
	except KeyError as myError:
		logging.error(f"Error: {myError}")
	return ()


def traverse_ous_and_accounts(ou_id: str, dot):
	"""
	Description: Recursively traverse the OUs and accounts
	@param ou_id: The ID of the OU to start from
	@param dot: The diagram to draw on
	"""
	# Retrieve the details of the current OU
	if ou_id[0] == 'r':
		ou_name = 'Root'
	else:
		ou = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
		ou_name = ou['OrganizationalUnit']['Name']

	if pPolicy:
		# Retrieve the policies associated with this OU
		ou_associated_policies = []
		for aws_policy_type in aws_policy_type_list:
			# The function below is a paginated operation, but returns more values than are allowed to be applied to a single OU, so pagination isn't needed in this case.
			# Eventually, they will likely change that - so this is a TODO for later.
			logging.info(f"Checking for {aws_policy_type} policies on OU {ou_id}")
			ou_associated_policies.extend(org_client.list_policies_for_target(TargetId=ou_id, Filter=aws_policy_type)['Policies'])
		for policy in ou_associated_policies:
			# If it's a Managed Policy and the user didn't want to see managed policies, then skip, otherwise show it.
			if policy['AwsManaged'] and not pManaged:
				continue
			else:
				dot.edge(ou_id, policy['Id'])

	# Retrieve the accounts under the current OU
	all_accounts = []
	accounts = org_client.list_accounts_for_parent(ParentId=ou_id)
	all_accounts.extend(accounts['Accounts'])
	while 'NextToken' in accounts.keys():
		accounts = org_client.list_accounts_for_parent(ParentId=ou_id, NextToken=accounts['NextToken'])
		all_accounts.extend(accounts['Accounts'])

	# Add the current OU as a node in the diagram, with the number of direct accounts it has under it
	dot.node(ou_id, label=f"{ou_name} | {len(all_accounts)}\n{ou_id}", shape=ou_shape, style='filled', fillcolor=ou_fillcolor)

	all_account_associated_policies = []
	account_associated_policies = []
	for account in all_accounts:
		account_id = account['Id']
		account_name = account['Name']
		# Add the account as a node in the diagram
		if account['Status'] == 'SUSPENDED':
			dot.node(account_id, label=f"{account_name}\n{account_id}\nSUSPENDED", shape=account_shape, style='filled', fillcolor=suspended_account_fillcolor)
		else:
			dot.node(account_id, label=f"{account_name}\n{account_id}", shape=account_shape, style='filled', fillcolor=account_fillcolor)
		# Add an edge from the current OU to the account
		dot.edge(ou_id, account_id)

		# TODO: Would love to multi-thread this... but we'll run into API limits quickly.
		if pPolicy:
			# Gather every kind of policy that could be attached to an account
			for aws_policy_type in aws_policy_type_list:
				logging.info(f"Checking for {aws_policy_type} policies on account {account_id}")
				account_associated_policies.extend(org_client.list_policies_for_target(TargetId=account_id, Filter=aws_policy_type)['Policies'])
			# Create a list of policy associations with the account that's connected to them
			all_account_associated_policies.extend([{'AcctId'     : account_id,
			                                         'PolicyId'   : x['Id'],
			                                         'PolicyName' : x['Name'],
			                                         'PolicyType' : x['Type'],
			                                         'AWS_Managed': x['AwsManaged']} for x in account_associated_policies])

	if pPolicy:
		all_account_associated_policies_uniq = set()
		for item in all_account_associated_policies:
			# This if statement skips showing the "FullAWSAccess" policies, if the "Managed" parameter wasn't used.
			if item['AWS_Managed'] and not pManaged:
				continue
			else:
				all_account_associated_policies_uniq.add((item['AcctId'], item['PolicyId']))
		for association in all_account_associated_policies_uniq:
			dot.edge(association[0], association[1])

	# Retrieve the child OUs under the current OU, and use pagination, since it's possible to have so many OUs that pagination is required.
	child_ous = org_client.list_organizational_units_for_parent(ParentId=ou_id)
	all_child_ous = child_ous['OrganizationalUnits']
	while 'NextToken' in child_ous.keys():
		child_ous = org_client.list_organizational_units_for_parent(ParentId=ou_id, NextToken=child_ous['NextToken'])
		all_child_ous.extend(child_ous['OrganizationalUnits'])

	logging.info(f"There are {len(all_child_ous)} OUs in OU {ou_id}")
	for child_ou in all_child_ous:
		child_ou_id = child_ou['Id']
		# Recursively traverse the child OU and add edges to the diagram
		logging.info(f"***** Starting to look at OU {child_ou['Name']} right now... ")
		traverse_ous_and_accounts(child_ou_id, dot)
		logging.info(f"***** Finished looking at OU {child_ou['Name']} right now... ")
		dot.edge(ou_id, child_ou_id)


def create_policy_nodes(dot):
	associated_policies = []
	for aws_policy_type in aws_policy_type_list:
		response = org_client.list_policies(Filter=aws_policy_type)
		associated_policies.extend(response['Policies'])
		while 'NextToken' in response.keys():
			response = org_client.list_policies(Filter=aws_policy_type, NextToken=response['NextToken'])
			associated_policies.extend(response['Policies'])
	for policy in associated_policies:
		policy_id = policy['Id']
		policy_name = policy['Name']

		if policy['Type'] == 'SERVICE_CONTROL_POLICY':
			policy_type = 'scp'
		elif policy['Type'] == 'RESOURCE_CONTROL_POLICY':
			policy_type = 'rcp'
		elif policy['Type'] == 'TAG_POLICY':
			policy_type = 'tag'
		elif policy['Type'] == 'BACKUP_POLICY':
			policy_type = 'backup'
		elif policy['Type'] == 'AISERVICES_OPT_OUT_POLICY':
			policy_type = 'ai'
		elif policy['Type'] == 'CHATBOT_POLICY':
			policy_type = 'chatbot'
		else:
			policy_type = 'unknown'

		# This if statement allows us to skip showing the "FullAWSAccess" policies unless the user provided the parameter to want to see them
		if policy['AwsManaged'] and not pManaged:
			continue
		else:
			dot.node(policy_id, label=f"{policy_name}\n {policy_id} | {policy_type}", shape=policy_shape, color=policy_linecolor, style='filled', fillcolor=policy_fillcolor)


def find_max_accounts_per_ou(ou_id, max_accounts=0):
	all_accounts = []
	accounts = org_client.list_accounts_for_parent(ParentId=ou_id)
	all_accounts.extend(accounts['Accounts'])
	logging.info(f"Found {len(all_accounts)} accounts in ou {ou_id} - totaling {len(all_accounts)}")
	# TODO: Figure a way to put a progress bar here - even thought we don't know how many accounts there might eventually be
	# TODO: This has to somehow recurse, to handle the finding of # of accounts in the OUs under root
	while 'NextToken' in accounts.keys():
		accounts = org_client.list_accounts_for_parent(ParentId=ou_id, NextToken=accounts['NextToken'])
		all_accounts.extend(accounts['Accounts'])
		logging.info(f"Found {len(all_accounts)} more accounts in ou {ou_id} - totaling {len(all_accounts)} accounts so far")
	max_accounts_return = max(len(all_accounts), max_accounts)

	nested_ous = org_client.list_organizational_units_for_parent(ParentId=ou_id)
	logging.info(f"Found {len(nested_ous['OrganizationalUnits'])} OUs in ou {ou_id}")
	for ou in nested_ous['OrganizationalUnits']:
		max_accounts_return = max(find_max_accounts_per_ou(ou['Id'], max_accounts_return), max_accounts_return)
	return max_accounts_return


def find_accounts_in_org():
	all_accounts = []
	org_accounts = org_client.list_accounts()
	all_accounts.extend(org_accounts['Accounts'])
	while 'NextToken' in org_accounts.keys():
		org_accounts = org_client.list_accounts(NextToken=org_accounts['NextToken'])
		all_accounts.extend(org_accounts['Accounts'])
		logging.info(f"Finding another {len(org_accounts['Accounts'])}. Total accounts found: {len(all_accounts)}")
	return all_accounts


def draw_org(froot, filename):
	max_accounts_per_ou = 1

	# Create a new Digraph object for the diagram
	dot = Digraph('AWS Organization', comment="Organization Structure")

	if pPolicy:
		create_policy_nodes(dot)

	print(f"Beginning to traverse OUs and draw the diagram... ")

	traverse_ous_and_accounts(froot, dot)
	max_accounts_per_ou = find_max_accounts_per_ou(froot, max_accounts_per_ou)

	dot_unflat = dot.unflatten(stagger=round_up(max_accounts_per_ou / 5))

	# Save the diagram to a PNG file
	dot_unflat.render(filename, format='png', view=False)
	print(f"Diagram saved to '{Fore.RED}{filename}.png{Fore.RESET}'")


if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	pProfile = args.Profile
	pTiming = args.Time
	pPolicy = args.policy
	pManaged = args.aws_managed
	pStartingPlace = args.starting_place
	verbose = args.loglevel

	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	begin_time = time()
	print(f"Beginning to look through the Org in order to create the diagram")

	# Create an AWS Organizations client
	org_session = boto3.Session(profile_name=pProfile)
	org_client = org_session.client('organizations')
	ERASE_LINE = '\x1b[2K'

	if pStartingPlace is None:
		# Find the root Org ID
		logging.info(f"User didn't include a specific OU ID, so we're starting from the root")
		root = org_client.list_roots()['Roots'][0]['Id']
		saved_filename = 'aws_organization'
	else:
		logging.info(f"User asked us to start from a specific OU ID: {pStartingPlace}")
		root = pStartingPlace
		saved_filename = 'aws_organization_subset'

	# If they specified they want to see the AWS policies, then they obviously want to see policies overall.
	if pManaged and not pPolicy:
		pPolicy = True

	# Find all the Organization Accounts
	all_org_accounts = find_accounts_in_org()

	# Display a message based on the number of accounts
	if len(all_org_accounts) > 360 and pStartingPlace is not None:
		print(f"Since there are {len(all_org_accounts)} in your Organization, this script will take a long time to run. If you're comfortable with that\n"
		      f"re-run this script and add '--start {root} ' as a parameter to this script, and we'll run without this reminder.\n"
		      f"Otherwise - you could run this script for only a specific OU's set of accounts by specifying '--start <OU ID>' and we'll start the drawing at that OU (and include any OUs below it)")
		print()
		sys.exit(1)
	if pPolicy:
		anticipated_time = 5 + (len(all_org_accounts) * 2)
		print(f"Due to there being {len(all_org_accounts)} accounts in this Org, this process will likely take about {anticipated_time} seconds")
		if anticipated_time > 30:
			print()
			print(f"{Fore.RED}Since this may take a while, you could re-run this script for only a specific OU by using the '--ou <OU ID>' parameter {Fore.RESET}")
			print()
	else:
		anticipated_time = 5 + (len(all_org_accounts) / 10)
		print(f"Due to there being {len(all_org_accounts)} accounts in this Org, this process will likely take about {anticipated_time} seconds")

	# Draw the Org itself and save it to the local filesystem
	draw_org(root, 'aws_organization')

	if pTiming and pPolicy:
		print(f"{Fore.GREEN}Drawing the Org structure when policies are included took {time() - begin_time:.2f} seconds{Fore.RESET}")
	elif pTiming:
		print(f"{Fore.GREEN}Drawing the Org structure without policies took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print("Thank you for using this script")
	print()
