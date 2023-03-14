# Management Account Identity Center Permissions Sets

From your AWS management account in the AWS IAM Identity Center web console, you will need to add/create the permission set for your management account administrators. Note that any permission set assigned to the management account cannot be leveraged or edited from the AWS IAM Identity Center delegated admin AWS account.

Follow the [Create a permission set](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtocreatepermissionset.html) instructions from the AWS Identity Center documentation to create the following permission sets or deploy the CloudFormation template in this directory.

> **Note:** that the MA-Administrator permissions set leverages a *Predefined permission set*, whereas the MA-ReadOnly uses a *Custom permission set*:

**MA-Administrator**
Permission Set Name: MA-Administrator
Permission Set Type: Predefined
Description: Gives administrative access to the management account
Tags: Add your defined mandatory tags to this permission set
Associated Policies: Predefined permission set: AdministratorAccess

**MA-ReadOnly**
Permission Set Name: MA-ReadOnly
Permission Set Type: Custom
Description: Gives read-only access to the management account
Tags: Add your defined mandatory tags to this permission set
Associated Policies: Custom Permission set: AWS managed policy ReadOnlyAccess

## CloudFormation Template

The CloudFormation template creates two permissions set for AWS Identity Users accessing the management account. Deploy the template in your AWS Management account under the region your Identity Center is deployed in.

## Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `pIdentityCenterArn` | String |  | The ARN of the IAM Identity Center instance under which the operation will be executed. |
| `pMAAdminSessionDuration` | String |  `PT1H` | The length of time that the MA-Administrator user sessions are valid for in the ISO-8601 standard |
| `pMAReadOnlySessionDuration` | String | `PT1H` | The length of time that the MA-ReadOnly user sessions are valid for in the ISO-8601 standard. |
