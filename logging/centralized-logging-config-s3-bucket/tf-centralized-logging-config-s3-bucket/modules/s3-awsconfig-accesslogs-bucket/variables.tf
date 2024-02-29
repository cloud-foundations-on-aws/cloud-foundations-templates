variable "p_region" {
  description = "The region to deploy into."
  type        = string
}

variable "p_s3_config_accesslogging_bucket" {
  description = "Name for the S3 Bucket to hold AWS CloudTrail logging"
  type        = string
}

variable "p_move_to_glacier" {
  description = "Do you wish to transition the logs to Glacier before permanently deleting"
  type        = string
}

variable "p_sse_algorithm" {
  description = "S3 bucket SSE Algorithm."
  type        = string
  validation {
    condition     = contains(["AES256", "aws:kms"], var.p_sse_algorithm)
    error_message = "Valid values for var: S3 bucket SSE Algorithm are (AES256, aws:kms)."
  }
}
variable "p_transition_days" {
  description = "Number of Days to retain the logs, after which it will be permanently deleted"
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

