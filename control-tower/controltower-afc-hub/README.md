# Control Tower AFC Hub

Before you begin to customize accounts in AWS Control Tower, you must set up a role that contains a trust relationship between AWS Control Tower management account and your hub account. When assumed, the role grants AWS Control Tower access to administer the hub account. The role must be named AWSControlTowerBlueprintAccess.

AWS Control Tower assumes this role to create a Portfolio resource on your behalf in Service Catalog, then to add your blueprint as a Service Catalog Product to this Portfolio, and then to share this Portfolio, and your blueprint, with your member account during account provisioning.

This template demonstrates the best practice of granting least-privilege access.

## CloudFormation

The solution can be deployed with the single CloudFormation template [cfn-controltower-afc-hub.yaml](./cfn-controltower-afc-hub.yaml)

### CloudFormation Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| pManagementAccount | String | | Management account id which AWS Control Tower is deployed in. |
| pAWSAdministratorAccessRole | String | The IAM Identity Center managed IAM Role you use to access the AWS Control Tower dashboard |

