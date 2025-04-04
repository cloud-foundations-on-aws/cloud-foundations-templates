# Custom Lens

This directory contains the **10 Step Organizational Foundation [Well Architected Custom Lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) that can be used to assess and track your initial Cloud Foundations deployments.

You can use this Lens as a step-by-step guide to review or implement you organizational foundation.


## CFA Custom Lens Usage

To deploy this Custom Lens in your environment:

### 1. Log into an AWS account
Log into one of your AWS accounts.  The WA Custom Lens does not affect any of your workloads.  It does not create, modify, or read any of your resources (except the Custom Lens itself).

### 2. Go to the Well-Architected Tool console
Go to the [Well-Architected Tool console](https://us-east-1.console.aws.amazon.com/wellarchitected/home?region=us-east-1#/welcome) in your AWS account.

### 3. Navigate to Custom Lenses in the WA Tool
Click on Custom lenses in the left navigation panel.

### 4. Create custom lens
Click on **Create custom lens** in the top right.

### 5. Choose the Custom Lens json
Choose the `cfa-organizations-lens.json` file in this directory and click **Submit**.

### 6. Publish the Custom Lens
Publish the Custom Lens and provide a version number.

### 7. Define a Workload
A WA Custom Lens is used to evaluate a workload.  In the case of the `cfa-organizations-lens.json`, we are evaluating or implementing on the AWS Organization.

Click on **Workloads** in the left navigation panel and then click **Define workload** and **Define Workload** again.

### 8. Provide the workload details

1. Workload Properties:
Fill in the following information:
- **Name:** *Organization*
- **Description:** Provide a brief description.
- **Review Owner:** Provide your email.
- **Environment:** Choose *Production*
- **Regions:** Select the AWS Regions that you are using
- Leave the remaining as defaults

Select **Next**

2. On the **Apply profile** screen, select **Next**

3. On the Apply lenses screen, select the **AWS Cloud Foundations Accelerator - 10 Step organizational foundation** that you have added in previous steps.

4. Click **Define workload**

### 9. Start reviewing workload
On the Workload that you have just created, click on **Start reviewing** -> **AWS Cloud Foundations Accelerator - 10 Step organizational foundation** to use the Custom Lens.

## Content

| Custom Lens                                                             | Description | Type |
|-------------------------------------------------------------------------| ----------- | ---- |
| [10 Step Organizational Foundation Lens](./cfa-organizations-lens.json) |  Custom Lens to measure and track your progress as you complete the core Cloud Foundations capabilities. This Custom Lens goes into greater depth than the Acceleration Day Custom Lens | [Custom Lens](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) |
