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

LENS_URL = "https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/cloud-foundations-accelerator-custom-lens.json"
LENS_NAME = "AWS Cloud Foundations Accelerator"

client = boto3.client('wellarchitected')


def import_custom_lens(lens_url):
    try:
        lens_arn = client.import_lens(JSONString=str(requests.get(lens_url).text))['LensArn']
        print(f"Imported lens: {lens_arn}")
        return lens_arn
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            print(f"{LENS_NAME} lens already exists.")
            existing_lens = get_existing_lens(LENS_NAME)
            return existing_lens['LensArn']
        else:
            raise e


def get_existing_lens(lens_name):
    try:
        lens_summaries = client.list_lenses(LensType='CUSTOM_SELF', LensStatus='PUBLISHED', LensName=lens_name)['LensSummaries']
        if lens_summaries:
            return lens_summaries[0]
        else:
            raise ValueError(f"No lens found with the name '{lens_name}'")
    except ClientError as e:
        raise e


def create_lens_version(lens_arn):
    try:
        response = client.create_lens_version(LensAlias=lens_arn, LensVersion='1', IsMajorVersion=True)
        print(f"Created lens version")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print("Lens version already exists.")
        else:
            raise e


def create_workload(lens_arn, regions, owner):
    try:
        workload_arn = client.create_workload(
            WorkloadName='Organization',
            Description='Cloud Foundation Accelerator',
            Environment='PRODUCTION',
            AwsRegions=regions,
            ReviewOwner=owner,
            Lenses=[lens_arn]
        )['WorkloadArn']
        print(f"Workload created: {workload_arn}\n\nNavigate to the Well Architected Tool AWS console to review the Workload")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print("Workload already exists.")
        else:
            raise e


def main():
    regions = os.environ['Regions'].split(',')
    owner = os.environ["Owner"]

    lens_arn = import_custom_lens(LENS_URL)
    create_lens_version(lens_arn)
    create_workload(lens_arn, regions, owner)


if __name__ == "__main__":
    main()
