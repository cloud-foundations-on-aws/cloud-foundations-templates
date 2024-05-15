import { AccountType } from '../types';

import { STSClient, GetCallerIdentityCommand } from "@aws-sdk/client-sts";
import { OrganizationsClient, DescribeOrganizationCommand, } from "@aws-sdk/client-organizations";

async function getAccountId(region:string): Promise<string> {
  const stsClient:STSClient = new STSClient({region});
  try {
    const getCallerIdentityCommand = new GetCallerIdentityCommand({});
    const Account  = await stsClient.send(getCallerIdentityCommand);
    return Account.Account!
  } catch (error) {
    console.error("Error getting account ID:", error);
    throw error;
  }
};

// function checking if management account, member account, or standalone account
export const defineAccountType = async (region: string): Promise<AccountType> => {
  const organizationsClient = new OrganizationsClient({ region });
  let isInOrganization:boolean = false
  let isManagementAccount:boolean = false
  try {
    const currentAccountId:string = await getAccountId(region);
    if(currentAccountId){
      const describeOrganizationCommand = new DescribeOrganizationCommand({});
      const describeOrganizationResponse = await organizationsClient.send(describeOrganizationCommand);
      // the account is not standalone and part of AWS Organization
      if (describeOrganizationResponse.Organization?.MasterAccountId) {
        const managementAccountId:string = describeOrganizationResponse.Organization?.MasterAccountId
        if(managementAccountId == currentAccountId){
          // this is an organization and this is the management account
          isManagementAccount = true;
          isInOrganization = true;
        }
        else{
          // there is an organization, but this isn't the management account
          isInOrganization = true;
        }
      } else {
        // there isn't an organization and this account is standalone
        isInOrganization = false;
      }
    }
  } catch (error) {
    console.error("Error:", error);
  } finally {
    organizationsClient.destroy();
  }
  return { isInOrganization, isManagementAccount };
};