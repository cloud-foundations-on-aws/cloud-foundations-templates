# Network Default VPC deletion

This script will look for and delete default VPCs and associated resources (subnets, IGWs) in all AWS regions of an
 account.

## Description

This Bash script deletes the default VPCs in all regions of an AWS account. The script retrieves a list of regions
 from AWS and deletes the default VPC for each region. The script also detaches and deletes any Internet Gateways (IGWs) attached to the default VPC, as well as any subnets in the default VPC.

## How to Use

This script can be executed locally with [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) with the appropriate [configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) or it can be executed from [CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html) by cloning this repo to your CloudShell instance or by [uploading the file to CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-cloudshell.html#:~:text=To%20upload%20files%20to%20AWS%20CloudShell).

1. Open a terminal and navigate to the directory where the script is saved.
2. Run the script by typing `./delete-default-vpcs.sh`.
3. A list of regions will be displayed, and the script will begin processing each region.
4. The output of each region will print out to the console.

>**Note** Script requires JQ to be installed.

## Usage

`./network-default-vpc-deletion.sh`

If you choose not to download the script you can run it directly via curl:

```sh
curl -fsS https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/network/scripts/network-default-vpc-deletion/network-default-vpc-deletion.sh | bash
```
