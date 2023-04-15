# Control Tower Cross Account Trust

The following template deploys an execution role in the your account(s) which can be assumed by Control Tower from the management account. Use this template prior to enroll existing accounts into your Control Tower environment. Without deploying the role/trust in the target account, Control Tower will be unable to access the account and therefore unable to enroll the account. For more information visit [Manually add the required IAM role to an existing AWS account and enroll it](https://docs.aws.amazon.com/controltower/latest/userguide/enroll-manually.html) in the Control Tower documentation.

Be sure to review the [Prerequisites for enrollment](https://docs.aws.amazon.com/controltower/latest/userguide/enrollment-prerequisites.html) as described in the Control Tower documentation.

> **Info:** The template will fail to provision if the account was created by Control Tower account factory or someone manually created the role. Use this template only for accounts created outside of Control Tower account factory.

## CloudFormation Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| pManagementAccountId | String | | Management account id which AWS Control Tower is deployed in. |
