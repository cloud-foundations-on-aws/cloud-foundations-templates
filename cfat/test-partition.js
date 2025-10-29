// Simple test script to verify partition detection
const { STSClient, GetCallerIdentityCommand } = require('@aws-sdk/client-sts');

async function testPartitionDetection() {
  const region = process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || 'us-east-1';
  const stsClient = new STSClient({ region });
  
  try {
    const command = new GetCallerIdentityCommand({});
    const response = await stsClient.send(command);
    
    if (response.Arn) {
      const arnParts = response.Arn.split(':');
      const partition = arnParts[1];
      
      let defaultRegion;
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
      
      console.log(`Detected partition: ${partition}`);
      console.log(`Default region for partition: ${defaultRegion}`);
      console.log(`Current region: ${region}`);
      console.log(`Account ID: ${response.Account}`);
      
      return { partition, defaultRegion };
    }
  } catch (error) {
    console.error("Error detecting partition:", error);
    return { partition: 'aws', defaultRegion: 'us-east-1' };
  } finally {
    stsClient.destroy();
  }
}

testPartitionDetection();