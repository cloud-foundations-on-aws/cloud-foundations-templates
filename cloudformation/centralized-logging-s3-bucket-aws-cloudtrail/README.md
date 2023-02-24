# S3 Bucket for Centralized AWS CloudTrail logging

Template creates an S3 Bucket to be deployed in your log archive account for centralized logging of CloudTrail. Template will deploy two S3 buckets: one for centralized config logging and another for access logging.

The centralized config logging bucket is configured so that AWS CloudTrail can write to it within your Organization. Deploy this bucket to your log archive account.

## Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `S3 Bucket name` | String | `config-logs` | defines the name of the s3 bucket to store logs from CloudTrail. The name will be suffixed with the account ID to help create a globally unique name. |
| `SSE algorithm` | String |  `AES256` | Accepts values of `AES256` or `aws:kms` to set the server side encryption of the S3 Bucket. If you specify `aws:kms` you will need to include  `KMS Key ID` parameter in the template. |
| `KMS key ID` | String |  | The KMS key ID that you use to encrypt data at rest in the S3 Bucket. Leave this blank if using `AES256` for the `SSE algorithm` parameter. |
| `Retention in days` | String | 365  | Number of Days to retain the CloudTrail logs, after which it will be permanently deleted. |
| `Retention days for access logs` | String | 365 | Number of Days to retain the access logs, after which it will be permanently deleted. |
| `Transition to Glacier` | String | No | Yes or No option to to specify to transition the logs to Glacier before permanently deleting. |
| `Transition to Glacier days` | String | 364 | The number of days to transition the data from S3 to Glacier if Glacier is being used. |
| `AWS Organization ID` | String | | The ID of your AWS Organization |