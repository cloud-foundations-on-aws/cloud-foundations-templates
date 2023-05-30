# Sets the provider for AWS with region defined in vars file
# Note this uses default aws credentials on the local machine
provider "aws" {
  region = var.region
}

provider "aws" {
  alias = "security"
  region = var.region
  assume_role {
    # Assumes the role for Security/Audit account for deployment.
    role_arn    = "arn:aws:iam::${local.audit_id}:role/AWSControlTowerExecution"
  }
}