variable "management_account_id" {
  type = string
  description = "The account number of the account where Control Tower was deployed"
}

variable "region" {
  type = string
  default = "us-east-1"
  description = "Home region where you have Control Tower deployed"
}