# Identity Management

The following directory contains various templates, examples, policies, and scripts that can help you establish your foundational identity management capability in your cloud environment. Please refer to the following table for a quick description of each solution within the directory:

| Example | Description | Type |
| --------------- | ----------- | ---- |
| [management account AWS IdC assignments](./cloudformation/management-account-aws-idc-assignments/) |  Template creates two assignments for AWS Identity Users in the management account for admin and read-only access. Deploy the template in your AWS Management account under the region your Identity Center is deployed in. | CloudFormation |
| [management account AWS IdC permission sets](./cloudformation/management-account-aws-idc-permission-sets/) | Template creates two permissions set for AWS Identity Users accessing the management account with admin or read-only permissions. Deploy the template in your AWS Management account under the region your Identity Center is deployed in. | CloudFormation |

## What is Identity Management?

Identity management in AWS (Amazon Web Services) refers to the process of creating, managing, and controlling user identities and their access to AWS resources. This includes managing user authentication, authorization, and access control for AWS services and resources.

AWS provides several tools and services to help with identity management, including AWS Identity and Access Management (IAM), Identity Center formally known as *AWS Single Sign-On (SSO)*, and AWS Organizations. Overall, identity management in AWS is crucial for maintaining security and control over access to AWS resources. By using IAM, SSO, and Organizations, AWS users can easily manage user identities and their access to resources, while maintaining security and compliance with industry standards.