import { DelegatedServices } from "@aws-sdk/client-organizations";

export interface CfatCheck {
  check:string;
  description:string;
  status:string;
  required:boolean;
  weight:number
  loe:number
  remediationLink?: string;
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

export interface OrgDelegatedAdminAccount {
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

export interface Task {
  title: string;
  category?: string;
  detail?:string;
  remediationLink?: string;
}

export interface CloudFoundationAssessment {
  organizationDeploy?: Boolean;
  managementAccount?: Boolean;
  isLegacyCurSetup?: Boolean;
  vpcChecks?: VpcCheck[];
  ec2Checks?: Ec2Check[];
  iamUserChecks?: IamUserInfo[];
  orgArn?: string,
  orgId?: string,
  orgRootOuId?: string;
  orgServices?: OrgService[]
  orgCloudFormationStatus?: string;
  orgMemberAccounts?: OrgMemberAccount[];
  orgDelegatedAdminAccounts?: OrgDelegatedAdminAccount[];
  orgOuInfo?: OUInfo[];
  controlTowerRegion?: string;
  controlTowerLatestAvailableVersion?: string;
  controlTowerDeployedVersion?: string
  controlTowerDriftStatus?: string;
  controlTowerStatus?: string;
  scpEnabled?: boolean;
  tagPolicyEnabled?: boolean;
  backupPolicyEnabled?: boolean;
  configDetails?: ConfigInfo[];
  cloudTrailDetails?: CloudTrailInfo[];
  idcInfo?: IdCInfo;
  cfatChecks?: CfatCheck[];
}

interface JiraCSVData {
  [key: string]: {
    Summary: string;
    Description: string;
    Status: string;
  };
}

interface CSVOptions {
  headers?: { [key: string]: string };
  filename?: string;
}