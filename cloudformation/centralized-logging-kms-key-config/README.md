# KMS Key for Centralized AWS Config logging

Template creates a KMS Key to be deployed in your Security Tooling account for encrypting AWS Config Snapshots and
 History in the Log Archive account.

The centralized Config KMS Key policy allows the Log Archive and Management account to decrypt.

Deploy this KMS Key Template to your Security Tooling account.

## CloudFormation Parameters

| Parameter Name | Type | Default Value | Description |
| -------------- | ---- | ------------- | ----------- |
| `pManagementAccountId` | String | | The organization Management Account ID. |
| `pLogArchiveAccountId` | String |  | The organization Log Archive Account ID. |
| `pConfigKeyAlias` | String | config-org-key | The CloudTrail KMS Key Alias. |

## KMS Key Settings

The CloudFormation template sets the below recommended KMS key attributes.

| Parameter | Recommendation | Description | 
| ----------| -------------- | ----------- |
| `Key Type` | Symmetric | AWS KMS supports several types of KMS keys: symmetric encryption keys, symmetric HMAC keys, asymmetric encryption keys, and asymmetric signing keys.
| `Key Usage` | Encrypt and Decrypt |The key usage of a KMS key determines whether the KMS key is used for encryption and decryption, or signing and verifying signatures, or generating and verifying HMAC tags. |
| `Key Material Origin` | KMS | Key material origin is a KMS key property that identifies the source of the key material in the KMS key. |
| `Regionality` | Single Region | AWS KMS supports single-Region and multi-Region keys. |
| `Alias` | Use an alias that clearly defines the key as the AWS Config key (eg. config-org-key) | An alias is a friendly name for a AWS KMS key. For example, an alias lets you refer to a KMS key as test-key instead of 1234abcd-12ab-34cd-56ef-1234567890ab. |
| `Administration Policy` | Reference the Example policy in the policies directory | A key policy is a resource policy for an AWS KMS key. Key policies are the primary way to control access to KMS keys.  The Administration policy determines what principle(s) will have permissions to manage the key. |
| `Usage Policy` | Reference the Example policy in the policies directory | A key policy is a resource policy for an AWS KMS key. Key policies are the primary way to control access to KMS keys.  The Usage policy determines what principle(s) will have permissions to use the key. |
