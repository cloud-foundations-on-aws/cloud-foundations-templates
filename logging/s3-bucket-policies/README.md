# Centralized Logging S3 Policies

The directory provides a comprehensive set of S3 Policies that enable you to govern access to your AWS cloud foundation's S3 buckets in a secure and flexible manner across multiple AWS accounts. By utilizing these policies, you can define fine-grained access controls and set permissions at the object or bucket level, ensuring the confidentiality, integrity, and availability of your data while adhering to your organization's compliance requirements.

| Policy | AWS Service | Description |
| -------- | ----------- | ----------- |
| [Centralized logging CloudTrail S3 Bucket policy](./centralized-logging-cloudtrail-s3-bucket-policy/) | S3 | S3 Bucket policy that allows AWS Organization CloudTrail trail to write to the bucket. |
| [Centralized logging Config S3 Bucket policy](./centralized-logging-config-s3-bucket-policy/) | S3 | S3 Bucket policy that allows Config recorders within an AWS Organization to write to the bucket. |
