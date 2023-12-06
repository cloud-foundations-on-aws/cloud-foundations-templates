variable "availability_zone_names" {
  type    = list(string)
  default = ["us-west-1a"]
}

variable "p_s3_bucket_name" {
  description = "Name for the S3 Bucket to hold AWS CloudTrail logging"
  type        = string
  default     = "aws-config-logs"
}


variable "p_retention_days" {
  description = "Number of Days to retain the logs, after which it will be permanently deleted"
  type        = string
  default     = "365"
}

variable "p_retention_days_for_access_logs" {
  description = "Number of Days to retain the access logs, after which it will be permanently deleted"
  type        = string
  default     = "365"
}

variable "p_organization_id" {
  description = "Organization Id for the management account."
  type        = string
  default     = "SomeOrgId"
}

variable "p_trail_account_id" {
  description = "The AWS account Id which the CloudTrail Organization Trail exists in."
  type        = string
  default     = "123456"
}

variable "p_trail_name" {
  description = "The name of the Organization Trail for CloudTrail"
  type        = string
  default     = "aws-config-org"
}