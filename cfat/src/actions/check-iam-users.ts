import { IamUserInfo } from '../types';
import { IAMClient, ListUsersCommand, ListAccessKeysCommand, GetAccessKeyLastUsedCommand } from "@aws-sdk/client-iam";

// function list all IAM users and if they have keys in the management account
const checkIamUsers = async (): Promise<IamUserInfo[]> => {
  // Set to us-east-1 as IAM is global and region isn't a concern
  const iamClient = new IAMClient({ region: 'us-east-1' });
  const iamUserInfo: IamUserInfo[] = [];
  try {
    const listUsersCommand = new ListUsersCommand({});
    const listUsersResponse = await iamClient.send(listUsersCommand);
    for (const user of listUsersResponse.Users || []) {
      const userName = user.UserName || "";
      const listAccessKeysCommand = new ListAccessKeysCommand({
        UserName: userName,
      });
      const listAccessKeysResponse = await iamClient.send(listAccessKeysCommand);
      const accessKeys = listAccessKeysResponse.AccessKeyMetadata || [];
      if (accessKeys.length > 0) {
        for (const accessKey of accessKeys) {
          const accessKeyId = accessKey.AccessKeyId || "";
          const getLastUsedCommand = new GetAccessKeyLastUsedCommand({
            AccessKeyId: accessKeyId,
          });
          const lastUsedResponse = await iamClient.send(getLastUsedCommand);
          const foundUserInfo: IamUserInfo = {
            userName,
            accessKeyId,
            lastUsed: lastUsedResponse && lastUsedResponse.AccessKeyLastUsed
              ? `${lastUsedResponse.AccessKeyLastUsed.LastUsedDate}` || "Not available"
              : "Not available",
          };
          iamUserInfo.push(foundUserInfo);
        }
      } else {
        const foundUserInfo: IamUserInfo = {
          userName
        };
        iamUserInfo.push(foundUserInfo);
      }
    }
  } catch (error) {
    console.error("Error:", error);
  } finally {
    iamClient.destroy();
  }
  return iamUserInfo;
};

export default checkIamUsers;