# Management Account Identity Center Assignments

From the management account in AWS IAM Identity Center, you will need to assign your users to a permission set and to the management account. It is best practice to assign only users and not groups to the management account administrator assignment. Groups can be updated in the IAM Identity Center delegated admin account and could give unauthorized access to the management account.

Follow the instructions below assigning your management account users to both the MA-Administrator and MA-ReadOnly permission sets:

1. Access AWS accounts in AWS IAM Identity Center.
2. Select the checkbox next to your management AWS account.
3. Select Assign users and then select the user accounts you created for management account administration
4. Select Next then select MA-Administrator or MA-ReadOnly for permission set

The assignment will complete and your management account administrative users should be able to login and have access to the management account.

## Terraform Directory

The Terraform Directory creates two assignments for AWS Identity Users. Deploy this in your AWS Management account under the region your Identity Center is deployed in.

## Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `region` | String | `us-east-1` | Region to deploy the Terraform code to |
| `ma_admin_users` | List |   | List of user names/emails to assign MA-Administrator access to. Example: `exampleuser@example.com` |
| `ma_read_only_users` | List |   | List of user names/emails to assign MA-ReadOnly access to. Example: `exampleuser@example.com` |

# Usage

## Pre-requisites

Prior to using this repo you will need awscli and terraform installed on the system running the code. Links to instructions below:

* [AWSCLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* [Terraform Download](https://www.terraform.io/downloads.html)
* [Terraform Install Guide](https://learn.hashicorp.com/terraform/getting-started/install)

# Running the Code

* [TF Cheatsheet](https://res.cloudinary.com/acloud-guru/image/fetch/c_thumb,f_auto,q_auto/https:/acg-wordpress-content-production.s3.us-west-2.amazonaws.com/app/uploads/2020/11/terraform-cheatsheet-from-ACG.pdf)

This directory is intended to be run locally

Getting started you'll need to open a `terminal` window and change direcotries to the working directory

Next you need to instantiate the terraform working environment by running the following command `terraform init`

Once complete you're ready to use terraform to deploy the resources defined in `main.tf`. It's recommended to do a dry run first by running the command `terraform plan`
This will show you what changes are going to happen without *any* chance of it deploying

```
Terraform will perform the following actions:

  # aws_ssoadmin_account_assignment.ma_admin_assignment[0] will be created
  + resource "aws_ssoadmin_account_assignment" "ma_admin_assignment" {
      + id                 = (known after apply)
      + instance_arn       = "arn:aws:sso:::instance/ssoins-XXXXXXXXXXXXXX"
      + permission_set_arn = "arn:aws:sso:::permissionSet/ssoins-XXXXXXXXXXXXXX/ps-YYYYYYYYYYY"
      + principal_id       = "<USERID>"
      + principal_type     = "USER"
      + target_id          = "<ACCOUNTID>"
      + target_type        = "AWS_ACCOUNT"
    }

  # aws_ssoadmin_account_assignment.ma_read_only_assignment[0] will be created
  + resource "aws_ssoadmin_account_assignment" "ma_read_only_assignment" {
      + id                 = (known after apply)
      + instance_arn       = "arn:aws:sso:::instance/ssoins-XXXXXXXXXXXXXX"
      + permission_set_arn = "arn:aws:sso:::permissionSet/ssoins-XXXXXXXXXXXXXX/ps-YYYYYYYYYYY"
      + principal_id       = "<USERID>"
      + principal_type     = "USER"
      + target_id          = "<ACCOUNTID>"
      + target_type        = "AWS_ACCOUNT"
    }

Plan: 2 to add, 0 to change, 0 to destroy.

```
To build out the resources defined use the command `terrafrom apply` 
This will provide the same output as above but now you'll be prompted to confirm the build/changes

In order to remove the resources from your environment run the command `terraform destroy`
When using in practice take *EXTREME* caution using this command as it will remove *ALL* resources defined/managed in the `.statefile`