import { SSOAdminClient,
  ListInstancesCommand
} from "@aws-sdk/client-sso-admin";
import { IdCInfo } from "../types";

async function getIdcInfo(regionList: string[]): Promise<IdCInfo> {
  let idcDetails: IdCInfo = {found: false}
  for (const region of regionList){
    const ssoAdminClient = new SSOAdminClient({region});
    try {
      const ssoInput = {
        MaxResults: Number("100")
      };
      const command = new ListInstancesCommand(ssoInput);
      const ssoInstanceResponse = await ssoAdminClient.send(command);
      if (ssoInstanceResponse.Instances && ssoInstanceResponse.Instances.length > 0) {
        const ssoInstance = ssoInstanceResponse.Instances[0];
        idcDetails.found = true;
        idcDetails.region = region;
        idcDetails.arn = ssoInstance.InstanceArn
        idcDetails.id = ssoInstance.IdentityStoreId
        break
      }
    } catch (error) {
      console.log(`Error looking for AWS Identity Center details in region ${region}`)
    }
    finally {
      ssoAdminClient.destroy();
    }
 }
 return idcDetails;
};

export default getIdcInfo;