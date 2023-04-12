# Centralized Logging  CloudFormation templates

Inside the directory, you can find a collection of sample templates in CloudFormation that can assist you in deploying different components of your AWS cloud foundation centralized logging capability. The templates are grouped into solution directories, each of which includes documentation for implementing the corresponding solution. With these resources at your disposal, you can quickly and effectively deploy the necessary AWS resources to build and maintain a robust cloud infrastructure.

| Example | Description |
| --------------- | ----------- |
| [centralized logging CloudTrail S3 Bucket](./centralized-logging-cloudtrail-s3-bucket/) | Template creates an S3 Bucket to be deployed in your log archive account for centralized logging of CloudTrail. |
| [centralized logging Config S3 Bucket](./centralized-logging-config-s3-bucket/)  | Template creates an S3 Bucket to be deployed in your log archive account for centralized logging of Config. |
| [centralized logging KMS key Cloudtrail](./centralized-logging-kms-key-cloudtrail/) | Template creates a KMS Key to be deployed in your Security Tooling account for encrypting an Organizational CloudTrail Trail. |
| [centralized logging KMS key Config](./centralized-logging-kms-key-config/) | Template creates a KMS Key to be deployed in your Security Tooling account for encrypting AWS Config Snapshots and History in the Log Archive account. |
| [centralized logging Org Trail CloudTrail](./centralized-logging-org-trail-cloudtrail/) | Template creates an Organization CloudTrail trail for management events and records them in a previously created centralized S3 bucket in the Log Archive account. |
