#Output file for resources deployed

output "config_key" {
  value = aws_kms_key.config_key.arn
  description = "Arn Value of the KMS key"
}