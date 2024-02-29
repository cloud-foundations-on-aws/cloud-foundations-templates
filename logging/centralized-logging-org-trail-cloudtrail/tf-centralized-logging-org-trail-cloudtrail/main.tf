terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}
provider "aws" {
  region = "us-west-2"
}

variable "p_s3_bucket_name" {
  description = "Name for the S3 Bucket to hold AWS CloudTrail logging"
  type        = string
}

variable "p_trail_name" {
  description = "Name of the Cloud Trail"
  type        = string
}

resource "aws_cloudtrail" "example" {
  name                          = var.p_trail_name
  s3_bucket_name                = var.p_s3_bucket_name
  enable_logging = true
  enable_log_file_validation=true
  include_global_service_events=true
  is_multi_region_trail =true
  is_organization_trail=true
  event_selector {
	include_management_events=true
	read_write_type="All"
  }
}
