# Pulls in the data of the Organization
data "aws_organizations_organization" "org" {}

# Pulls in the data of current session to pull account id for later use
data "aws_caller_identity" "current" {}

# Pulls in the data of current partition to pull aws/gov/chn or region for later use
data "aws_partition" "current" {}

# Searches and pulls the account id for the Log Archive Account
locals {
  log_account = "Log Archive"
  formatted_list = [for name in data.aws_organizations_organization.org.accounts[*].name : lower(name)]
  log_index = index(local.formatted_list, lower(local.log_account))
  log_id = data.aws_organizations_organization.org.accounts[local.log_index].id
}

resource "aws_kms_key" "config_key" {
  description             = "AWS Config KMS Key"
  enable_key_rotation     = true 
}


resource "aws_kms_alias" "config_key_alias" {
  name          = "alias/${var.config_key_alias}"
  target_key_id = aws_kms_key.config_key.key_id
}

resource "aws_kms_key_policy" "config_key_policy" {
  key_id = aws_kms_key.config_key.id
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
        Sid       = "Allow Config to use KMS for encryption"
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
