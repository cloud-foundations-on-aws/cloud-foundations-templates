# Used to define the region to deploy the resources to 
variable "region" {
  type = string
  default = "us-east-2"
  description = "Home region where you have Identity Center deployed"
}

variable "ma_admin_users" {
  type = list
  description = "List of user names for MA-Administrator Access (e.g. exampleuser@example.com)"
}

variable "ma_read_only_users"{
  type = list
  description = "List of user names for MA-ReadOnly Access (e.g. exampleuser@example.com)"
}