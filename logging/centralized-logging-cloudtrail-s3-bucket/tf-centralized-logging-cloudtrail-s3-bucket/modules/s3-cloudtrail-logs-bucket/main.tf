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

provider "aws" {
  region = var.p_region
}

resource "aws_s3_bucket" "example" {
  bucket = var.p_s3_logging_bucket
  
}
resource "aws_s3_bucket_versioning" "versioning_example" {
  bucket = aws_s3_bucket.example.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_logging" "example" {
  bucket = aws_s3_bucket.example.id

  target_bucket = aws_s3_bucket.example.id
  target_prefix = ""
}
resource "aws_s3_bucket_ownership_controls" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
resource "aws_s3_bucket_acl" "log_bucket_acl" {
  bucket = aws_s3_bucket.example.id
  acl    = "log-delivery-write"
  depends_on = [aws_s3_bucket_ownership_controls.example]
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.example.id

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

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id
	
  rule {
			apply_server_side_encryption_by_default {
			  sse_algorithm     = "AES256"
			}
		}
  
  
}

resource "aws_s3_bucket_policy" "allow_access_from_another_account" {
  bucket = aws_s3_bucket.example.id
  policy = data.aws_iam_policy_document.allow_access_from_another_account_2.json
}

data "aws_iam_policy_document" "allow_access_from_another_account_2" {
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
      aws_s3_bucket.example.arn,
      "${aws_s3_bucket.example.arn}/*",
    ]
	
	condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = [false]
    }
  }
}

