import { ConfigServiceClient, DescribeConfigurationRecorderStatusCommand, DescribeDeliveryChannelsCommand } from '@aws-sdk/client-config-service';
import { ConfigInfo } from '../types';

async function checkConfigExists(regions: string[]): Promise<ConfigInfo[]> {
  let configDetails:ConfigInfo[] = [];
  for (const region of regions) {
    const configServiceClient = new ConfigServiceClient({ region });
    let configDetail: ConfigInfo = {
      region: region,
      configRecorderFound: false,
      configDeliveryChannelFound: false
    }
    try {
      // Check if Config recorder exists
      const recorderResponse = await configServiceClient.send(new DescribeConfigurationRecorderStatusCommand({}));
      const recorderExists = recorderResponse.ConfigurationRecordersStatus?.length !== 0;
      if(recorderExists){
        configDetail.configRecorderFound = true
      }
      // Check if Config delivery channel exists
      const channelResponse = await configServiceClient.send(new DescribeDeliveryChannelsCommand({}));
      const channelExists = channelResponse.DeliveryChannels?.length !== 0;
      if(channelExists){
        configDetail.configDeliveryChannelFound = true
      }
    configDetails.push(configDetail)
    } catch (error) {
      console.error(`Error checking AWS Config in ${region}:`, error);
    }
    finally {
      configServiceClient.destroy();
    }
  }
  return configDetails;
}

export default checkConfigExists