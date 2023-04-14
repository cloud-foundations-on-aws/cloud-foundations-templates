# AWS Organizations

The following directory contains various templates, examples, policies, and scripts that can help you establish your foundational AWS Organization structure in the cloud. Please refer to the following table for a quick description of each solution within the directory:

| Example | Description | Type |
| ------- | ----------- | ---- |
| [foundational Organizational Unit structure](./foundational-organizational-unit-structure/) | Template deploys a basic AWS Organizational Unit structure with AWS accounts for log centralization and security tooling. | [CloudFormation](./foundational-organizational-unit-structure/cfn-foundational-organizational-unit-structure.yaml) |
| [Org hardening example scp](./scp-org-hardening-example/) | Prevents member accounts from leaving the AWS Organization, stops root user activity in member accounts, and stops resource sharing outside of the AWS Organization. | [Service Control Policy](./scp-org-hardening-example/) |
