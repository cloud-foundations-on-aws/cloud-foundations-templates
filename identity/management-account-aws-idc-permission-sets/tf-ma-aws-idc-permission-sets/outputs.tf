#Output file for resources deployed

output "ma_admin_permission_set_arn" {
  value = aws_ssoadmin_permission_set.ma_admin.arn
  description = "Arn value of the MA-Administrator Permission Set"
}

output "ma_read_only_permission_set_arn" {
  value = aws_ssoadmin_permission_set.ma_read_only.arn
  description = "Arn value of the MA-Administrator Permission Set"
}