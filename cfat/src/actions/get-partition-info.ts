import { STSClient, GetCallerIdentityCommand } from "@aws-sdk/client-sts";

export interface PartitionInfo {
  partition: string;
  defaultRegion: string;
}

async function getPartitionInfo(): Promise<PartitionInfo> {
  const region = process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || 'us-east-1';
  const stsClient = new STSClient({ region });
  
  try {
    const command = new GetCallerIdentityCommand({});
    const response = await stsClient.send(command);
    
    if (response.Arn) {
      const arnParts = response.Arn.split(':');
      const partition = arnParts[1];
      
      // Determine default region based on partition
      let defaultRegion: string;
      switch (partition) {
        case 'aws-us-gov':
          defaultRegion = 'us-gov-west-1';
          break;
        case 'aws-cn':
          defaultRegion = 'cn-north-1';
          break;
        case 'aws':
        default:
          defaultRegion = 'us-east-1';
          break;
      }
      
      return { partition, defaultRegion };
    }
    
    // Fallback to standard AWS partition
    return { partition: 'aws', defaultRegion: 'us-east-1' };
  } catch (error) {
    console.error("Error detecting partition:", error);
    // Fallback to standard AWS partition
    return { partition: 'aws', defaultRegion: 'us-east-1' };
  } finally {
    stsClient.destroy();
  }
}

export default getPartitionInfo;