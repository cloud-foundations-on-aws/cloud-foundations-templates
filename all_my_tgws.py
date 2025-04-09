#!/usr/bin/env python3
import logging
import os
import sys
from queue import Queue
from threading import Thread
from tqdm.auto import tqdm
from time import time
from decorators import timer

from botocore.exceptions import ClientError
from colorama import Fore, init

from Inventory_Modules import get_all_credentials, find_tgws2, find_account_vpcs2, find_attachments2, find_route_tables2, display_results
from ArgumentsClass import CommonArguments

init()
__version__ = "2025.04.08"


##################
# Functions
##################

def parse_args(f_args):
	"""
	Description: Parses the arguments passed into the script
	@param f_args: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = os.path.split(sys.argv[0])
	parser = CommonArguments()
	parser.multiprofile()
	parser.multiregion()
	parser.extendedargs()
	parser.rootOnly()
	parser.rolestouse()
	parser.save_to_file()
	parser.timing()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	local.add_argument(
		"--diagram", "--diag",
		help="Whether to output a diagram for the TGWs and attachments",
		dest="DrawNetworkDiagram",
		action="store_true")
	local.add_argument(
		"--type",
		nargs="*",
		choices=['tgw', 'vpc', 'attach', 'rt', 'all'],
		default=['all'],
		help="Which types of resources you want identified and (possibly) included in the diagram",
		dest="ResourceTypes",
		action="store")
	return parser.my_parser.parse_args(f_args)

@timer()
def check_accounts_for_vpcs(CredentialList):
	"""
	Note that this function takes a list of Credentials and checks for vpcs in every account it has creds for
	"""

	class FindVPCs(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					account_vpcs = find_account_vpcs2(c_account_credentials)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for vpc in account_vpcs['Vpcs']:
						vpc['MgmtAccount'] = c_account_credentials['MgmtAccount']
						vpc['AccountId'] = c_account_credentials['AccountId']
						vpc['Region'] = c_account_credentials['Region']
						vpc['VpcName'] = "None"
						vpc['credentials'] = c_account_credentials
						# vpc.update(aws_access_key_id=c_account_credentials['AccessKeyId'],
						#            aws_secret_access_key=c_account_credentials['SecretAccessKey'],
						#            aws_session_token=c_account_credentials['SessionToken'],
						#            region_name=c_account_credentials['Region'])
						if 'Tags' in vpc.keys():
							for tag in vpc['Tags']:
								if tag['Key'] == 'Name':
									vpc['VpcName'] = tag['Value']
					if len(account_vpcs['Vpcs']) > 0:
						AllVPCs.extend(account_vpcs['Vpcs'])
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					continue
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(f"Actual Error: {my_Error}")
					continue
				finally:
					logging.info(f"Finished finding vpcs in accounts {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					pbar.update()
					self.queue.task_done()

	###########

	checkqueue = Queue()

	AllVPCs = []
	WorkerThreads = min(len(CredentialList), 50)

	pbar = tqdm(desc=f'Finding vpcs in {len(CredentialList)} accounts / regions',
	            total=len(CredentialList), unit=' locations'
	            )

	for x in range(WorkerThreads):
		worker = FindVPCs(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			checkqueue.put((credential))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllVPCs


def dedupe_vpcs_by_account(vpcs_found):
	"""
	De-duplicates VPCs by Account Number
	Args:
		vpcs_found (list): List of VPC dictionaries
	Returns:
		list: De-duped list of VPCs
	"""
	seen_vpcs = set()
	deduped_vpcs = []

	for vpc in vpcs_found:
		# Create a unique key using account number and region
		# We don't use the VPC ID here, since we're really trying to get only those accounts WITH a VPC per region,
		# in order to decrease the number of accounts we need to check for TGW attachments
		unique_key = (vpc.get('AccountId'), vpc.get('Region'))

		if unique_key not in seen_vpcs:
			seen_vpcs.add(unique_key)
			deduped_vpcs.append(vpc)

	return deduped_vpcs

# @timer()
def find_tgws(CredentialList: list):
	"""
	Note that this function takes a list of Credentials and finds the TGWs in every account it has creds for
	"""

	class FindTGWs(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					org_tgws = find_tgws2(c_account_credentials)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for tgw in org_tgws:
						tgw['MgmtAccount'] = c_account_credentials['MgmtAccount']
						tgw['AccountId'] = c_account_credentials['AccountId']
						tgw['Region'] = c_account_credentials['Region']
						tgw['credentials'] = c_account_credentials
						# tgw.update(aws_access_key_id=c_account_credentials['AccessKeyId'],
						#            aws_secret_access_key=c_account_credentials['SecretAccessKey'],
						#            aws_session_token=c_account_credentials['SessionToken'],
						#            region_name=c_account_credentials['Region'])
						tgw['TGWName'] = "None"
						if 'Tags' in tgw.keys():
							for tag in tgw['Tags']:
								if tag['Key'] == 'Name':
									tgw['TGWName'] = tag['Value']
					AllTGWs.extend(org_tgws)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(f"Actual Error: {my_Error}")
					continue
				finally:
					logging.info(f"Finished finding tgws in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					pbar.update()
					self.queue.task_done()

	###########

	checkqueue = Queue()

	AllTGWs = []
	WorkerThreads = min(len(CredentialList), 50)

	pbar = tqdm(desc=f'Finding TGWs from {len(CredentialList)} accounts / regions',
	            total=len(CredentialList), unit=' locations'
	            )

	for x in range(WorkerThreads):
		worker = FindTGWs(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in CredentialList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			checkqueue.put((credential))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllTGWs


def dedupe_tgws_by_account(tgws_found):
	"""
	De-duplicates TGWs by Account Number
	Args:
		tgws_found (list): List of TGW dictionaries
	Returns:
		list: De-duped list of TGWs
	"""
	seen_tgws = set()
	deduped_tgws = []

	for tgw in tgws_found:
		# Create a unique key using account number and vpc id
		# No need to specify the region here, since the ID will be unique to the region
		unique_key = (tgw.get('AccountId'), tgw.get('TransitGatewayId'))

		if unique_key not in seen_tgws:
			seen_tgws.add(unique_key)
			deduped_tgws.append(tgw)

	return deduped_tgws

@timer()
def check_for_attachments(VPCList: list):
	"""
	Note that this function takes a list credentials and checks for TGW attachments in each account and region it has creds for
	"""

	class FindTGWAttachments(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					attachments = find_attachments2(c_account_credentials)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for attachment in attachments:
						attachment['MgmtAccount'] = c_account_credentials['MgmtAccount']
						attachment['AccountId'] = c_account_credentials['AccountId']
						attachment['Region'] = c_account_credentials['Region']
						attachment['AttachmentName'] = "None"
						if 'Tags' in attachment.keys():
							for tag in attachment['Tags']:
								if tag['Key'] == 'Name':
									attachment['AttachmentName'] = tag['Value']
					AllAttachments.extend(attachments)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					logging.info(f"Finished finding attachments in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					pbar.update()
					self.queue.task_done()

	###########

	checkqueue = Queue()

	AllAttachments = []
	WorkerThreads = min(len(VPCList), 50)

	pbar = tqdm(desc=f'Finding attachments from {len(VPCList)} VPCs',
	            total=len(VPCList), unit=' vpcs'
	            )

	for x in range(WorkerThreads):
		worker = FindTGWAttachments(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in VPCList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			if 'credentials' in credential.keys():
				checkqueue.put((credential['credentials']))
			else:
				checkqueue.put((credential))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllAttachments


def dedupe_attachments_by_account(attachments_found):
	"""
	De-duplicates TGWs by Account Number
	Args:
		attachments_found (list): List of attachment dictionaries
	Returns:
		list: De-duped list of attachments
	"""
	seen_attachments = set()
	deduped_attachments = []

	for attachment in attachments_found:
		# Create a unique key using attachment id, since attachments can show up in both the providing and consuming accounts.
		unique_key = (attachment.get('TransitGatewayAttachmentId'))

		if unique_key not in seen_attachments:
			seen_attachments.add(unique_key)
			deduped_attachments.append(attachment)

	return deduped_attachments

@timer()
def find_tgw_route_tables(TGWList: list) -> list:
	"""
	Note that this function takes a list of Credentials and checks for subnets in every account it has creds for
	"""

	class FindRouteTables(Thread):

		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# Get the work from the queue and expand the tuple
				c_account_credentials = self.queue.get()
				logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
				try:
					logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
					route_tables = find_route_tables2(c_account_credentials)
					logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
					for rt in route_tables:
						rt['MgmtAccount'] = c_account_credentials['MgmtAccount']
						rt['AccountId'] = c_account_credentials['AccountId']
						rt['Region'] = c_account_credentials['Region']
						rt['RTName'] = "None"
						if 'Tags' in rt.keys():
							for tag in rt['Tags']:
								if tag['Key'] == 'Name':
									rt['RTName'] = tag['Value']
					if len(route_tables) > 0:
						AllRouteTables.extend(route_tables)
				except KeyError as my_Error:
					logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
					logging.info(f"Actual Error: {my_Error}")
					pass
				except AttributeError as my_Error:
					logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
					logging.warning(my_Error)
					continue
				finally:
					logging.info(f"Finished finding transit gateway route tables in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}")
					pbar.update()
					self.queue.task_done()

	checkqueue = Queue()

	AllRouteTables = []
	WorkerThreads = min(len(TGWList), 50)

	# TODO: This references 'TGWs' in the description,
	#  but it's possible that the user didn't specify TGWs,
	#  and therefore this should be x accounts and not TGWs.
	pbar = tqdm(desc=f'Finding Route Tables from {len(TGWList)} TGWs',
	            total=len(TGWList), unit=' TGWs'
	            )

	for x in range(WorkerThreads):
		worker = FindRouteTables(checkqueue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()

	for credential in TGWList:
		logging.info(f"Connecting to account {credential['AccountId']}")
		try:
			if 'credentials' in credential.keys():
				checkqueue.put((credential['credentials']))
			else:
				checkqueue.put((credential))
		except ClientError as my_Error:
			if "AuthFailure" in str(my_Error):
				logging.error(f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region")
				logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
				pass
	checkqueue.join()
	pbar.close()
	return AllRouteTables

@timer()
def combine_all_resources(VPCList: list, TGWList: list, AttachmentList: list, RouteTableList: list):
	"""
	Combines all resources into a single list
	:param VPCList: List of VPCs
	:param TGWList: List of TGWs
	:param AttachmentList: List of attachments
	:param RouteTableList: List of route tables
	:return: List of all resources
	"""
	AllResources = []
	resource = {}
	for item in VPCList:
		resource['MgmtAccount'] = item['MgmtAccount']
		resource['AccountId'] = item['AccountId']
		resource['Region'] = item['Region']
		resource['Type'] = "VPC"
		resource['ResourceId'] = item['VpcId']
		resource['Name'] = item['VpcName']
		AllResources.append(resource.copy())
	for item in TGWList:
		resource['MgmtAccount'] = item['MgmtAccount']
		resource['AccountId'] = item['AccountId']
		resource['Region'] = item['Region']
		resource['Type'] = "TGW"
		resource['ResourceId'] = item['TransitGatewayId']
		resource['Name'] = item['TGWName']
		AllResources.append(resource.copy())
	for item in AttachmentList:
		resource['MgmtAccount'] = item['MgmtAccount']
		resource['AccountId'] = item['AccountId']
		resource['Region'] = item['Region']
		resource['Type'] = "TGW Attachment"
		resource['ResourceId'] = item['TransitGatewayAttachmentId']
		resource['Name'] = item['AttachmentName']
		AllResources.append(resource.copy())
	for item in RouteTableList:
		resource['MgmtAccount'] = item['MgmtAccount']
		resource['AccountId'] = item['AccountId']
		resource['Region'] = item['Region']
		resource['Type'] = "Route Table"
		resource['ResourceId'] = item['TransitGatewayRouteTableId']
		resource['Name'] = item['RTName']
		AllResources.append(resource.copy())
	sorted_AllResource = sorted(AllResources, key=lambda x: (x['Region'], x['AccountId'], x['Type'], x['ResourceId']))
	return sorted_AllResource


def get_regions(Resources: list):
	regions = []
	resource: dict
	for resource in Resources:
		if resource['Region'] not in regions:
			regions.append(resource['Region'])
	return regions


def draw_network1(VPCList, TGWList, AttachmentList):
	"""
	Description: Draws out the network, given the TGWs, VPCs, etc provided
	@param VPCList: List of VPCs
	@param TGWList: List of TGWs
	@param AttachmentList: List of attachments
	"""
	import graphviz

	# Create a new directed graph
	dot = graphviz.Digraph(comment='AWS Network Diagram')

	# Set graph attributes for radial layout
	dot.attr(rankdir='TB')  # Top to bottom direction
	dot.attr(splines='spline')  # Curved lines
	dot.attr(concentrate='true')  # Merge edges
	dot.attr(ranksep='2.0')  # Increase space between ranks

	# Create invisible edges between TGWs to keep them centered
	if len(TGWList) > 1:
		with dot.subgraph(name='cluster_tgw_align') as c:
			c.attr(rank='same')  # Force TGWs to same rank
			prev_tgw = None
			for tgw in TGWList:
				current_tgw = tgw['TransitGatewayId']
				c.node(current_tgw,
				       label=f"{current_tgw}\n{tgw.get('AccountId', 'Unknown')}",
				       shape='diamond',
				       style='filled',
				       fillcolor='lightgreen')
				if prev_tgw:
					c.edge(prev_tgw, current_tgw, style='invis')  # Invisible edge
				prev_tgw = current_tgw
	else:
		# If only one TGW, add it directly
		for tgw in TGWList:
			dot.node(tgw['TransitGatewayId'],
			         label=f"{tgw['TransitGatewayId']}\n{tgw.get('AccountId', 'Unknown')}",
			         shape='diamond',
			         style='filled',
			         fillcolor='lightgreen')

	# Group VPCs by which TGW they connect to
	vpc_groups = {}
	for attachment in AttachmentList:
		tgw_id = attachment['TransitGatewayId']
		if tgw_id not in vpc_groups:
			vpc_groups[tgw_id] = []
		vpc_groups[tgw_id].append(attachment['ResourceId'])

	# Add VPCs in subgraphs around their TGWs
	for tgw_id, vpc_list in vpc_groups.items():
		with dot.subgraph(name=f'cluster_vpc_{tgw_id}') as c:
			c.attr(rank='same')
			for vpc_id in vpc_list:
				# Find the full VPC info
				vpc = next((v for v in VPCList if v['VpcId'] == vpc_id), None)
				if vpc:
					c.node(vpc_id,
					       label=f"{vpc_id}\n{vpc.get('AccountId', 'Unknown')}",
					       shape='box',
					       style='filled',
					       fillcolor='lightblue')

	# Add edges with labels on both sides
	for attachment in AttachmentList:
		dot.edge(attachment['ResourceId'],
		         attachment['TransitGatewayId'],
		         headlabel=f"TGW: {attachment['TransitGatewayAttachmentId'][-8:]}",
		         taillabel=f"VPC: {attachment.get('VpcAttachmentId', 'Unknown')[-8:]}",
		         labeldistance='2.0',
		         labelangle='45')

	# Render the graph
	try:
		dot.render('aws_network_diagram', format='png', cleanup=True)
		print("Network diagram has been saved as 'aws_network_diagram.png'")
	except Exception as e:
		print(f"Error generating diagram: {str(e)}")
		print("Make sure graphviz is installed on your system")


def draw_network(Regions: list, VPCList: list, TGWList: list, AttachmentList: list, RouteTableList: list):
	"""
	Description: Draws out the network from the VPCs, TGWs, and TGW Attachments
	:param VPCList: List of VPCs
	:param TGWList: List of TGWs
	:param AttachmentList: List of attachments
	:param RouteTableList: List of route tables
	"""
	import graphviz

	# Create a new directed graph
	dot = graphviz.Digraph(comment='AWS Network Diagram', engine='circo')
	# dot = graphviz.Digraph(comment='AWS Network Diagram')
	# dot.attr(rankdir='LR')  # Left to right layout
	# Set graph attributes for radial layout
	# dot.attr(splines='spline')  # Curved lines
	# dot.attr(sep='+25,25')  # Increase separation between nodes
	# dot.attr(nodesep='2.0')  # Minimum space between nodes
	# dot.attr(ranksep='4.0')  # Minimum space between ranks
	# dot.attr(overlap='scale')  # Prevent node overlap
	dot.attr(size='20,20')  # Increase canvas size
	# Create separate sub-drawings for each region
	sorted_VPCList = sorted(VPCList, key=lambda x: (x['AccountId'], x['Region'], x['VpcId']))
	for region in Regions:
		with dot.subgraph(name=f'cluster_regions-{region}') as r:
			r.attr(label=region)
			r.attr(cluster='true')
		# r.attr(nodesep='1.5')  # Space between nodes in cluster
		# r.node(region,
		#        label=region,
		#        shape='box',
		#        style='filled',
		#        fillcolor='lightblue')
		# Add VPC nodes
		for vpc in sorted_VPCList:
			if vpc['Region'] == region:
				dot.node(vpc['VpcId'],
				         label=f"{vpc['VpcId']}\n{vpc.get('AccountId', 'Unknown')}",
				         shape='box',
				         style='filled',
				         fillcolor='lightblue')

		# Add TGW nodes
		for tgw in TGWList:
			if tgw['Region'] == region:
				dot.node(tgw['TransitGatewayId'],
				         label=f"{tgw['TransitGatewayId']}\n{tgw.get('AccountId', 'Unknown')}",
				         shape='diamond',
				         root='true',
				         style='filled',
				         fillcolor='lightgreen',
				         # margin='0.3',  # Add margin around node text
				         # width='2',  # Minimum width
				         # height='1'  # Minimum height
				         )

		# Add Route Table nodes
		for rt in RouteTableList:
			if rt['Region'] == region:
				dot.node(rt['TransitGatewayRouteTableId'],
				         label=f"{rt['TransitGatewayRouteTableId']}\n{rt.get('AccountId', 'Unknown')}",
				         shape='ellipse',
				         style='filled',
				         fillcolor='orange',
				         # margin='0.3',  # Add margin around node text
				         # width='2',  # Minimum width
				         # height='2'  # Minimum height
				         )

	for rt in RouteTableList:
		dot.edge(rt['TransitGatewayRouteTableId'],
		         rt['TransitGatewayId'],
		         label=f"Default Association: {rt['DefaultAssociationRouteTable']}\nDefault Propagation: {rt['DefaultPropagationRouteTable']}"
		         )

	# Add edges for attachments
	for attachment in AttachmentList:
		# vpc_side = f"{attachment.get('ResourceId', 'Unknown')}"
		# tgw_side = f"{attachment['Association'].get('TransitGatewayRouteTableId', 'Unknown')}"

		# Add edge from VPC to TGW
		dot.edge(attachment['ResourceId'],
		         attachment['Association']['TransitGatewayRouteTableId'],
		         label=attachment['TransitGatewayAttachmentId'],
		         # minlen='2',  # Minimum edge length
		         # labeldistance='2.0',  # Distance of label from node
		         # labelangle='45'  # Angle of label
		         # taillabel=vpc_side,
		         # headlabel=tgw_side,
		         )
	# Render the graph
	try:
		dot.render('aws_network_diagram', format='png', cleanup=True)
		print("Network diagram has been saved as 'aws_network_diagram.png'")
	except Exception as e:
		print(f"Error generating diagram: {str(e)}")
		print("Make sure graphviz is installed on your system")


##################
# Main
##################


ERASE_LINE = '\x1b[2K'
begin_time = time()

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])
	pProfiles = args.Profiles
	pRegionList = args.Regions
	pAccounts = args.Accounts
	pRoleList = args.AccessRoles
	pSkipAccounts = args.SkipAccounts
	pSkipProfiles = args.SkipProfiles
	pRootOnly = args.RootOnly
	pFilename = args.Filename
	pTiming = args.Time
	verbose = args.loglevel
	pDrawNetwork = args.DrawNetworkDiagram
	pResourceTypes = args.ResourceTypes
	# Setup logging levels
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	logging.info(f"Profiles: {pProfiles}")

	print()
	print(f"Checking accounts for TGWs and attachments... ")
	print()
	display_dict = {'MgmtAccount': {'DisplayOrder': 1, 'Heading': 'Mgmt Acct'},
	                'AccountId'  : {'DisplayOrder': 2, 'Heading': 'Acct Number'},
	                'Region'     : {'DisplayOrder': 3, 'Heading': 'Region'},
	                'ResourceId' : {'DisplayOrder': 4, 'Heading': 'Resource'},
	                'Type'       : {'DisplayOrder': 5, 'Heading': 'Type'},
	                'Name'       : {'DisplayOrder': 6, 'Heading': 'Name'}}

	# Get credentials from all relevant Children accounts
	AllCredentials = get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoleList)

	# Find TGWs
	TGWsFound = find_tgws(AllCredentials) if any(item in ['tgw','all'] for item in pResourceTypes) else ''
	# Since multiple accounts / vpcs will show a transit gateway associated (due to sharing),
	# we need to de-dupe the TGW Listing we send
	# And if we didn't even look for TGWs, we can still run this, and it will be fast...
	DeDupedTGWs = dedupe_tgws_by_account(TGWsFound)

	# Find VPCs
	VPCsFound = check_accounts_for_vpcs(AllCredentials) if any(item in ['vpc','all'] for item in pResourceTypes) else ''
	# The Find_Attachment finds all attachments for all VPCs in one call, so by sending a list of VPCs, we're duplicating the attachments
	# So we need to de-dupe the VPC Listing we send, to narrow it down
	# And if we didn't even look for VPCs, we can still run this, and it will be fast...
	AccountsWithVPCs = dedupe_vpcs_by_account(VPCsFound)

	# Finding Transit Gateway Attachments
	DeDupedAttachments = []
	if any(item in ['vpc', 'all'] for item in pResourceTypes) and any(item in ['attach','all'] for item in pResourceTypes):
		logging.info(f"Finding attachments constrained by VPCs, since VPC identification was requested")
		AttachmentsFound = check_for_attachments(AccountsWithVPCs)
		DeDupedAttachments = dedupe_attachments_by_account(AttachmentsFound)
	elif any(item in ['attach','all'] for item in pResourceTypes):
		logging.info(f"Finding attachments without any VPC constraints, since VPC identification was not requested")
		AttachmentsFound = check_for_attachments(AllCredentials)
		DeDupedAttachments = dedupe_attachments_by_account(AttachmentsFound)

	# Finding Transit Gateway Route Tables
	RouteTablesFound = []
	if any(item in ['tgw', 'all'] for item in pResourceTypes) and any(item in ['rt', 'all'] for item in pResourceTypes):
		logging.info(f"Finding attachments constrained by TGWs, since TGW identification was requested")
		RouteTablesFound = find_tgw_route_tables(DeDupedTGWs)
	elif any(item in ['rt','all'] for item in pResourceTypes):
		logging.info(f"Finding attachments without being constrained by the TGWs we found, since TGW identification was not requested")
		RouteTablesFound = find_tgw_route_tables(AllCredentials)

	# Combine all lists of resource types into a single list
	AllResources = combine_all_resources(VPCsFound, DeDupedTGWs, DeDupedAttachments, RouteTablesFound)
	ResourcedRegions = get_regions(AllResources)
	display_results(AllResources, display_dict, None, pFilename)

	draw_network(ResourcedRegions, VPCsFound, TGWsFound, DeDupedAttachments, RouteTablesFound) if pDrawNetwork else ''
	# draw_network1(VPCsFound, TGWsFound, DeDupedAttachments) if pDrawNetwork else ''
	# # display_results(SubnetsFound, display_dict)
	# present_results()
	# # Print out an analysis of what was found at the end
	# if verbose < 50:
	# 	analyze_results()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")

"""
print(f'{Fore.RED}Found {len(VPCsFound)} VPCs{Fore.RESET}')
for item in VPCsFound:
	print(item)
print(f'{Fore.RED}Found {len(TGWsFound)} Transit Gateways{Fore.RESET}')
for item in TGWsFound:
	print(item)
print(f'{Fore.RED}Found {len(AttachmentsFound)} Transit Gateway Attachments{Fore.RESET}')
for item in AttachmentsFound:
	print(item)
"""
print()
print("Thank you for using this script")
print()
