import { CloudFormationClient,
  DescribeOrganizationsAccessCommand,
  DescribeOrganizationsAccessInput,
} from "@aws-sdk/client-cloudformation";

import {OrgCloudFormationStatus} from '../types'

async function getOrgCloudFormation(region: string): Promise<OrgCloudFormationStatus> {
  let orgCfnStatus: OrgCloudFormationStatus = {
    status: "disabled"
  }
  const cloudFormationClient = new CloudFormationClient({region});
  try {
    const describeOrgAccessInput: DescribeOrganizationsAccessInput = {};
    const command = new DescribeOrganizationsAccessCommand(describeOrgAccessInput);
    const cloudFormationOrgAccess = await cloudFormationClient.send(command);
    //console.log("CloudFormation activation status: ", cloudFormationOrgAccess.Status)
    orgCfnStatus.status = cloudFormationOrgAccess.Status ?? "disabled"
  }
  catch (error) {
    console.log(`Error: ${error}`);
    //throw new Error(`Error: ${error}`);
  }
  finally {
    cloudFormationClient.destroy()
    return orgCfnStatus
  }
};

export default getOrgCloudFormation;