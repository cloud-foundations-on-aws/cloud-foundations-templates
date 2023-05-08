# Control Tower Cross Account Trust

The following template deploys an execution role in the your account(s) which can be assumed by Control Tower from the management account. Use this template prior to enroll existing accounts into your Control Tower environment. Without deploying the role/trust in the target account, Control Tower will be unable to access the account and therefore unable to enroll the account. For more information visit [Manually add the required IAM role to an existing AWS account and enroll it](https://docs.aws.amazon.com/controltower/latest/userguide/enroll-manually.html) in the Control Tower documentation.

Be sure to review the [Prerequisites for enrollment](https://docs.aws.amazon.com/controltower/latest/userguide/enrollment-prerequisites.html) as described in the Control Tower documentation.

> **Info:** The deployment will fail to provision if the account was created by Control Tower account factory or someone manually created the role. Use this template only for accounts created outside of Control Tower account factory.

## Terraform Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| management_account_id | String | | Management account id which AWS Control Tower is deployed in. |


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

  # aws_iam_role.ct_exe_role will be created
  + resource "aws_iam_role" "ct_exe_role" {
      + arn                   = (known after apply)
      + assume_role_policy    = jsonencode(
            {
              + Statement = [
                  + {
                      + Action    = "sts:AssumeRole"
                      + Effect    = "Allow"
                      + Principal = {
                          + AWS = "175039216299"
                        }
                      + Sid       = ""
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + create_date           = (known after apply)
      + force_detach_policies = false
      + id                    = (known after apply)
      + managed_policy_arns   = [
          + "arn:aws:iam::aws:policy/AdministratorAccess",
        ]
      + max_session_duration  = 3600
      + name                  = "AWSControlTowerExecution"
      + name_prefix           = (known after apply)
      + path                  = "/"
      + role_last_used        = (known after apply)
      + tags_all              = (known after apply)
      + unique_id             = (known after apply)

      + inline_policy {
          + name   = (known after apply)
          + policy = (known after apply)
        }
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + cross_account_role_arn = (known after apply)
```
To build out the resources defined use the command `terrafrom apply` 
This will provide the same output as above but now you'll be prompted to confirm the build/changes

```

In order to remove the resources from your environment run the command `terraform destroy`
When using in practice take *EXTREME* caution using this command as it will remove *ALL* resources defined/managed in the `.statefile`