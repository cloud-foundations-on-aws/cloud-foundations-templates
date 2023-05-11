# Pulls in data of existing Identity Center Instance
data "aws_ssoadmin_instances" "identity_center" {}

# Pulls in the data of current session to pull account id for later use
data "aws_caller_identity" "current" {}

# Pulls in the data of existing MA-Administrator Permission Set
# Assumes you used the other deployment and have same naming convention
data "aws_ssoadmin_permission_set" "ma_admin" {
  instance_arn = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  name         = "MA-Administrator"
}

# Pulls in the data of existing MA-ReadOnly Permission Set
# Assumes you used the other deployment and have same naming convention
data "aws_ssoadmin_permission_set" "ma_read_only" {
  instance_arn = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  name         = "MA-ReadOnly"
}

# Pulls data on user name to get id for assignment later
data "aws_identitystore_user" "ma_admin_users" {
  count = length(var.ma_admin_users)
  identity_store_id = tolist(data.aws_ssoadmin_instances.identity_center.identity_store_ids)[0]

  alternate_identifier {
    unique_attribute {
      attribute_path  = "UserName"
      attribute_value = var.ma_admin_users[count.index]
    }
  }
}

# Pulls data on user name to get id for assignment later
data "aws_identitystore_user" "ma_read_only_users" {
  count = length(var.ma_read_only_users)
  identity_store_id = tolist(data.aws_ssoadmin_instances.identity_center.identity_store_ids)[0]

  alternate_identifier {
    unique_attribute {
      attribute_path  = "UserName"
      attribute_value = var.ma_read_only_users[count.index]
    }
  }
}

# Assigns users to the MA-Administrator Permission Set
resource "aws_ssoadmin_account_assignment" "ma_admin_assignment" {
  count = length(var.ma_admin_users)
  instance_arn       = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  permission_set_arn = data.aws_ssoadmin_permission_set.ma_admin.arn

  principal_id   = data.aws_identitystore_user.ma_admin_users.*.id[count.index]
  principal_type = "USER"

  target_id   = data.aws_caller_identity.current.account_id
  target_type = "AWS_ACCOUNT"
}

# Assigns users to the MA-ReadOnly Permission Set
resource "aws_ssoadmin_account_assignment" "ma_read_only_assignment" {
  count = length(var.ma_read_only_users)
  instance_arn       = tolist(data.aws_ssoadmin_instances.identity_center.arns)[0]
  permission_set_arn = data.aws_ssoadmin_permission_set.ma_read_only.arn

  principal_id   = data.aws_identitystore_user.ma_read_only_users.*.id[count.index]
  principal_type = "USER"

  target_id   = data.aws_caller_identity.current.account_id
  target_type = "AWS_ACCOUNT"
}