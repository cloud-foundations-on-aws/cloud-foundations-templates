variable p_root_org_id {
  description = "Organization root Id (r-xxxx)"
  type = string
}

variable p_log_archive_account_name {
  description = "alias (AWS account name) for the production log archive account"
  type = string
  default = "Log Archive"
}

variable p_log_archive_account_email {
  description = "root user email address for the production log archive account. Example: aws-log-archive-[org-identifier]@example.com"
  type = string
}

variable p_security_tooling_account_name {
  description = "alias (AWS account name) for the production security account"
  type = string
  default = "Security Tooling"
}

variable p_security_tooling_account_email {
  description = "root user email address for the production security tooling account. Example: aws-security-tooling-[org-identifier]@example.com"
  type = string
}

resource "aws_organizations_organizational_unit" "r_exceptions_ou" {
  name = "Exceptions"
  parent_id = var.p_root_org_id
}

resource "aws_organizations_organizational_unit" "r_infrastructure_ou" {
  name = "Infrastructure"
  parent_id = var.p_root_org_id
}

resource "aws_organizations_organizational_unit" "r_security_ou" {
  name = "Security"
  parent_id = var.p_root_org_id
}

resource "aws_organizations_organizational_unit" "r_sandbox_ou" {
  name = "Sandbox"
  parent_id = var.p_root_org_id
}

resource "aws_organizations_organizational_unit" "r_workloads_ou" {
  name = "Workloads"
  parent_id = var.p_root_org_id
}

resource "aws_organizations_account" "r_log_archive_prod_account" {
  name = var.p_log_archive_account_name
  email = var.p_log_archive_account_email
  parent_id = aws_organizations_organizational_unit.r_security_ou.id
}

resource "aws_organizations_account" "r_security_tooling_prod_account" {
  name = var.p_security_tooling_account_name
  email = var.p_security_tooling_account_email
  parent_id = aws_organizations_organizational_unit.r_security_ou.id
}