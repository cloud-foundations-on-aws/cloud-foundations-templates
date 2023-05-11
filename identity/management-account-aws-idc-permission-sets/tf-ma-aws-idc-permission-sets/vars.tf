# Used to define the region to deploy the resources to 
variable "region" {
  type = string
  default = "us-east-2"
  description = "Home region where you have Identity Center deployed"
}

# MA-Admin Duration
variable "ma_admin_session" {
  type = string
  default = "PT1H"
  description = "The length of time that the MA-Administrator user sessions are valid for in the ISO-8601 standard"
  validation {
    condition     = can(regex("^PT[1-9]H|^PT1[0-2]H", var.ma_admin_session))
    error_message = "Must be PT<1-12>H (eg PT1H or PT12H)"
  }
}

# MA-Admin Duration
variable "ma_read_only_session" {
  type = string
  default = "PT1H"
  description = "The length of time that the MA-ReadOnly user sessions are valid for in the ISO-8601 standard"
  validation {
    condition     = can(regex("^PT[1-9]H|^PT1[0-2]H", var.ma_read_only_session))
    error_message = "Must be PT<1-12>H (eg PT1H or PT12H)"
  }
}
