# Centralized Logging Config S3 Bucket Policy

The following S3 Bucket policy will enable an S3 bucket to receive AWS Config snapshots for an AWS Config recorder delivery channel.

Follow the [AWS Config User Guide guidance on creating an S3 bucket policy for Config](https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-policy.html#granting-access-in-another-account), create and apply a bucket policy [centralized-logging-config-s3-bucket-policy](./centralized-logging-config-s3-bucket-policy.json) to the Config S3 bucket. Update the policy by replacing the `[BUCKET_NAME]` with your AWS S3 Bucket name.

