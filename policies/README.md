# Policy templates

The directory contains a wide range of sample policies that are organized by AWS service to aid in managing resource access for your AWS cloud foundation. By leveraging these sample policies, you can understand the different permissions that are required for accessing specific AWS resources and the scope of those permissions.

| Policy | AWS Service | Description |
| -------- | ----------- | ----------- |
| [KMS key policy for Org Cloudtrail](./kms/kms-key-policy-for-org-cloudtrail/) | KMS | KMS key policy to encrypt CloudTrail within a multi account environment. |
| [KMS key policy for Org Config](./kms/kms-key-policy-for-org-config/) | KMS | KMS key policy to encrypt Config within a multi account environment. |
| [centralized logging Config S3 Bucket policy](./s3/centralized-logging-config-s3-bucket-policy/) | S3 | S3 Bucket policy that allows Config recorders within an AWS Organization to write to the bucket. |
| [org hardening example scp](./service-control-policies/org-hardening-example/) | SCP | Prevents member accounts from leaving the AWS Organization, stops root user activity in member accounts, and stops resource sharing outside of the AWS Organization. |
