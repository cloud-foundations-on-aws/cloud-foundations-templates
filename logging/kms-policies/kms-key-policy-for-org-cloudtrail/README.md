# KMS key policy for Org CloudTrail

By default, the log files delivered by CloudTrail to your bucket are encrypted by [Amazon server-side encryption with Amazon S3-managed encryption keys (SSE-S3)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html). To provide a security layer that is directly manageable, we recommend that you use [server-side encryption with AWS KMS keys (SSE-KMS)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html) for your CloudTrail log files.

Leverage the [kms-key-policy-for-org-cloudtrail](./kms-key-policy-cloudtrail.json) template to create a KMS key following the [AWS KMS guidance on creating keys](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html). Deploy the KMS key in the home region of your Security Tooling account (same region that CloudTrail will be deployed).
