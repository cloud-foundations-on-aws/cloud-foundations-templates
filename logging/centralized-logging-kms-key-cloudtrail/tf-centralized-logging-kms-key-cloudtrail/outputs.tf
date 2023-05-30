#Output file for resources deployed

output "ct_key" {
  value = aws_kms_key.ct_key.arn
  description = "Arn Value of the KMS key"
}