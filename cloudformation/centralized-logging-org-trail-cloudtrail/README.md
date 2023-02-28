# Organization CloudTrail Trail

Template creates an Organization CloudTrail trail for management events and records them in a previously created
 centralized S3 bucket in the Log Archive account.

Deploy this CloudTrail trail to the home region of your management account.

## CloudFormation Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `pCloudTrailName` | String | `aws-cloudtrail-org` | CloudTrail Name |
| `pCloudTrailS3BucketName` | String |  | CloudTrail S3 Bucket Name located in the Log Archive account. |
| `pOrganizationCloudTrailKMSKeyId` | String |  | Organization CloudTrail KMS Key Arn. |


## CloudTrail Trail Parameters

Use the below parameters to create a Trail from the console.

| Parameter | Recommendation | Description |
| --------- | -------------- | ----------- |
| `Trail Name` | aws-cloudtrail-org* Ensure the CloudTrail name is the same as the conditional statement in the bucket policy. | The name of the CloudTrail Trail |
| `Enable for all accounts in my organization` | Enabled |  Enable cloudtrail for all accounts in organization |
| `Storage location` | The S3 bucket that was created in the Log Archive account. | The S3 bucket where CloudTrail will send logs. |
| `Log file SSE-KMS encryption` | Enabled | Enable the use of SSE-KMS customer managed key. |
| `Customer managed AWS KMS key` | Existing | New or Existing KMS key |
| `AWS KMS alias` | Use the ARN of the CloudTrail KMS key.  Note: this must be the full ARN (not the alias) because the key is in another account.  | The KMS key that will be used to encrypt CloudTrail |
| `Log file validation` | Enabled | Enable log file validation |
| `CloudWatch Logs` | Enabled | Enable CloudTrail to send logs to CloudWatch  |
