# Used to define the region to deploy the resources to 
variable "region" {
  type = string
  default = "us-east-1"
  description = "Home region where you have Control Tower deployed"
}

# Name of the config kms key
variable "config_key_alias" {
  type = string
  default = "config-org-key"
  description = "Config KMS Key Alias"
}
