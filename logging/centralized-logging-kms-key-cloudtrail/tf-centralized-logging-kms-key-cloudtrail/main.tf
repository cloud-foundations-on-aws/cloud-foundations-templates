# Pulls in the data of the Organization
data "aws_organizations_organization" "org" {}

# Pulls in the data of current session to pull account id for later use
data "aws_caller_identity" "current" {
  provider = aws.security
}

# Pulls in the data of current partition to pull aws/gov/chn or region for later use
data "aws_partition" "current" {}

# Searches and pulls the account id for the Log Archive Account
locals {
  log_account = "Log Archive"
  audit_account = "Audit"
  formatted_list = [for name in data.aws_organizations_organization.org.accounts[*].name : lower(name)]
  log_index = index(local.formatted_list, lower(local.log_account))
  audit_index = index(local.formatted_list, lower(local.audit_account))
  log_id = data.aws_organizations_organization.org.accounts[local.log_index].id
  audit_id = data.aws_organizations_organization.org.accounts[local.audit_index].id
}

resource "aws_kms_key" "ct_key" {
  provider = aws.security
  description             = "AWS Cloudtrail KMS Key"
  enable_key_rotation     = true 
}


resource "aws_kms_alias" "ct_key_alias" {
  provider = aws.security
  name          = "alias/${var.ct_key_alias}"
  target_key_id = aws_kms_key.ct_key.key_id
}

resource "aws_kms_key_policy" "ct_key_policy" {
  provider = aws.security
  key_id = aws_kms_key.ct_key.id
  policy = jsonencode({
    Id = "example"
    Statement = [
      {
        Sid       = "Enable IAM User Permissions"
        Principal = {
          AWS = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action    = "kms:*"
        Effect    = "Allow"
        Resource  = "*"
      },
      {
        Sid       = "Allow Cloudtrail to use KMS for encryption"
        Principal = {
          AWS = "arn:${data.aws_partition.current.partition}:iam::${data.aws_organizations_organization.org.master_account_id}:root"
        }
        Action    = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Effect    = "Allow"
        Resource  = "*"
      },
      {
        Sid       = "Allow Log Archive and Management account access"
        Principal = {
          AWS = [
            "arn:${data.aws_partition.current.partition}:iam::${data.aws_organizations_organization.org.master_account_id}:root",
            "arn:${data.aws_partition.current.partition}:iam::${local.log_id}:root"
          ]
        }
        Action    = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Effect    = "Allow"
        Resource  = "*"
      },
    ]
    Version = "2012-10-17"
  })
}
