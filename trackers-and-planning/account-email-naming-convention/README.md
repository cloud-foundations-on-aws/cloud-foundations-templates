# AWS Account email naming convention template

Use the following template to start out defining an email convention for your AWS accounts and tracking the AWS account root users to the email address.

>**Important:** It is also recommended to use distribution group emails over individual or personal email addresses.

When creating new AWS accounts, you will need to use an email address that is associated with the root user of the account. To better manage your AWS environment as it scales, it is recommended to establish a naming convention for the [account alias](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html#AboutAccountAlias) and the corresponding root account email address. We recommend using the same name used for the email as the AWS account alias.

>**Consider the following:** *Do not* simply give you AWS account such as the management account the name `aws-management-account`. Within AWS, you can potentially have more than one AWS management account and Organization. We recommend using an additional descriptor to ensure that if you scale your environment to multiple AWS Organizations, you will be able to identify the different environments. For more information, review this Multiple organizations section from the [AWS Whitepaper on Organizing your AWS Environment Using Multiple Accounts](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/multiple-organizations.html).
