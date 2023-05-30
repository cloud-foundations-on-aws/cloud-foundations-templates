# Centralized Logging KMS Key Config

> **Note:** The example uses a Terraform deployment from the AWS Management Account. The provider leverages assume role with the AWSControlTowerExecution role for cross across access in the environment.

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

Leverage the [kms-key-policy-for-org-config.json](../kms-key-policy-for-org-config.json) template to create a KMS key following the [AWS KMS guidance on creating keys](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html). Deploy the KMS key in the home region of your Security Tooling account ((same region where the Config S3 bucket will be located)).

## Terraform - KMS Key for Centralized AWS Config logging

The Terraform directory creates a KMS Key to be deployed in your [Security Tooling account](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/security-ou-and-accounts.html#security-tooling-accounts) for encrypting AWS Config Snapshots and History in the [Log Archive account](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/security-ou-and-accounts.html#services-in-log-archive-account).

The centralized Config KMS Key policy allows the Log Archive and Management account to decrypt.

Deploy this KMS Key Template to your Security Tooling account.

> **Note:** THIS SHOULD BE DEPLOYED USING CREDENTIALS IN THE AWS MANAGEMENT ACCOUNT. THIS DIRECTORY USES A SECOND PROVIDER TO DEPLOY INTO THE SECURITY/ADUIT ACCOUNT

### Terraform Parameters

| Parameter Name | Type | Default Value | Description |
| -------------- | ---- | ------------- | ----------- |
| `region` | String | `us-east-1` | The region in which to deploy the dictory |
| `config_key_alias` | String | config-org-key | The Config KMS Key Alias. |

