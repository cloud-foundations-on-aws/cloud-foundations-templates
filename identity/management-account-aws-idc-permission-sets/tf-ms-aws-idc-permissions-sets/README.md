# Management Account Identity Center Permissions Sets

From your AWS management account in  AWS IAM Identity Center, you will need to add/create the permission set for your management account administrators. Note that any permission set assigned to the management account cannot be leveraged or edited from the AWS IAM Identity Center delegated admin AWS account.

Follow the [Create a permission set](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtocreatepermissionset.html) instructions from the AWS Identity Center documentation to create the following permission sets or deploy the CloudFormation template in this directory.

> **Note:** that the MA-Administrator permissions set leverages a *Predefined permission set*, whereas the MA-ReadOnly uses a *Custom permission set*:

## MA-Administrator

<table>
<tr><th>Permission Set Name:</th><td>MA-Administrator</td></tr>
<tr><th>Permission Set Type:</th><td>Predefined</td></tr>
<tr><th>Description:</th><td> Gives administrative access to the management account</td></tr>
<tr><th>Tags:</th><td>Add your defined mandatory tags to this permission set</td></tr>
<tr><th>Associated Policies:</th><td>  Predefined permission set: AdministratorAccess</td></tr>
</table>

## MA-ReadOnly

<table>
<tr><th>Permission Set Name:</th><td> MA-ReadOnly</td></tr>
<tr><th>Permission Set Type:</th><td> Custom</td></tr>
<tr><th>Description:</th><td> Gives read-only access to the management account</td></tr>
<tr><th>Tags:</th><td> Add your defined mandatory tags to this permission set</td></tr>
<tr><th>Associated Policies:</th><td> Custom Permission set: AWS managed policy ReadOnlyAccess</td></tr>
</table>

## Terraform Directory

The Terraform direcotry creates two permissions set for AWS Identity Users accessing the management account. Deploy the directory in your AWS Management account under the region your Identity Center is deployed in.

## Terraform Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `region` | String | `us-east-1` | Region to deploy the Terraform code to |
| `ma_admin_session` | String |  `PT1H` | The length of time that the MA-Administrator user sessions are valid for in the ISO-8601 standard |
| `ma_read_only_session` | String | `PT1H` | The length of time that the MA-ReadOnly user sessions are valid for in the ISO-8601 standard. |

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
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the
following symbols:
  + create

Terraform will perform the following actions:

  # aws_ssoadmin_permission_set.ma_admin will be created
  + resource "aws_ssoadmin_permission_set" "ma_admin" {
      + arn              = (known after apply)
      + created_date     = (known after apply)
      + description      = "MA-Administrator access permission set"
      + id               = (known after apply)
      + instance_arn     = "arn:aws:sso:::instance/ssoins-XXXXXXXXXXXXX"
      + name             = "MA-Administrator"
      + session_duration = "PT1H"
      + tags_all         = (known after apply)
    }

  # aws_ssoadmin_permission_set.ma_read_only will be created
  + resource "aws_ssoadmin_permission_set" "ma_read_only" {
      + arn              = (known after apply)
      + created_date     = (known after apply)
      + description      = "MA-ReadOnly access permission set"
      + id               = (known after apply)
      + instance_arn     = "arn:aws:sso:::instance/ssoins-XXXXXXXXXXXXX"
      + name             = "MA-ReadOnly"
      + session_duration = "PT1H"
      + tags_all         = (known after apply)
    }

Plan: 2 to add, 0 to change, 0 to destroy.
```
To build out the resources defined use the command `terrafrom apply` 
This will provide the same output as above but now you'll be prompted to confirm the build/changes

In order to remove the resources from your environment run the command `terraform destroy`
When using in practice take *EXTREME* caution using this command as it will remove *ALL* resources defined/managed in the `.statefile`