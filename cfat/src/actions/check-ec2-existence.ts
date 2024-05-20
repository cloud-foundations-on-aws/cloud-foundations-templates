import { EC2Client, DescribeInstancesCommand, DescribeInstancesCommandOutput } from "@aws-sdk/client-ec2";
import { Ec2Check } from '../types';

async function checkEc2Exists(regions: string[]): Promise<Ec2Check[]> {
  let ec2Validation: Ec2Check[] = []
  for (const region of regions){
    const ec2Client = new EC2Client({ region });

    const command = new DescribeInstancesCommand({});

    try {
      const response = await ec2Client.send(command);
      if(response.Reservations){
        if (response.Reservations.length > 0) {
          //console.log(`WARNING: Instance(s) exists in region: ${region}`);
          const ec2Found: Ec2Check = {
            region: region,
            ec2Found: true
          }
          ec2Validation.push(ec2Found)
        }
        else{
          const ec2Found: Ec2Check = {
            region: region,
            ec2Found: false
          }
          ec2Validation.push(ec2Found)
        }
      } else {
        const ec2Found: Ec2Check = {
          region: region,
          ec2Found: false
        }
        ec2Validation.push(ec2Found)
      }
    } catch (error) {
      console.log(`Error checking instance: ${error}`);
    }
    finally {
      ec2Client.destroy();
    }
  }// end for
  return ec2Validation;
};

export default checkEc2Exists;