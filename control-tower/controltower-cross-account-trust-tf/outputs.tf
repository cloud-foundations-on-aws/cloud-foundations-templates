output "cross_account_role_arn" {
  value = aws_iam_role.ct_exe_role.arn
  description = "Arn value of the cross account role for Control Tower "
}