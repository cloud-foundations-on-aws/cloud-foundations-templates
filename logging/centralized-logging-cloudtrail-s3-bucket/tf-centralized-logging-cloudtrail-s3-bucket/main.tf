terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

data "aws_caller_identity" "current" {}

locals {
  cLoggingBucket = format("%s-access-logs-%s",var.p_s3_bucket_name, data.aws_caller_identity.current.account_id)
  cCloudTrailBucketBucket = format("%s-%s",var.p_s3_bucket_name, data.aws_caller_identity.current.account_id)
}
 

module "CreateLoggingBucket" {
  source              = "./modules/s3-cloudtrail-logs-bucket"
  p_organization_id   = "13579"
  p_trail_account_id  = "12456"
  p_retention_days=365
  p_retention_days_for_access_logs=365
  p_s3_logging_bucket = local.cLoggingBucket
  p_s3_bucket_name = var.p_s3_bucket_name
  p_region = "us-west-2"
}

module "CreateCloudTrailBucket" {
  source = "./modules/s3-cloudtrail-bucket"
  p_s3_bucket_name     = var.p_s3_bucket_name
  p_s3_logging_bucket = local.cLoggingBucket
  p_retention_days 		=var.p_retention_days
  p_retention_days_for_access_logs=var.p_retention_days_for_access_logs
  p_organization_id   = "abc"
  p_trail_account_id  = "avb"
  p_region = "us-west-2"
  p_trail_name=var.p_trail_name
}
