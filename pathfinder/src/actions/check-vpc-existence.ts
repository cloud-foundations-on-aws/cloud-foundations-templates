import { EC2Client, DescribeVpcsCommand} from "@aws-sdk/client-ec2";
import { VpcCheck } from '../types';

async function checkVpcExists(regions: string[]): Promise<VpcCheck[]> {
  let vpcValidation: VpcCheck[] = []
  for (const region of regions){
    const ec2Client = new EC2Client({ region });
    const command = new DescribeVpcsCommand({});
    try {
      const response = await ec2Client.send(command);
      if(response.Vpcs){
        if (response.Vpcs.length > 0) {
          //console.log(`WARNING: VPC(s) exists in region: ${region}`);
          const vpcFound: VpcCheck = {
            region: region,
            vpcFound: true
          }
          vpcValidation.push(vpcFound)
        }
        else{
          const vpcFound: VpcCheck = {
            region: region,
            vpcFound: false
          }
          vpcValidation.push(vpcFound)
        }
      } else {
        const vpcFound: VpcCheck = {
          region: region,
          vpcFound: false
        }
        vpcValidation.push(vpcFound)
      }
    } catch (error) {
      console.log(`Error checking instance: ${error}`);
    }
    finally {
      ec2Client.destroy();
    }
  }// end for
  return vpcValidation;
};

export default checkVpcExists;