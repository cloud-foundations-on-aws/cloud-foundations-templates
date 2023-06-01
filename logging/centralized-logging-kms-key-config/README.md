# Centralized Logging KMS Key Config

> **Notice:** This repository provides sample scripts, templates, policies, etc. They are not intended to be or supported as solutions, but serve as a helpful reference for building your own landing zone solution.

KMS (Key Management Service) can be used to encrypt AWS Config logs by generating and managing encryption keys that are used to encrypt and decrypt the logs. To enable encryption of AWS Config logs, KMS must be configured with the appropriate permissions to access the S3 bucket where the logs are stored. Once configured, KMS will use a customer master key (CMK) to encrypt the logs, which can only be decrypted using the same key. This ensures that the AWS Config logs are secure and can only be accessed by authorized individuals or services. Additionally, KMS provides detailed auditing and logging of all key usage, providing additional security and compliance measures for the encryption of AWS Config logs.

> **Note:** By default, the log files delivered by Config to your bucket are encrypted by [Amazon server-side encryption with Amazon S3-managed encryption keys (SSE-S3)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html). To provide a security layer that is directly manageable, we recommend that you use [server-side encryption with AWS KMS keys (SSE-KMS)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html) for your Config log files.

## KMS Key Settings

The following settings are recommended to be set for the KMS key attributes.

| Parameter | Recommendation | Description |
| ----------| -------------- | ----------- |
| `Key Type` | Symmetric | AWS KMS supports several types of KMS keys: symmetric encryption keys, symmetric HMAC keys, asymmetric encryption keys, and asymmetric signing keys.
| `Key Usage` | Encrypt and Decrypt |The key usage of a KMS key determines whether the KMS key is used for encryption and decryption, or signing and verifying signatures, or generating and verifying HMAC tags. |
| `Key Material Origin` | KMS | Key material origin is a KMS key property that identifies the source of the key material in the KMS key. |
| `Regionality` | Single Region | AWS KMS supports single-Region and multi-Region keys. |
| `Alias` | Use an alias that clearly defines the key as the AWS Config key (eg. config-org-key) | An alias is a friendly name for a AWS KMS key. For example, an alias lets you refer to a KMS key as test-key instead of 1234abcd-12ab-34cd-56ef-1234567890ab. |
| `Administration Policy` | Reference the Example policy in the policies directory | A key policy is a resource policy for an AWS KMS key. Key policies are the primary way to control access to KMS keys.  The Administration policy determines what principle(s) will have permissions to manage the key. |
| `Usage Policy` | Reference the Example policy in the policies directory | A key policy is a resource policy for an AWS KMS key. Key policies are the primary way to control access to KMS keys.  The Usage policy determines what principle(s) will have permissions to use the key. |

## KMS Key Policy - Org AWS Config

Leverage the [kms-key-policy-for-org-config.json](./kms-key-policy-for-org-config.json) template to create a KMS key following the [AWS KMS guidance on creating keys](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html). Deploy the KMS key in the home region of your Security Tooling account ((same region where the Config S3 bucket will be located)).

## CloudFormation - KMS Key for Centralized AWS Config logging

The CloudFormation template [cfn-centralized-logging-kms-key-config.yaml](./cfn-centralized-logging-kms-key-config.yaml) creates a KMS Key to be deployed in your [Security Tooling account](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/security-ou-and-accounts.html#security-tooling-accounts) for encrypting AWS Config Snapshots and History in the [Log Archive account](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/security-ou-and-accounts.html#services-in-log-archive-account).

The centralized Config KMS Key policy allows the Log Archive and Management account to decrypt.

Deploy this KMS Key Template to your Security Tooling account.

### CloudFormation Parameters

| Parameter Name | Type | Default Value | Description |
| -------------- | ---- | ------------- | ----------- |
| `pManagementAccountId` | String | | The organization Management Account ID. |
| `pLogArchiveAccountId` | String |  | The organization Log Archive Account ID. |
| `pConfigKeyAlias` | String | config-org-key | The CloudTrail KMS Key Alias. |

