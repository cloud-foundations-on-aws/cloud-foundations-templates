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
  cConfigAccessLoggingBucket = format("%s-access-logs-%s",var.p_s3_bucket_name, data.aws_caller_identity.current.account_id)
  cConfigLoggingBucket = format("%s-%s",var.p_s3_bucket_name, data.aws_caller_identity.current.account_id)
}
 
/*
module "CreateAWSConfigAccessLoggingBucket" {
  source              = "./modules/s3-awsconfig-accesslogs-bucket"
  p_organization_id   = "13579"
  p_trail_account_id  = "12456"
  p_sse_algorithm     = "AES256"
  p_retention_days=365
  p_retention_days_for_access_logs=365
  p_s3_config_accesslogging_bucket = local.cConfigAccessLoggingBucket
  p_region = "us-west-2"
  p_transition_days = 22
  p_move_to_glacier=true
}
*/
module "CreateAWSConfigBucket" {
  source = "./modules/s3-awsconfig-bucket"
  p_s3_config_accesslogging_bucket = local.cConfigAccessLoggingBucket
  p_s3_config_bucket = local.cConfigLoggingBucket
  p_region = "us-west-2"
  p_transition_days = 22
  p_move_to_glacier=true
  p_retention_days 		= var.p_retention_days
  p_retention_days_for_access_logs=var.p_retention_days_for_access_logs
  p_organization_id   = "abc"
  p_trail_account_id  = "avb"
  p_trail_name=var.p_trail_name
}
