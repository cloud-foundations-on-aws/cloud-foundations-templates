# Sets the variable used for the management account id
# No default value is set
variable "management_account_id" {
  type = string
  description = "The account number of the account where Control Tower was deployed"
}

# Used to define the region to deploy the resources to 
variable "region" {
  type = string
  default = "us-east-1"
  description = "Home region where you have Control Tower deployed"
}