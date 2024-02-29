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
data "aws_partition" "current" {}

provider "aws" {
  region = var.p_region
}


resource "aws_s3_bucket" "awsconfig-bucket" {
  bucket = var.p_s3_config_bucket
  
}
resource "aws_s3_bucket_versioning" "awsconfig-bucket" {
  bucket = aws_s3_bucket.awsconfig-bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_logging" "awsconfig-bucket" {
  bucket = aws_s3_bucket.awsconfig-bucket.id

  target_bucket = var.p_s3_config_accesslogging_bucket 
  target_prefix = ""
}
resource "aws_s3_bucket_ownership_controls" "awsconfig-bucket" {
  bucket = aws_s3_bucket.awsconfig-bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
resource "aws_s3_bucket_public_access_block" "awsconfig-bucket" {
  bucket = aws_s3_bucket.awsconfig-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.awsconfig-bucket.id

	dynamic "rule" {
		for_each = var.p_move_to_glacier ? [1] : []
		content{	
					id = "retention-rule"
					status = "Enabled"
					expiration {
					  days = var.p_retention_days_for_access_logs
					}
					noncurrent_version_expiration {
					  noncurrent_days = var.p_retention_days_for_access_logs
					}
					transition {
						days=var.p_transition_days
						storage_class="GLACIER"
					}
					noncurrent_version_transition {
						noncurrent_days =var.p_transition_days
						storage_class="GLACIER"
					}
			}
	}
	
		dynamic "rule" {
		for_each = var.p_move_to_glacier ? [] : [1]
		content{		
					id = "retention-rule"
					status = "Enabled"
					expiration {
					  days = 	var.p_retention_days_for_access_logs
					}
					noncurrent_version_expiration {
					  noncurrent_days = var.p_retention_days_for_access_logs
					}
			}
	}
  
}

resource "aws_s3_bucket_server_side_encryption_configuration" "awsconfig-bucket" {
  bucket = aws_s3_bucket.awsconfig-bucket.id
	
  rule {
			apply_server_side_encryption_by_default {
			  sse_algorithm     = "AES256"
			}
		}  
  
}


resource "aws_s3_bucket_policy" "aws_config_bucket_policy" {
  bucket = aws_s3_bucket.awsconfig-bucket.id
  policy = data.aws_iam_policy_document.s3_aws_config_bucket_policy.json
}

data "aws_iam_policy_document" "s3_aws_config_bucket_policy" {

	  statement {
		sid = "AllowSSLRequestsOnly"
		effect = "Deny"
		principals {
		  type        = "AWS"
		  identifiers = ["*"]
		}

		actions = [
		  "s3:*"
		]

		resources = [
		  aws_s3_bucket.awsconfig-bucket.arn,
		  "${aws_s3_bucket.awsconfig-bucket.arn}/*",
		]
		
		condition {
		  test     = "Bool"
		  variable = "aws:SecureTransport"
		  values   = [false]
		}
	  }
	  
	  statement {
		sid = "AWSBucketPermissionsCheck"
		effect = "Allow"
		principals {
		  type        = "Service"
		  identifiers = ["config.amazonaws.com"]
		}
		actions = ["s3:GetBucketAcl"]
		resources = [
		  format("arn:%s:s3:::%s", data.aws_partition.current.partition,aws_s3_bucket.awsconfig-bucket.id)
		]
	  }
	  
	  statement {
		sid = "AWSConfigBucketExistenceCheck"
		effect = "Allow"
		principals {
		  type        = "Service"
		  identifiers = ["cloudtrail.amazonaws.com"]
		}
		actions = ["s3:ListBucket"]
		resources = [
		  format("arn:%s:s3:::%s", data.aws_partition.current.partition,aws_s3_bucket.awsconfig-bucket.id)
		]
		
	  }
  
    statement {
		sid = "AWSBucketDeliveryForConfig"
		effect = "Allow"
		principals {
		  type        = "Service"
		  identifiers = ["config.amazonaws.com"]
		}
		actions = ["s3:PutObject"]
		resources = [
		  format("arn:%s:s3:::%s/AWSLogs/*/*", data.aws_partition.current.partition,aws_s3_bucket.awsconfig-bucket.id)
		]
		
	
  }
  
	
  

}