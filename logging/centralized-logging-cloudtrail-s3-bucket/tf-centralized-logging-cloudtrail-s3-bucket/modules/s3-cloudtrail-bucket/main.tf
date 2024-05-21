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


resource "aws_s3_bucket" "cloudtrail-bucket" {
  bucket = format("%s-%s",var.p_s3_bucket_name, data.aws_caller_identity.current.account_id)
  
}
resource "aws_s3_bucket_versioning" "versioning_example" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_logging" "cloudtrail-bucket" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id

  target_bucket = var.p_s3_logging_bucket 
  target_prefix = ""
}
resource "aws_s3_bucket_ownership_controls" "cloudtrail-bucket" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
resource "aws_s3_bucket_public_access_block" "cloudtrail-bucket" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail-bucket" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id

  rule {
    id = "retention-rule"
    status = "Enabled"
	expiration {
      days = var.p_retention_days_for_access_logs
    }
	noncurrent_version_expiration {
      noncurrent_days = var.p_retention_days_for_access_logs
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail-bucket" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id
	
  rule {
			apply_server_side_encryption_by_default {
			  sse_algorithm     = "AES256"
			}
		}  
  
}


resource "aws_s3_bucket_policy" "allow_access_from_another_account" {
  bucket = aws_s3_bucket.cloudtrail-bucket.id
  policy = data.aws_iam_policy_document.s3_cloud_trail_bucket_policy.json
}

data "aws_iam_policy_document" "s3_cloud_trail_bucket_policy" {
  statement {
	sid = "AWSCloudTrailAclCheck"
	effect = "Allow"
	principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
	actions = ["s3:GetBucketAcl"]
	resources = [
	  format("arn:%s:s3:::%s", data.aws_partition.current.partition,aws_s3_bucket.cloudtrail-bucket.id)
    ]
	condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = [format("arn:%s:cloudtrail:%s:%s:trail/%s", data.aws_partition.current.partition, var.p_region ,var.p_trail_account_id, var.p_trail_name)]
    }
  }
  
    statement {
	sid = "AWSCloudTrailWrite"
	effect = "Allow"
	principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
	actions = ["s3:PutObject"]
	resources = [
	  format("arn:%s:s3:::%s/AWSLogs/*", data.aws_partition.current.partition,aws_s3_bucket.cloudtrail-bucket.id)
    ]
	condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
	condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = [format("arn:%s:cloudtrail:%s:%s:trail/%s", data.aws_partition.current.partition, var.p_region ,var.p_trail_account_id, var.p_trail_name)]
    }
	
  }
  
	statement {
	sid = "AWSCloudTrailOrganizationWrite"
	effect = "Allow"
	principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
	actions = ["s3:PutObject"]
	resources = [
	  format("arn:%s:s3:::%s/AWSLogs/%s/*", data.aws_partition.current.partition,aws_s3_bucket.cloudtrail-bucket.id, var.p_organization_id)
    ]
	
  }
  
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
      aws_s3_bucket.cloudtrail-bucket.arn,
      "${aws_s3_bucket.cloudtrail-bucket.arn}/*",
    ]
	
	condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = [false]
    }
  }
}