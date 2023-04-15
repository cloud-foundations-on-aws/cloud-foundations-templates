# Organization S3 Bucket

The following template deploys an S3 Bucket that has a trust for an AWS Organization to allow any AWS account within the Organization to `GetObject` and `ListBucket`. The bucket is commonly used to centrally share CloudFormation templates bucket which can only be accessed by the AWS account within the trusted Organization.

>**Note:** The trust is set for AWS account access and users cannot access templates via public URL through a web browser.

## Parameters

The following parameters are used in the CloudFormation template.

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `pOrgBucketName` | String |  | The name of the S3 Bucket which will have the Organization trust put on it. |
| `pLogBucketName` | String | | The name of the access logging bucket which will be deployed if access logging is enabled |
| `pOrganizationId` | String |  | The ID of your AWS Organization |
| `pDeployAccessLogging` | String | `No` | Yes/No value whether to deploy to enable access logging on the S3 Bucket and to deploy the S3 Log Bucket |
| `pUseVersioning` | String | `No` | Yes/No value whether you want the template to enable versioning on the S3 Bucket |
