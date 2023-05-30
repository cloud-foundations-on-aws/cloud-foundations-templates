# Identity Management and Access Control

The following directory contains various templates, examples, policies, and scripts that can help you establish your foundational [identity management and access control capability](https://aws.amazon.com/solutions/guidance/identity-management-and-access-control-on-aws/) in your cloud environment. Please refer to the following table for a quick description of each solution within the directory:

| Example | Description | Type |
| --------------- | ----------- | ---- |
| [management account AWS IdC assignments](./management-account-aws-idc-assignments/) |  Template creates two assignments for AWS Identity Users in the management account for admin and read-only access. Deploy the template in your AWS Management account under the region your Identity Center is deployed in. | [CloudFormation](./management-account-aws-idc-assignments/cfn-management-account-aws-idc-assignments.yaml) <br /> [Terraform](./management-account-aws-idc-assignments/tf-management-account-aws-idc-assignments/)|
| [management account AWS IdC permission sets](./management-account-aws-idc-permission-sets/) | Template creates two permissions set for AWS Identity Users accessing the management account with admin or read-only permissions. Deploy the template in your AWS Management account under the region your Identity Center is deployed in. | [CloudFormation](./management-account-aws-idc-permission-sets/cfn-ma-aws-idc-permission-sets.yaml) <br /> [Terraform](./management-account-aws-idc-permission-sets/tf-ma-aws-idc-permission-sets/)|
