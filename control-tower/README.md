# Control Tower

The directory contains various templates, scripts, and infrastructure as code for assisting in setting up and managing your `control tower` environment. Please refer to the following table for a quick description of each solution within the directory:

| Example | Description | Type |
| --------------- | ----------- | ---- |
| [Control Tower cross account trust](./controltower-cross-account-trust) | Template creates the cross-account trust necessary for Control Tower to manage. Use this template for accounts provisioned outside of the Control Tower environment that need to be enrolled into it. | [CloudFormation](./controltower-cross-account-trust/cfn-controltower-cross-account-trust.yaml) <br /> [Terraform](./controltower-cross-account-trust-tf) |
