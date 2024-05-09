import { DelegatedServices } from "@aws-sdk/client-organizations";

export interface CfatCheck {
  title:string;
  description:string;
  pass:boolean;
  required:boolean;
  weight:number 
}

export interface AccountType {
  isInOrganization: boolean;
  isManagementAccount?: boolean;
};

export interface ControlTowerInfo {
  controlTowerRegion?: string;
  latestAvailableVersion?: string;
  deployedVersion?: string
  driftStatus?: string;
  status?: string
}

export interface Ec2Check {
  region?: string;
  ec2Found?: boolean
}

export interface CloudTrailInfo{
  region?: string;
  trailFound?: boolean;
  isOrgTrail?: boolean;
  isMultiRegion?: boolean;
}
export interface VpcCheck {
  region?: string;
  vpcFound?: boolean
}
export interface IamUserInfo {
  userName: string;
  accessKeyId?: string;
  lastUsed?: string;
};

export interface IdCInfo{
  found: boolean;
  region?: string
  arn?: string;
  id?: string;
}

export interface LegacyCurInfo{
  isLegacyCurSetup: boolean;
};

export interface OrgService {
  service: string;
};

export interface OrgInfo {
  arn?: string,
  id?: string,
  rootOuId?: string
}

interface OUInfo {
  id?: string;
  name?: string;
  accounts?: Account[];
}

export interface OrgCloudFormationStatus {
  status: string
};

export interface PolicyTypesEnabled {
  scpEnabled: boolean;
  tagPolicyEnabled: boolean;
  backupPolicyEnabled: boolean;
};

export interface OrgDelegatedAdminAccounts {
  accountName?: string;
  services?: DelegatedServices[];
}

export interface ConfigInfo {
  region?: string;
  configRecorderFound?: boolean
  configDeliveryChannelFound?: boolean
}

export interface OrgMemberAccount {
  accountName?: string;
  accountEmail?: string;
}