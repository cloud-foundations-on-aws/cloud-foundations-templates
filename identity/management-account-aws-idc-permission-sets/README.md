# Management Account Identity Center Permissions Sets

> **Notice:** This repository provides sample scripts, templates, policies, etc. They are not intended to be or supported as solutions, but serve as a helpful reference for building your own landing zone solution.

From your AWS management account in  AWS IAM Identity Center, you will need to add/create the permission set for your management account administrators. Note that any permission set assigned to the management account cannot be leveraged or edited from the AWS IAM Identity Center delegated admin AWS account.

Follow the [Create a permission set](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtocreatepermissionset.html) instructions from the AWS Identity Center documentation to create the following permission sets or deploy the CloudFormation template in this directory.

> **Note:** that the MA-Administrator permissions set leverages a *Predefined permission set*, whereas the MA-ReadOnly uses a *Custom permission set*:

## MA-Administrator

<table>
<tr><th>Permission Set Name:</th><td>MA-Administrator</td></tr>
<tr><th>Permission Set Type:</th><td>Predefined</td></tr>
<tr><th>Description:</th><td> Gives administrative access to the management account</td></tr>
<tr><th>Tags:</th><td>Add your defined mandatory tags to this permission set</td></tr>
<tr><th>Associated Policies:</th><td>  Predefined permission set: AdministratorAccess</td></tr>
</table>

## MA-ReadOnly

<table>
<tr><th>Permission Set Name:</th><td> MA-ReadOnly</td></tr>
<tr><th>Permission Set Type:</th><td> Custom</td></tr>
<tr><th>Description:</th><td> Gives read-only access to the management account</td></tr>
<tr><th>Tags:</th><td> Add your defined mandatory tags to this permission set</td></tr>
<tr><th>Associated Policies:</th><td> Custom Permission set: AWS managed policy ReadOnlyAccess</td></tr>
</table>

## CloudFormation Template

The CloudFormation template creates two permissions set for AWS Identity Users accessing the management account. Deploy the template in your AWS Management account under the region your Identity Center is deployed in.

## Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `pIdentityCenterArn` | String |  | The ARN of the IAM Identity Center instance under which the operation will be executed. |
| `pMAAdminSessionDuration` | String |  `PT1H` | The length of time that the MA-Administrator user sessions are valid for in the ISO-8601 standard |
| `pMAReadOnlySessionDuration` | String | `PT1H` | The length of time that the MA-ReadOnly user sessions are valid for in the ISO-8601 standard. |
