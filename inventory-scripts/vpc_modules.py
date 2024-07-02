def del_vpc(ocredentials, fVPCId, fRegion):
	"""
	ocredentials looks like this:
		session_vpc = boto3.Session(
			aws_access_key_id = ocredentials['AccessKeyId'],
			aws_secret_access_key = ocredentials['SecretAccessKey'],
			aws_session_token = ocredentials['SessionToken'],
			region_name=fRegion)
	fVPCId is a string with the VPC ID in it
	fRegion is the string that represents the AWS region name
	"""

	import boto3
	import logging
	from botocore.exceptions import ClientError
	from colorama import init, Fore

	# ERASE_LINE = '\x1b[2K'

	def find_and_delete_vpc_endpoints(fVPC_client, fVpcId, fRegion):

		import logging
		vpc_endpoints = fVPC_client.describe_vpc_endpoints(
				Filters=[
					{
						'Name'  : 'vpc-id',
						'Values': [fVpcId]
						}
					]
				)
		vpc_endpoints_to_delete = []
		logging.info("Found %s vpc endpoints", len(vpc_endpoints))
		for x in range(len(vpc_endpoints['VpcEndpoints'])):
			vpc_endpoints_to_delete.append(vpc_endpoints['VpcEndpoints'][x]['VpcEndpointId'])

		logging.warning("Found %s endpoints in vpc", len(vpc_endpoints_to_delete))
		if len(vpc_endpoints_to_delete) > 0:
			try:
				response = fVPC_client.delete_vpc_endpoints(
						VpcEndpointIds=vpc_endpoints_to_delete
						)
				return 0
			except ClientError as my_error:
				print(my_error)
				return 1
		else:
			logging.warning("No Endpoints found to delete")
			return 0

	def find_and_delete_vpc_security_groups(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		vpc_security_groups = fVPC_client.describe_security_groups(
				Filters=[
					{
						'Name'  : 'vpc-id',
						'Values': [fVpcId]
						}
					]
				)
		for x in range(len(vpc_security_groups['SecurityGroups'])):
			if vpc_security_groups['SecurityGroups'][x]['GroupName'] == 'default':
				logging.info("Only found default security groups. These will auto-delete")
				continue
			else:
				try:
					logging.info("Deleting security group %s", vpc_security_groups['SecurityGroups'][x]['GroupId'])
					response = fVPC_client.delete_security_group(
							GroupId=vpc_security_groups['SecurityGroups'][x]['GroupId']
							)
				except ClientError as my_Error:
					print(my_Error)
					return 1
		return 0

	def find_and_delete_vpc_peering_connections(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		vpc_peering_connections = fVPC_client.describe_vpc_peering_connections(
				Filters=[
					{
						'Name'  : 'requester-vpc-info.vpc-id',
						'Values': [fVpcId]
						}
					]
				)
		for x in range(len(vpc_peering_connections['VpcPeeringConnections'])):
			try:
				response = fVPC_client.delete_vpc_peering_connection(
						VpcPeeringConnectionId=vpc_peering_connections['VpcPeeringConnections'][x][
							'VpcPeeringConnectionId']
						)
			except ClientError as my_Error:
				print(my_Error)
				return 1
		return 0

	def find_and_delete_vpc_route_tables(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		vpc_route_tables = fVPC_client.describe_route_tables(
				Filters=[
					{
						'Name'  : 'vpc-id',
						'Values': [fVpcId]
						}
					]
				)
		vpc_route_tables_to_delete = list()
		for x in range(len(vpc_route_tables['RouteTables'])):
			rRouteTableId = vpc_route_tables['RouteTables'][x]['RouteTableId']
			# Add all route tables to the delete list...
			vpc_route_tables_to_delete.append(rRouteTableId)
			for y in range(len(vpc_route_tables['RouteTables'][x]['Associations'])):
				rIsMain = vpc_route_tables['RouteTables'][x]['Associations'][y]['Main']
				# However, since we can't disassociate the "Main" Route Table, and we can't delete it, we remove it from our list.
				if rIsMain:
					vpc_route_tables_to_delete.remove(rRouteTableId)
					continue
				rRouteAssociation = vpc_route_tables['RouteTables'][x]['Associations'][y]['RouteTableAssociationId']
				try:
					disassociateresponse = fVPC_client.disassociate_route_table(
							AssociationId=rRouteAssociation
							)
					logging.critical("Disassociated Route Table ID: %s", rRouteTableId)
				except ClientError as my_Error:
					print(my_Error)
					return 1

			# pprint.pprint(vpc_route_tables_to_delete)
			for RtTbl in vpc_route_tables_to_delete:
				try:
					deleteresponse = fVPC_client.delete_route_table(
							RouteTableId=RtTbl
							)
					print("Deleted Route Table ID:", RtTbl)
					vpc_route_tables_to_delete.remove(RtTbl)
				except ClientError as my_Error:
					print(my_Error)
					return 1
		return 0

	def find_and_delete_vpc_nacls(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		vpc_nacls = fVPC_client.describe_network_acls(
				Filters=[
					{
						'Name'  : 'vpc-id',
						'Values': [fVpcId]
						}
					]
				)

		for x in (range(len(vpc_nacls['NetworkAcls']))):
			if vpc_nacls['NetworkAcls'][x]['IsDefault']:
				continue
			else:
				try:
					response = fVPC_client.delete_network_acl(
							NetworkAclId=vpc_nacls['NetworkAcls'][x]['NetworkAclId']
							)
				# pprint.pprint(response)
				except ClientError as my_Error:
					print(my_Error)
					return 1
		return 0

	def find_and_delete_subnets(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		subnets = fVPC_client.describe_subnets(
				Filters=[
					{
						'Name'  : 'vpc-id',
						'Values': [fVpcId]
						}
					]
				)
		# print("Found",len(subnets['Subnets']),"Subnets")

		# pprint.pprint(vpc_nacls)
		# pprint.pprint(vpc_nacls['NetworkAcls'][0]['IsDefault'])
		# print("There are "+str(len(subnets['Subnets']))+" subnets")
		# print("There are "+str(len(vpc_route_tables['RouteTables'][0]['Routes']))+" routes in the first table")
		for x in range(len(subnets['Subnets'])):
			try:
				rSubnetId = subnets['Subnets'][x]['SubnetId']
				response = fVPC_client.delete_subnet(
						SubnetId=rSubnetId
						)
			# pprint.pprint(response)
			except ClientError as my_Error:
				print(my_Error)
				return 1
		return 0

	def find_and_delete_NAT_gateways(fVPC_client, fVpcId, fRegion):

		import time
		from botocore.exceptions import ClientError

		cyclesWaited = 0
		nat_gateways = fVPC_client.describe_nat_gateways(
				Filters=[
					{
						'Name'  : 'vpc-id',
						'Values': [fVpcId]
						},
					{
						'Name'  : 'state',
						'Values': ['available']
						}
					]
				)
		rNatGWList = []
		if len(nat_gateways['NatGateways']) > 0:
			logging.info("Found %s NAT Gateways", len(nat_gateways['NatGateways']))
			for x in range(len(nat_gateways['NatGateways'])):
				rNatGWList.append(nat_gateways['NatGateways'][x]['NatGatewayId'])
				try:
					deleteresponse = fVPC_client.delete_nat_gateway(
							NatGatewayId=rNatGWList[x]
							)
				except ClientError as my_Error:
					print(my_Error)
					return 1
			print("Waiting for the NAT Gateways to be fully deleted")
			verify_nat_gws_are_gone = nat_gateways
			while len(verify_nat_gws_are_gone['NatGateways']) > 0:
				verify_nat_gws_are_gone = fVPC_client.describe_nat_gateways(
						Filters=[
							{
								'Name'  : 'state',
								'Values': [
									'available', 'pending', 'deleting', 'failed'
									]
								}
							],
						NatGatewayIds=rNatGWList
						)
				cyclesWaited += 1
				if cyclesWaited % 5 == 0:
					logging.info("Still waiting on NAT Gateways to be deleted...")
			# print(".", end='', flush=True)
			time.sleep(10)
		return 0

	def find_and_delete_gateways(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		gateways = fVPC_client.describe_internet_gateways(
				Filters=[
					{
						'Name'  : 'attachment.vpc-id',
						'Values': [fVpcId]
						}
					]
				)
		for x in range(len(gateways['InternetGateways'])):
			rGatewayId = gateways['InternetGateways'][x]['InternetGatewayId']
			try:
				detachresponse = fVPC_client.detach_internet_gateway(
						InternetGatewayId=rGatewayId,
						VpcId=fVpcId
						)
			except ClientError as my_Error:
				print(my_Error)
				return 1
			try:
				deleteresponse = fVPC_client.delete_internet_gateway(
						InternetGatewayId=rGatewayId
						)
			except ClientError as my_Error:
				print(my_Error)
				return 1
		return 0

	def find_and_delete_virtual_gateways(fVPC_client, fVpcId, fRegion):

		import time
		from botocore.exceptions import ClientError

		cyclesWaited = 0
		vgws = fVPC_client.describe_vpn_gateways(
				Filters=[
					{
						'Name'  : 'attachment.vpc-id',
						'Values': [fVpcId]
						},
					{
						'Name'  : 'attachment.state',
						'Values': ['attached']
						}
					]
				)
		rVPN_GatewayList = list()
		for x in range(len(vgws['VpnGateways'])):
			rVPN_GatewayList.append(vgws['VpnGateways'][x]['VpnGatewayId'])
			try:
				detachresponse = fVPC_client.detach_vpn_gateway(
						VpnGatewayId=rVPN_GatewayList[x],
						VpcId=fVpcId
						)
			except ClientError as my_Error:
				print(my_Error)
				return 1

			print("Waiting for the VPN Gateways to be fully detached")
			verify_vgws_are_gone = vgws
			while len(verify_vgws_are_gone['VpnGateways']) > 0:
				verify_vgws_are_gone = fVPC_client.describe_vpn_gateways(
						Filters=[
							{
								'Name'  : 'attachment.state',
								'Values': ['attached', 'detaching']
								},
							],
						VpnGatewayIds=rVPN_GatewayList
						)
				cyclesWaited += 1
				if cyclesWaited % 5 == 0:
					logging.info("Still waiting on VGWS to be deleted...")
				# pprint.pprint(verify_nat_gws_are_gone)
				time.sleep(10)
		return 0

	def delete_vpc(fVPC_client, fVpcId, fRegion):

		from botocore.exceptions import ClientError

		try:
			response = fVPC_client.delete_vpc(
					VpcId=fVpcId
					)
			return 0
		except ClientError as my_Error:
			print(my_Error)
			return 1

	###### Main ########################################
	session_vpc = boto3.Session(
			aws_access_key_id=ocredentials['AccessKeyId'],
			aws_secret_access_key=ocredentials['SecretAccessKey'],
			aws_session_token=ocredentials['SessionToken'],
			region_name=fRegion)
	client_vpc = session_vpc.client('ec2')
	try:
		# 1. Call EC2.Client.describe_vpc_endpoints. Filter on your VPC id. Call EC2.client.delete_vpc_endpoints on each
		print(f"Deleting vpc in {fRegion}...", end='', flush=True)

		logging.info(f"Deleting vpc-endpoints... for vpc {fVPCId} in region {fRegion}")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_vpc_endpoints(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_endpoints deletion script")
			return 1  # out of the try
		# 2. Call VPC.security_groups. Delete the group unless its group_name attribute is "main". The main security group will be deleted via VPC.delete().
		logging.info("Deleting security groups...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_vpc_security_groups(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_security_group deletion script")
			return 1  # out of the try

		# 3. Call EC2.Client.describe_vpc_peering_connections. Filter on your VPC id as the requester-vpc-info.vpc-id. (My VPC is a requester. There is also accepter-vpc-info.vpc-id among other filters.) Iterate through the entries keyed by VpcPeeringConnections. Get an instance of the peering connection by instantiating a EC2.ServiceResource.VpcPeeringConnection with the VpcPeeringConnectionId. Call VpcPeeringConnection.delete() to remove the peering connection.
		logging.info("Deleting vpc peering connections...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_vpc_peering_connections(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_peering_connection deletion script")
			return 1  # out of the try

		# Need to figure a way to wait on this operation, if there are Gateways to be deleted.
		logging.info("Deleting NAT Gateways...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_NAT_gateways(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_NAT_gateways deletion script")
			return 1  # out of the try

		# 4. Call vpc.route_tables.all() and iterate through the route tables. For each route table, iterate through its routes using the RouteTable.routes attribute. Delete the routes where route['Origin'] is 'CreateRoute'. I deleted using EC2.Client.delete_route using EC2.RouteTable.id and route['DestinationCidrBlock']. After removing the routes, call EC2.RouteTable.delete() to remove the route table itself. I set up exception handlers for each delete. Not every route table can be deleted, but I haven't cracked the code. Maybe next week.
		logging.info("Deleting vpc route tables...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_vpc_route_tables(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_route_tables deletion script")
			return 1  # out of the try

		# 5. Iterate through vpc.network_acls.all(), test12 the NetworkAcl.is_default attribute and call NetworkAcl.delete for non-default acls.
		logging.info("Deleting vpc network access control lists...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_vpc_nacls(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_nacls deletion script")
			return 1  # out of the try

		#
		# 6. Iterate through vpc.subnets.all().network_interfaces.all(). Call EC2.NetworkInterface.delete() on each.
		logging.info("Deleting subnets...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_subnets(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_subnets deletion script")
			return 1  # out of the try
		#
		# 7. Iterate through vpc.internet_gateways.all(). Call EC2.InternetGateway.delete() on each.
		logging.info("Deleting Internet Gateways...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_gateways(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_gateways deletion script")
			return 1  # out of the try

		# Virtual Gateway
		logging.info("Deleting Virtual Customer Gateways...")
		print(".", end='', flush=True)
		ResultGood = (find_and_delete_virtual_gateways(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the vpc_virtual_gateways deletion script")
			return 1  # out of the try

		#
		# 8. Call vpc.delete()
		print("!")
		ResultGood = (delete_vpc(client_vpc, fVPCId, fRegion) == 0)
		if not ResultGood:
			logging.error("Something failed in the final vpc deletion script")
			return 1  # out of the try
	except ClientError as my_Error:
		print(my_Error)
		print(f"{Fore.RED}What to do now?{Fore.RESET}")
		return 1

	return 0
