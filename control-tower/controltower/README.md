# Control Tower

Cloudformation template to deploy AWS Control Tower with the the `AWS::ControlTower::LandingZone` CloudFormation resources. The template can deploy a new AWS Organization and Control Tower environment or deploy Control Tower into an existing AWS Organization.

The template enables you to choose whether to create new AWS accounts for the Control Tower Audit and Log Archive account or use existing AWS accounts by importing them via this template.

> **Note:** The template requires that the `Security OU` name does not already exist. Control Tower will create this OU.

## CloudFormation

The solution can be deployed with the single CloudFormation template [cfn-controltower.yaml](./cfn-controltower.yaml)

### CloudFormation Parameters

| Parameter | Type | Default Value | Description |
| --------- | ---- | ------------- | ----------- |
| pCreateNewAwsOrg | String | `Yes` | Specify whether to create the AWS Organization or if one already exists. Select no if you already have an AWS Organization.|
| pSandboxOuName | String | `Sandbox` | Name of additional OU to be created and registered in Control Tower. |
| pSecurityOuName | String | `Security` | The security Organizational Unit name. |
| pDeployNewSecurityAccount | String (Yes/No) | `Yes` | Deploy a NEW Security account or select No and enter an existing AWS account ID to use a pre-existing account. |
| pImportedSecurityAccountId | String | | If you selected No for creating a new Security account, enter the existing account ID that will serve as your Security account ID. |
| pSecurityAccountAlias | String | `Audit` | The AWS account alias for the Security account. If importing a pre-existing Security account, leave blank. |
| pSecurityAccountEmailAddress| String | | The Security email address for any newly created Security account. Leave this blank if importing a pre-existing Security account.|
| pDeployNewLogArchiveAccount | String (Yes/No) | `Yes` |  Deploy a NEW Log Archive account or select No and enter an existing AWS account ID to use a pre-existing account. |
| pImportedLogArchiveAccountId | String | | If you selected No for creating a new Log Archive account, enter the existing account ID that will serve as your Log Archive account ID. |
| pLogArchiveAccountAlias | String | `Log Archive` | The AWS account alias for the Log Archive account. If importing a pre-existing Log Archive account, leave blank. |
| pLogArchiveAccountEmailAddress | String | | The Log Archive email address for any newly created Log Archive account. Leave this blank if importing a pre-existing Log Archive account. |
| pVersion | String | `3.3` | The version number of Landing Zone |
| pGovernedRegions | CommaDelimitedList | `"us-east-1, us-west-2"` | List of governed regions |
| pLoggingBucketRetentionPeriod | Number | `365` | Retention period for centralized logging bucket |
| pAccessLoggingBucketRetentionPeriod | Number | `90` | Retention period for access logging bucket |
