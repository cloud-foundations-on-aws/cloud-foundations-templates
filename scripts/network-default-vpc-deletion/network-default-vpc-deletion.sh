#!/usr/bin/env bash

# get list of regions
export REGIONS=$(aws ec2 describe-regions | jq -r ".Regions[].RegionName")

# function to process a region
process_region() {
    local region="$1"
    echo "Processing region $region"

    # get default VPC ID
    local vpc_id=$(aws --region="$region" ec2 describe-vpcs --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text)

    # get list of IGWs attached to the default VPC
    local igw_ids=$(aws --region="$region" ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values="$vpc_id" --query "InternetGateways[].InternetGatewayId" --output text)

    # detach and delete IGWs
    for igw_id in $igw_ids; do
        echo "Detaching and deleting IGW $igw_id in region $region"
        aws --region="$region" ec2 detach-internet-gateway --internet-gateway-id="$igw_id" --vpc-id="$vpc_id"
        aws --region="$region" ec2 delete-internet-gateway --internet-gateway-id="$igw_id"
    done

    # get list of subnet IDs in the default VPC
    local subnet_ids=$(aws --region="$region" ec2 describe-subnets --filters Name=vpc-id,Values="$vpc_id" --query "Subnets[].SubnetId" --output text)

    # delete subnets
    for subnet_id in $subnet_ids; do
        echo "Deleting subnet $subnet_id in region $region"
        aws --region="$region" ec2 delete-subnet --subnet-id="$subnet_id"
    done

    # delete default VPC
    if [ "$vpc_id" == "None" ]; then
      echo "No default VPC found"
    else
      echo "Deleting default VPC in region $region"
      aws --region="$region" ec2 delete-vpc --vpc-id="$vpc_id"
    fi
}


for region in $REGIONS; do
    # list vpcs
    echo $region
    process_region $region
    echo
done
