# Custom Lens

This directory contains [Well Architected Custom Lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) that can be used to assess and track your Cloud Foundations deployments.

## CFA Custom Lens Usage

To use the CFA Custom lens in your environment, follow the below steps.

1. Log into an AWS account.  This account will be used to hold the Well-Architected Custom Lens
2. Run the following command: `curl -sSL https://github.com/cloud-foundations-on-aws/cloud-foundations-templates/blob/custom-lens-install-script/custom-lens/custom-lens.sh | sh`
3. Answer the questions in the console.
4. Review the Organization Workload in the Well Architected Tool console.

## Content

| Custom Lens | Description | Type |
| --------------- | ----------- | ---- |
| [Cloud Foundations Accelerator Custom Lens](./cloud-foundations-accelerator-custom-lens.json) |  Custom Lens to measure and track your progress as you complete the core Cloud Foundations capabilities. This Custom Lens goes into greater depth than the Acceleration Day Custom Lens | [Custom Lens](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) |
