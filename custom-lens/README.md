# Custom Lens

This directory contains [Well Architected Custom Lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) that can be used to assess and track your Cloud Foundations deployments.

## CFA Custom Lens Usage

To automatically publish the Lens for use in your account follow the below steps.  Alternatively, you can manually deploy the Custom Lens json following the [Well Architected Custom Lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) guidance.

1. Log into an AWS account.  This account will be used to hold the Well-Architected Custom Lens
2. Run the following command in CloudShell. Add in the regions you plan to operate in: `export Regions=[AWS Region list] Owner="CFA"; curl -sSL https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/auto-deploy/app.py | python3`

    Example: `export Regions="us-east-1,us-west-2" Owner="CFA"; curl -sSL https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/custom-lens/custom-lens/auto-deploy/app.py | python3`

3. Navigate to the Well Architected Tool console in AWS.  Choose Workloads and select 'Organization' and then click Continue Reviewing and choose AWS Cloud Foundations Accelerator.

## Content

| Custom Lens | Description | Type |
| --------------- | ----------- | ---- |
| [Cloud Foundations Accelerator Custom Lens](./cloud-foundations-accelerator-custom-lens.json) |  Custom Lens to measure and track your progress as you complete the core Cloud Foundations capabilities. This Custom Lens goes into greater depth than the Acceleration Day Custom Lens | [Custom Lens](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) |
