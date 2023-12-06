variable "p_s3_bucket_name" {
  description = "Name for the S3 Bucket to hold AWS CloudTrail logging"
  type        = string
}
variable "p_s3_logging_bucket" {
  description = "Name for the S3 Bucket to hold AWS CloudTrail logging"
  type        = string
}

variable "p_retention_days" {
  description = "Number of Days to retain the logs, after which it will be permanently deleted"
  type        = string
}

variable "p_retention_days_for_access_logs" {
  description = "Number of Days to retain the access logs, after which it will be permanently deleted"
  type        = string
}

variable "p_organization_id" {
  description = "Organization Id for the management account."
  type        = string
}

variable "p_trail_account_id" {
  description = "The AWS account Id which the CloudTrail Organization Trail exists in."
  type        = string
}
variable "p_trail_name" {
  description = "The name of the Organization Trail for CloudTrail"
  type        = string
  default     = "aws-cloudtrail-org"
}
variable "p_region" {
  description = "The region to deploy into."
  type        = string
}