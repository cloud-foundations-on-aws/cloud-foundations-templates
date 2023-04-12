# KMS key policy for Org Config

By default, the log files delivered by Config to your bucket are encrypted by [Amazon server-side encryption with Amazon S3-managed encryption keys (SSE-S3)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html). To provide a security layer that is directly manageable, we recommend that you use [server-side encryption with AWS KMS keys (SSE-KMS)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html) for your Config log files.

Leverage the [kms-key-policy-for-org-config](./kms-key-policy-config.json) template to create a KMS key following the [AWS KMS guidance on creating keys](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html). Deploy the KMS key in the home region of your Security Tooling account ((same region where the Config S3 bucket will be located)).
