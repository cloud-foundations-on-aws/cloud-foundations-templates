#Structured way to implement IAM Policy
data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [var.management_account_id]
    }
  }
}

#IAM Role needed for Control Tower
resource "aws_iam_role" "ct_exe_role" {
  name                = "AWSControlTowerExecution"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess"] #Admin access as required by CT
}