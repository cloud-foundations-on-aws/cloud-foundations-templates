import boto3
import requests
from botocore.exceptions import ClientError
import os

"""
This module interacts with the AWS Well-Architected Tool to manage custom lenses and workloads.

Functions:
    main():
        The main function of the module, responsible for the following tasks:
        1. Import a custom lens from a GitHub repository URL.
        2. Create a new version of the imported lens if it already exists.
        3. Create a new workload in the Well-Architected Tool, associating it with the imported lens.

Environment Variables:
    Regions (str): A comma-separated list of AWS regions where the workload should be created.
    Owner (str): The owner of the workload being created.

Usage:

    Example:
        $ export Regions="us-east-1,us-west-2"
        $ export Owner="example@company.com"
        $ python app.py

Dependencies:
    - boto3 (AWS SDK for Python)
    - requests (Python library for making HTTP requests)
    - os (Python built-in module for operating system operations)

Note:
    This module assumes that the AWS credentials are properly configured and available in the environment.
    It also assumes that the user has the necessary permissions to interact with the Well-Architected Tool.
"""

client = boto3.client('wellarchitected')
#url = "https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/cloud-foundations-accelerator-custom-lens.json"
url = "https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/cloud-foundations-accelerator-custom-lens.json"

def main():

    AwsRegions = os.environ['Regions'].split(',')
    ReviewOwner = os.environ["Owner"]
    try:
        import_lens = client.import_lens(
            JSONString=str(requests.get(url).text)
        )['LensArn']
        print(import_lens)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            print("awscloudfoundationsaccelerator already exists")
            custom_lens_present = True
            custom_lens = client.list_lenses(
                LensType='CUSTOM_SELF',
                LensStatus='PUBLISHED',
                LensName='AWS Cloud Foundations Accelerator'
            )['LensSummaries'][0]
            import_lens = custom_lens['LensArn']
            current_version = custom_lens['LensVersion']
        else:
            print("Unexpected error: %s" % e)

    try:
      create_version = client.create_lens_version(
          LensAlias=import_lens,
          LensVersion='1',
          IsMajorVersion=True
      )
      print(create_version)
    except ClientError as e:
      if e.response['Error']['Code'] == 'ConflictException':
        print("Version already exists")
      else:
        print("Unexpected error: %s" % e)

    try:
      create_workload = client.create_workload(
          WorkloadName='Organization',
          Description='Cloud Foundation Accelerator',
          Environment='PRODUCTION',
          AwsRegions=AwsRegions,
          ReviewOwner=ReviewOwner,
          Lenses=[
              import_lens,
          ],
      )['WorkloadArn']
      print(f"{create_workload} created in Well Architected Tool. \n\nNavigate to the Well Architected Tool AWS console to review the Workload")
    except ClientError as e:
      if e.response['Error']['Code'] == 'ConflictException':
        print("Workload already exists")
      else:
        print("Unexpected error: %s" % e)


if __name__ == "__main__":
    main()
