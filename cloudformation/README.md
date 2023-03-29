# Cloud Foundations CloudFormation templates

Inside the directory, you can find a collection of sample templates in CloudFormation that can assist you in deploying different components of your AWS cloud foundation. The templates are grouped into solution directories, each of which includes documentation for implementing the corresponding solution. With these resources at your disposal, you can quickly and effectively deploy the necessary AWS resources to build and maintain a robust cloud infrastructure.

| Sample Solution | Description |
| --------------- | ----------- |
| [centralized logging CloudTrail S3 Bucket](./centralized-logging-cloudtrail-s3-bucket/) | Template creates an S3 Bucket to be deployed in your log archive account for centralized logging of CloudTrail. |
| [centralized logging Config S3 Bucket](./centralized-logging-config-s3-bucket/)  | Template creates an S3 Bucket to be deployed in your log archive account for centralized logging of Config. |
| [centralized logging KMS key Cloudtrail](./centralized-logging-kms-key-cloudtrail/) | Template creates a KMS Key to be deployed in your Security Tooling account for encrypting an Organizational CloudTrail Trail. |
| [centralized logging KMS key Config](./centralized-logging-kms-key-config/) | Template creates a KMS Key to be deployed in your Security Tooling account for encrypting AWS Config Snapshots and History in the Log Archive account. |
| [centralized logging Org Trail CloudTrail](./centralized-logging-org-trail-cloudtrail/) | Template creates an Organization CloudTrail trail for management events and records them in a previously created centralized S3 bucket in the Log Archive account. |
| [controltower-cross-account-trust](./controltower-cross-account-trust) | Template creates the cross-account trust necessary for Control Tower to manage. Use this template for accounts provisioned outside of the Control Tower environment that need to be enrolled into it. |
| [foundational Organizational Unit structure](./foundational-organizational-unit-structure/) | Template deploys a basic AWS Organizational Unit structure with AWS accounts for log centralization and security tooling. |
| [foundational Tagging Policy](./foundational-tagging-policy/) | The foundational tagging policy provides a CloudFormation template example of creating an AWS Organization Tagging policy. Leverage the template to customize for you tagging policy solutions. |
| [management account AWS IdC assignments](./management-account-aws-idc-assignments/) |  Template creates two assignments for AWS Identity Users in the management account for admin and read-only access. Deploy the template in your AWS Management account under the region your Identity Center is deployed in. |
| [management account AWS IdC permission sets](./management-account-aws-idc-permission-sets/) | Template creates two permissions set for AWS Identity Users accessing the management account with admin or read-only permissions. Deploy the template in your AWS Management account under the region your Identity Center is deployed in. |
