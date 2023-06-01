# S3 Bucket for Centralized AWS CloudTrail logging

> **Notice:** This repository provides sample scripts, templates, policies, etc. They are not intended to be or supported as solutions, but serve as a helpful reference for building your own landing zone solution.

To centralize AWS CloudTrail logs, you need to configure a central AWS S3 Bucket with the appropriate permissions, enabling a CloudTrail Organization Trail to write logs to it. You can utilize the resources available in the directory to create your very own AWS S3 Bucket, dedicated to centralized logging of CloudTrail.

## S3 Bucket Policy - Centralized CloudTrail logging

The S3 Bucket policy [s3-bucket-policy-centralized-logging-cloudtrail.json](./s3-bucket-policy-centralized-logging-cloudtrail.json) will enable an S3 bucket to receive AWS CloudTrail events from an Organization CloudTrail Trail.

Follow the [AWS CloudTrail User Guide guidance on creating an S3 bucket policy for CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html).

## CloudFormation - S3 Bucket for Centralized AWS CloudTrail logging

The CloudFormation template [cfn-centralized-logging-cloudtrail-s3-bucket.yaml](./cfn-centralized-logging-cloudtrail-s3-bucket.yaml) creates an S3 Bucket to be deployed in your log archive account for centralized logging of CloudTrail. Template will deploy two S3 buckets: one for centralized config logging and another for access logging.

The centralized CloudTrail logging bucket is configured so that AWS CloudTrail can write to it within your Organization. Deploy this bucket to your log archive account.

### Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `CloudTrail AWS Account Id` | String |  | Management Account ID.|
| `CloudTrail Trail Name` | String | aws-cloudtrail-org | The name of the Organization Trail for CloudTrail.|
| `S3 Bucket name` | String | `cloudtrail-logs` | defines the name of the s3 bucket to store logs from CloudTrail. The name will be suffixed with the account ID to help create a globally unique name. |
| `SSE algorithm` | String |  `AES256` | Accepts values of `AES256` or `aws:kms` to set the server side encryption of the S3 Bucket. If you specify `aws:kms` you will need to include  `KMS Key ID` parameter in the template. |
| `KMS key ID` | String |  | The KMS key ID that you use to encrypt data at rest in the S3 Bucket. Leave this blank if using `AES256` for the `SSE algorithm` parameter. If using KMS Key, ensure it is in same region as the S3 Bucket. |
| `Retention in days` | String | 365  | Number of Days to retain the CloudTrail logs, after which it will be permanently deleted. |
| `Retention days for access logs` | String | 365 | Number of Days to retain the access logs, after which it will be permanently deleted. |
| `Transition to Glacier` | String | No | Yes or No option to to specify to transition the logs to Glacier before permanently deleting. |
| `Transition to Glacier days` | String | 364 | The number of days to transition the data from S3 to Glacier if Glacier is being used. |
| `AWS Organization ID` | String | | The ID of your AWS Organization |
