import boto3
import requests
from botocore.exceptions import ClientError

client = boto3.client('wellarchitected')
url = "https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/cloud-foundations-accelerator-custom-lens.json"

def main():

    region_input = input("Enter AWS Regions - us-east-1,us-west-2,us-east-2 :").strip()
    AwsRegions = region_input.split(',')
    OwnerEmail = input("Enter Review Owner Email: ")

    custom_lens_present = False
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
          WorkloadName='Organizations',
          Description='Cloud Foundation Accelerator',
          Environment='PRODUCTION',
          AwsRegions=AwsRegions,
          ReviewOwner=OwnerEmail,
          Lenses=[
              import_lens,
          ],
      )['WorkloadArn']
      print(create_workload)
    except ClientError as e:
      if e.response['Error']['Code'] == 'ConflictException':
        print("Workload already exists")
      else:
        print("Unexpected error: %s" % e)


if __name__ == "__main__":
    main()
