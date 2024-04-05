import boto3
import json

ec2 = boto3.client('ec2')
# get list of regions
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

# function to delete the default VPC from every region
def process_vpc(vpc_id, region):
    print(f"Deleting VPC {vpc_id} from region {region}")
    ec2 = boto3.client('ec2', region_name=region)
    igw_filters = [{'Name':'attachment.vpc-id','Values':[vpc_id]}]
    igws = ec2.describe_internet_gateways(Filters=igw_filters)['InternetGateways']
    igw_ids = [igw['InternetGatewayId'] for igw in igws]

    # detach and delete IGWs
    for igw_id in igw_ids:
        print(f"Detaching and deleting IGW {igw_id} in region {region}")
        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)

    # get list of subnet IDs in the default VPC 
    subnets = ec2.describe_subnets(Filters=[{'Name':'vpc-id','Values':[vpc_id]}])['Subnets']
    subnet_ids = [ec2.delete_subnet(SubnetId=subnet['SubnetId']) for subnet in subnets]
    print(f"Deleting VPC {vpc_id} from region {region}")
    ec2.delete_vpc(VpcId=vpc_id)

# function to process a region  
def process_region(region):
    print(f"Processing region {region}")
    ec2 = boto3.client('ec2', region_name=region)
    vpc_filters = [{'Name':'isDefault','Values':['true']}]
    vpcs = ec2.describe_vpcs(Filters=vpc_filters)['Vpcs']
    if len(vpcs) == 0:
        print(f"No default VPC found in region {region}")
    elif len(vpcs) > 1:
        print(f"Multiple default VPCs found in region {region}")
    else:  # process default VPC
        print(f"Default VPC {vpcs[0]['VpcId']} found in region {region}")
        process_vpc(vpcs[0]['VpcId'], region)
    

# process each region
for region in regions:
    process_region(region)