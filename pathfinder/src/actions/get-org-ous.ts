import { OrganizationsClient, ListOrganizationalUnitsForParentCommand, ListOrganizationalUnitsForParentResponse, ListAccountsForParentCommand } from "@aws-sdk/client-organizations";
import { OUInfo } from '../types';


async function getOrgTopLevelOus(region:string, rootOuId: string ): Promise<OUInfo[]>  {
  const orgClient = new OrganizationsClient({ region });
  let topLevelOus: OUInfo[] = []
  try {
    const listOUsCommand = new ListOrganizationalUnitsForParentCommand({
      ParentId: rootOuId,
    });
    const listOUsResponse: ListOrganizationalUnitsForParentResponse = await orgClient.send(listOUsCommand);
    if(listOUsResponse.OrganizationalUnits){
      for (const ou of  listOUsResponse.OrganizationalUnits ){
        let topLevelOu:OUInfo = {
          id: ou.Id,
          name: ou.Name
        }
        const accountResponse = await orgClient.send(new ListAccountsForParentCommand({ ParentId: ou.Id }));
        if(accountResponse.Accounts && accountResponse.Accounts.length > 0){
          topLevelOu.accounts = accountResponse.Accounts
        }
        topLevelOus.push(topLevelOu)
      }
    }
  } catch (error) {
    console.error('Error checking service access:', error);
    return []
  } finally {
    orgClient.destroy();
  }
  return topLevelOus
};

export default getOrgTopLevelOus