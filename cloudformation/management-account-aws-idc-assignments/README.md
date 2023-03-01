# Management Account Identity Center Assignments

From the management account in the AWS IAM Identity Center web console, you will need to assign your users to a permission set and to the management account. It is best practice to assign only users and not groups to the management account administrator assignment. Groups can be updated in the IAM Identity Center delegated admin account and could give unauthorized access to the management account.

Follow the instructions below assigning your management account users to both the MA-Administrator and MA-ReadOnly permission sets:

1. Access AWS accounts in AWS IAM Identity Center.
2. Select the checkbox next to your management AWS account.
3. Select Assign users and then select the user accounts you created for management account administration
4. Select Next then select MA-Administrator or MA-ReadOnly for permission set

The assignment will complete and your management account administrative users should be able to login and have access to the management account.

## CloudFormation Template

The CloudFormation template creates two assignments for AWS Identity Users. Deploy the template in your AWS Management account under the region your Identity Center is deployed in.

## Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| `pIdCInstanceId` | String |  | Then Identity Center instance Id. Example: `ssoins-xxxxxxxxxxxxxxxx` |
| `pManagementAccountId` | String |  | The AWS Management Account Id to deploy the assignment to |
| `pMAAdministratorUserId` | String |   | The MA-Administrator Identity Center User Id. Example: Example: `92670cccd8-6c7550b2-66ea-4c80-a7f5-7929bd561793`
) |
| `pMAAdministratorPermissionSetId` | String |  | The name of the permission set to assign the user Example: `ps-xxxxxxxxxxxxxxxx` |
| `pMAAdministratorPermissionSetId` | String |  | The ARN of the IAM Identity Center instance under which the operation will be executed |
| `pMAReadOnlyUserId` | String |   | The MA-ReadOnly Identity Center User Id. Example: `92670cccd8-6c7550b2-66ea-4c80-a7f5-7929bd561793` |
| `pMAReadOnlyPermissionSetId` | String |  | The name of the permission set to assign the user. Example: `ps-xxxxxxxxxxxxxxxx` |
