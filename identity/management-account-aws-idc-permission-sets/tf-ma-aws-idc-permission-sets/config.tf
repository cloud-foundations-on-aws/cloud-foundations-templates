# Sets the provider for AWS with region defined in vars file
# Note this uses default aws credentials on the local machine
provider "aws" {
  region = var.region
}