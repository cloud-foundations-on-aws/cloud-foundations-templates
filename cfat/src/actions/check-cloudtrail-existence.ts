import { CloudTrailClient, DescribeTrailsCommand } from '@aws-sdk/client-cloudtrail';
import { CloudTrailInfo } from '../types';

async function checkCloudTrailExists(regions: string[]): Promise<CloudTrailInfo[]> {
  let cloudTrailValidation: CloudTrailInfo[] = []
  for (const region of regions){
    const cloudTrailClient = new CloudTrailClient({ region });
    const cloudTrailDescribeCommand = new DescribeTrailsCommand({});

    try {
      const cloudTrailResponse = await cloudTrailClient.send(cloudTrailDescribeCommand);
      if(cloudTrailResponse.trailList){
          for (const trail of cloudTrailResponse.trailList) {
            let trailInfo: CloudTrailInfo = {}
            if(trail.HomeRegion == region){
              //console.log(`trail found in ${region}`)
              trailInfo = {
                region: region,
                trailFound: true,
                isOrgTrail: trail.IsMultiRegionTrail,
                isMultiRegion: trail.IsMultiRegionTrail
              }
            }
            else{
              trailInfo = {
                region: region,
                trailFound: false
              }
            }
            cloudTrailValidation.push(trailInfo)
          }
      }
    } catch (error) {
      console.log(`Error checking instance: ${error}`);
    }
    finally {
      cloudTrailClient.destroy();
    }
  }// end for regions
  return cloudTrailValidation;
};

export default checkCloudTrailExists;