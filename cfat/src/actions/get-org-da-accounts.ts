import { OrganizationsClient, ListDelegatedAdministratorsCommand, ListDelegatedServicesForAccountCommand} from "@aws-sdk/client-organizations";
import { OrgDelegatedAdminAccount } from '../types';

async function getOrgDaAccounts(): Promise<OrgDelegatedAdminAccount[]> {
  let orgDaDetails: OrgDelegatedAdminAccount[] = []
  const orgClient = new OrganizationsClient({ region: 'us-east-1' });
  let orgDaDetail: OrgDelegatedAdminAccount = {}
  try {
    const command = new ListDelegatedAdministratorsCommand({});
    const response = await orgClient.send(command);
    if(response.DelegatedAdministrators){
      for (const da of response.DelegatedAdministrators) {
        const input = {AccountId: da.Id};
        const command = new ListDelegatedServicesForAccountCommand(input);
        const accountResponse = await orgClient.send(command);
        if(accountResponse.DelegatedServices){
          orgDaDetail = {
            services: accountResponse.DelegatedServices,
            accountName: da.Name
          }
          orgDaDetails.push(orgDaDetail)
        }
      }
    }
  } catch (error) {
    console.log(`Error looking for delegated services.`)
  }
  finally {
    orgClient.destroy();
  }
 return orgDaDetails;
};

export default getOrgDaAccounts;