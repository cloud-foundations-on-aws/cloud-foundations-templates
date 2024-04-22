import { EC2Client, DescribeRegionsCommand, DescribeRegionsResult } from "@aws-sdk/client-ec2";

async function getAllRegions(): Promise<string[]> {
  // grabbing all regions from us-east-1
  const ec2Client = new EC2Client({ region: "us-east-1" });
  try {
    const describeRegionsCommand = new DescribeRegionsCommand({});
    const response = await ec2Client.send(describeRegionsCommand);
    const regions: string[] = [];
    for (const region of response.Regions || []) {
      regions.push(region.RegionName || "");
    }
    return regions
  } catch (error) {
    console.error("Error retrieving regions:", error);
    return []
  } finally {
    ec2Client.destroy();
  }
}

export default getAllRegions