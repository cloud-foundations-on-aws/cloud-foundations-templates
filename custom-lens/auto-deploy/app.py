import boto3
import requests
from botocore.exceptions import ClientError
import os

client = boto3.client('wellarchitected')
#url = "https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/cloud-foundations-accelerator-custom-lens.json"
url = "https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/custom-lens-install-script/custom-lens/cloud-foundations-accelerator-custom-lens.json"

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
      print(f"{create_workload} created in Well Architected Tool. \nNavigate to the Well Architected Tool AWS console to review the Workload")
    except ClientError as e:
      if e.response['Error']['Code'] == 'ConflictException':
        print("Workload already exists")
      else:
        print("Unexpected error: %s" % e)


if __name__ == "__main__":
    main()
