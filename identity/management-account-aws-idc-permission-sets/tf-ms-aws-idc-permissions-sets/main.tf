# Pulls in data of existing Identity Center Instance
data "aws_ssoadmin_instances" "identity_center" {}

# Permission set for MA Admin
resource "aws_ssoadmin_permission_set" "ma_admin" {
  name             = "MA-Administrator"
  description      = "MA-Administrator access permission set"
  instance_arn     = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  session_duration = var.ma_admin_session
  /* Tag Block, use as necessary for implementation
  tags = {
    "key1" = "value1"
    "key2" = "value2"
  }
  */
}

# Attaches admin policy to MA-Admin permission set
resource "aws_ssoadmin_managed_policy_attachment" "ma_admin_policy" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.ma_admin.arn
}

# Permission set for MA ReadOnly
resource "aws_ssoadmin_permission_set" "ma_read_only" {
  name             = "MA-ReadOnly"
  description      = "MA-ReadOnly access permission set"
  instance_arn     = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  session_duration = var.ma_read_only_session
  /* Tag Block, use as necessary for implementation
  tags = {
    "key1" = "value1"
    "key2" = "value2"
  }
  */
}

# Attaches read only policy to MA-ReadOnly permission set
resource "aws_ssoadmin_managed_policy_attachment" "ma_read_only_policy" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.ma_read_only.arn
}