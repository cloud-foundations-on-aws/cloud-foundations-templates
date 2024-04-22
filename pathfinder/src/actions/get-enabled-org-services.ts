import { OrganizationsClient, ListAWSServiceAccessForOrganizationCommand, ListAWSServiceAccessForOrganizationResponse } from "@aws-sdk/client-organizations";
import { OrgService} from '../types';


async function getEnabledOrgServices(region:string): Promise<OrgService[]>  {
  const discoveredOrgServices: OrgService[] = []
  const orgClient = new OrganizationsClient({ region });
  try {
    const orgServiceAccessCommand = new ListAWSServiceAccessForOrganizationCommand({});
    const orgServiceAccessResponse: ListAWSServiceAccessForOrganizationResponse = await orgClient.send(orgServiceAccessCommand);
    if(orgServiceAccessResponse.EnabledServicePrincipals && orgServiceAccessResponse.EnabledServicePrincipals.length > 0){
      orgServiceAccessResponse.EnabledServicePrincipals
      for(const orgService of orgServiceAccessResponse.EnabledServicePrincipals){
        const foundOrgService: OrgService = {service: orgService.ServicePrincipal ?? ""}
        discoveredOrgServices.push(foundOrgService)
      }
    }
  } catch (error) {
    console.error('Error checking service access:', error);
  } finally {
    orgClient.destroy();
    return discoveredOrgServices;
  }
};

export default getEnabledOrgServices