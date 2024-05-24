import { CloudFoundationAssessment, Task } from '../types';

// backlog is a series of tasks put together that will close
// any necessary findings from the CFAT checks
async function createBacklog(assessment: CloudFoundationAssessment): Promise<Task[]> {
  let tasks: Task[] = [];
  if (assessment.iamUserChecks && assessment.iamUserChecks.length > 0) {
    for (const iamUser of assessment.iamUserChecks) {
      let iamTask: Task = {
        title: `Remove IAM user ${iamUser.userName}`,
        detail: `Review and determine if IAM user ${iamUser.userName} can be deleted.`,
        remediationLink: ""
      }
      tasks.push(iamTask);

      if (iamUser.accessKeyId) {
        let iamApiTask: Task = {
          title: `Remove IAM user ${iamUser.userName} API key ${iamUser.accessKeyId} `,
          detail: `Review and determine if IAM user API key ${iamUser.accessKeyId} for ${iamUser.userName} can be removed.`,
          remediationLink: "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_manage.html#id_users_deleting"
        }
        tasks.push(iamApiTask);
      }
    }
  }
  if (assessment.ec2Checks && assessment.ec2Checks.find(param => param.ec2Found === true)) {
    for (const ec2 of assessment.ec2Checks) {
      if (ec2.ec2Found && ec2.region) {
        let ec2Task: Task = {
          title: `Delete EC2 instance in ${ec2.region}`,
          detail: `Delete any unnecessary EC2 instance in ${ec2.region}`,
          remediationLink: "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html"
        }
        tasks.push(ec2Task);
      }
    }
  }
  if (assessment.vpcChecks && assessment.vpcChecks.length > 0) {
    for (const vpcFind of assessment.vpcChecks) {
      if (vpcFind.vpcFound && vpcFind.region) {
        let vpcTask: Task = {
          title: `Delete VPC in ${vpcFind.region}`,
          detail: `Delete any unnecessary VPC in ${vpcFind.region} to include the default VPC.`,
          remediationLink: "https://github.com/cloud-foundations-on-aws/cloud-foundations-templates/blob/main/network/network-default-vpc-deletion/README.md"
        }
        tasks.push(vpcTask);
      }
    }
  }

  if (!assessment.scpEnabled) {
    const scpEnabledTask: Task = {
      title: 'Enable SCP',
      detail: `Enable SCP in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html"
    }
    tasks.push(scpEnabledTask);
  }
  if (!assessment.tagPolicyEnabled) {
    let tagPolicyEnabledTask: Task = {
      title: 'Enable Tag Policy',
      detail: `Enable Tag Policy in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html"
    }
    tasks.push(tagPolicyEnabledTask);
  }
  if (!assessment.backupPolicyEnabled) {
    let backupPolicyEnabledTask: Task = {
      title: 'Enable Backup Policy',
      detail: `Enable Backup Policy in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html"
    }
    tasks.push(backupPolicyEnabledTask);
  }
  if (!assessment.isLegacyCurSetup) {
    const legacyCurSetupTask: Task = {
      title: 'Setup legacy CUR',
      detail: `Setup legacy CUR in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/cur/latest/userguide/dataexports-create-legacy.html"
    }
    tasks.push(legacyCurSetupTask);
  }
  let transitionalFound, suspendedFound, infrastructureFound: boolean = false;
  let workloadsFound: boolean = false;
  let securityFound: boolean = false;
  if (assessment.orgRootOuId) {
    if (assessment.orgOuInfo && assessment.orgOuInfo.length > 0) {
      for (const ou of assessment.orgOuInfo) {
        if (ou.name?.toLowerCase() === 'suspended') { suspendedFound = true }
        if (ou.name?.toLowerCase() === 'transitional') { transitionalFound = true }
        if (ou.name?.toLowerCase() === 'workloads') { workloadsFound = true }
        if (ou.name?.toLowerCase() === 'security') { securityFound = true }
        if (ou.name?.toLowerCase() === 'infrastructure') { infrastructureFound = true }
      }
    }
  }
  let identityDelegated: boolean = false
  let securityHubDelegated: boolean = false
  let guardDutyDelegated: boolean = false
  let configDelegated: boolean = false
  let iamAccessAnalyzerDelegated: boolean = false
  let s3StorageLensDelegated: boolean = false
  let ipamDelegated: boolean = false
  let accountDelegated: boolean = false
  let backupDelegated: boolean = false
  if (assessment.orgDelegatedAdminAccounts && assessment.orgDelegatedAdminAccounts.length > 0) {
    for (const account of assessment.orgDelegatedAdminAccounts) {
      if (account.services && account.services.length > 0) {
        for (const srv of account.services) {
          if (srv.ServicePrincipal === 'securityhub.amazonaws.com') { securityHubDelegated = true }
          if (srv.ServicePrincipal === 'guardduty.amazonaws.com') { guardDutyDelegated = true }
          if (srv.ServicePrincipal === 'sso.amazonaws.com') { identityDelegated = true }
          if (srv.ServicePrincipal === 'config.amazonaws.com') { configDelegated = true }
          if (srv.ServicePrincipal === 'access-analyzer.amazonaws.com') { iamAccessAnalyzerDelegated = true }
          if (srv.ServicePrincipal === 'storage-lens.s3.amazonaws.com') { s3StorageLensDelegated = true }
          if (srv.ServicePrincipal === 'ipam.amazonaws.com') { ipamDelegated = true }
          if (srv.ServicePrincipal === 'account.amazonaws.com') { accountDelegated = true }
          if (srv.ServicePrincipal === 'backup.amazonaws.com') { backupDelegated = true }
        }
      }
    }
  }
  const accountEmailReviewTask: Task = {
    title: 'Review account email addresses',
    detail: `Review Account Email Addresses in AWS Organization`,
    remediationLink: "https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html#ru-bp-group"
  }
  tasks.push(accountEmailReviewTask);
  // OUs
  if (!transitionalFound) {
    const transitionalTask: Task = {
      title: 'Deploy Transitional OU',
      detail: `Deploy Transitional OU in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/transitional-ou.html"
    }
    tasks.push(transitionalTask);
  }
  if (!suspendedFound) {
    const suspendedTask: Task = {
      title: 'Deploy Suspended OU',
      detail: `Deploy Suspended OU in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/suspended-ou.html"
    }
    tasks.push(suspendedTask);
  }
  if (!workloadsFound) {
    const workloadsTask: Task = {
      title: 'Deploy Workloads OU',
      detail: `Deploy Workloads OU in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/workloads-ou.html"
    }
    tasks.push(workloadsTask);
  }
  if (!securityFound) {
    const securityTask: Task = {
      title: 'Deploy Security OU',
      detail: `Deploy Security OU in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/security-ou-and-accounts.html"
    }
    tasks.push(securityTask);
  }
  if (!infrastructureFound) {
    const infrastructureTask: Task = {
      title: 'Deploy Infrastructure OU',
      detail: `Deploy Infrastructure OU in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/infrastructure-ou-and-accounts.html"
    }
    tasks.push(infrastructureTask);
  }
  // Control Tower
  if (assessment.controlTowerRegion === undefined) {
    const deployControlTowerTask: Task = {
      title: 'Deploy AWS Control Tower',
      detail: `Deploy AWS Control Tower in AWS Organization`,
      remediationLink: "https://catalog.workshops.aws/control-tower/en-US/prerequisites/deploying"
    }
    tasks.push(deployControlTowerTask);
  }
  if (assessment.controlTowerDriftStatus === 'DRIFTED') {
    const fixLzDriftTask: Task = {
      title: 'Fix drift in deployed landing zone',
      detail: `Fix drift in deployed landing zone`,
      remediationLink: "https://docs.aws.amazon.com/controltower/latest/userguide/resolve-drift.html"
    }
    tasks.push(fixLzDriftTask);
  }
  if (assessment.controlTowerDeployedVersion !== assessment.controlTowerLatestAvailableVersion) {
    const updateControlTowerTask: Task = {
      title: `Update AWS Control Tower to latest version`,
      detail: `Update AWS Control Tower to version ${assessment.controlTowerLatestAvailableVersion}`,
      remediationLink: "https://docs.aws.amazon.com/controltower/latest/userguide/update-controltower.html"
    }
    tasks.push(updateControlTowerTask);
  }
  // cloudtrail
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'cloudtrail.amazonaws.com')) {
    const ctOrgServiceTask: Task = {
      title: 'Enable AWS CloudTrail',
      detail: `Enable AWS CloudTrail in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/controltower/latest/userguide/resolve-drift.html"
    }
    tasks.push(ctOrgServiceTask);
  }

  // S3 Storage Lens
  if (!s3StorageLensDelegated) {
    const taskS3StorageLensDelegated: Task = {
      title: 'Delegate administration of Amazon S3 Storage Lens',
      detail: `Delegate administration to Amazon S3 Storage Lens`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-s3lens.html#integrate-enable-da-s3lens"
    }
    tasks.push(taskS3StorageLensDelegated);
  }
  // CloudFormation
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'member.org.stacksets.cloudformation.amazonaws.com')) {
    const orgServiceCfnEnableTask: Task = {
      title: 'Enable AWS CloudFormation',
      detail: `Enable AWS CloudFormation in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-activate-trusted-access.html"
    }
    tasks.push(orgServiceCfnEnableTask);
  }
  // Identity Center
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'sso.amazonaws.com')) {
    const ssoTask: Task = {
      title: 'Enable AWS Single Sign-On',
      detail: `Enable AWS Single Sign-On in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/singlesignon/latest/userguide/get-set-up-for-idc.html"
    }
    tasks.push(ssoTask);
  }
  if (!identityDelegated) {
    const identityDelegatedTask: Task = {
      title: 'Delegate administration to AWS IAM Identity Center',
      detail: `Delegate administration to AWS IAM Identity Center`,
      remediationLink: "https://docs.aws.amazon.com/singlesignon/latest/userguide/delegated-admin.html"
    }
    tasks.push(identityDelegatedTask);
  }
  // SecurityHub
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'securityhub.amazonaws.com')) {
    const taskSecurityHubDelegated: Task = {
      title: 'Delegate administration to AWS Security Hub',
      detail: `Delegate administration to AWS Security Hub`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-securityhub.html#integrate-enable-ta-securityhub"
    }
    tasks.push(taskSecurityHubDelegated);
  }
  if (!securityHubDelegated) {
    const taskSecurityHubDelegated: Task = {
      title: 'Delegate administration of AWS Security Hub',
      detail: `Delegate administration to AWS Security Hub`,
      remediationLink: "https://docs.aws.amazon.com/securityhub/latest/userguide/designate-orgs-admin-account.html"
    }
    tasks.push(taskSecurityHubDelegated);
  }
  // IAM Access Analyzer
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'access-analyzer.amazonaws.com')) {
    const taskIamAccessAnalyzerDelegated: Task = {
      title: 'Delegate administration to AWS IAM Access Analyzer',
      detail: `Delegate administration to AWS IAM Access Analyzer`,
      remediationLink: "https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-getting-started.html#access-analyzer-enabling"
    }
    tasks.push(taskIamAccessAnalyzerDelegated);
  }
  if (!iamAccessAnalyzerDelegated) {
    const taskIamAccessAnalyzerDelegated: Task = {
      title: 'Delegate administration of AWS IAM Access Analyzer',
      detail: `Delegate administration to AWS IAM Access Analyzer`,
      remediationLink: "https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-settings.html"
    }
    tasks.push(taskIamAccessAnalyzerDelegated);
  }
  // GuardDuty
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'guardduty.amazonaws.com')) {
    const taskGuardDutyDelegated: Task = {
      title: 'Enable AWS GuardDuty',
      detail: `Enable AWS GuardDuty in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-guardduty.html#integrate-enable-ta-guardduty"
    }
    tasks.push(taskGuardDutyDelegated);
  }
  if (!guardDutyDelegated) {
    const taskGuardDutyDelegated: Task = {
      title: 'Delegate administration of AWS GuardDuty',
      detail: `Delegate administration to AWS GuardDuty`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-guardduty.html"
    }
    tasks.push(taskGuardDutyDelegated);
  }
  // Config
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'config.amazonaws.com')) {
    const configOrgServiceTask: Task = {
      title: 'Enable AWS Config',
      detail: `Enable AWS Config in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-config.html#integrate-enable-ta-config"
    }
    tasks.push(configOrgServiceTask);
  }
  if (!configDelegated) {
    const taskConfigDelegated: Task = {
      title: 'Delegate administration of AWS Config',
      detail: `Delegate administration to AWS Config`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-config.html"
    }
    tasks.push(taskConfigDelegated);
  }
  // RAM
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'ram.amazonaws.com')) {
    const orgServiceRamTask: Task = {
      title: 'Enable AWS Resource Access Manager',
      detail: `Enable AWS Resource Access Manager in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-ram.html#integrate-enable-ta-ram"
    }
    tasks.push(orgServiceRamTask);
  }
  // IPAM
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'ipam.amazonaws.com')) {
    const orgServiceIpamTask: Task = {
      title: 'Enable AWS IPAM',
      detail: `Enable AWS IPAM in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-ipam.html"
    }
    tasks.push(orgServiceIpamTask);
  }
  if (!ipamDelegated) {
    const taskIpamDelegated: Task = {
      title: 'Delegate administration of AWS IPAM',
      detail: `Delegate administration to AWS IPAM`,
      remediationLink: "https://docs.aws.amazon.com/vpc/latest/ipam/enable-integ-ipam.html"
    }
    tasks.push(taskIpamDelegated);
  }
  // Account Manager
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'account.amazonaws.com')) {
    const orgServiceAccountTask: Task = {
      title: 'Enable AWS Account',
      detail: `Enable AWS Account in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/accounts/latest/reference/using-orgs-delegated-admin.html"
    }
    tasks.push(orgServiceAccountTask);
  }
  if (!accountDelegated) {
    const taskAccountDelegated: Task = {
      title: 'Delegate administration of AWS Account management',
      detail: `Delegate administration to AWS Account contact management`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-account.html#integrate-enable-da-account"
    }
    tasks.push(taskAccountDelegated);
  }
  // Backup
  if (!assessment.orgServices || !assessment.orgServices.find(param => param.service === 'backup.amazonaws.com')) {
    const orgServiceBackupTask: Task = {
      title: 'Enable AWS Backup',
      detail: `Enable AWS Backup in AWS Organization`,
      remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-backup.html#integrate-enable-ta-backup"
    }
    tasks.push(orgServiceBackupTask);
  }
  if (!backupDelegated) {
    const taskBackupDelegated: Task = {
      title: 'Delegate administration of AWS Backup',
      detail: `Delegate administration to AWS Backup`,
      remediationLink: "https://docs.aws.amazon.com/aws-backup/latest/devguide/manage-cross-account.html#backup-delegatedadmin"
    }
    tasks.push(taskBackupDelegated);
  }

  return tasks
}

export default createBacklog;