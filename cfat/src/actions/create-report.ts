import { DetachClassicLinkVpcCommand } from '@aws-sdk/client-ec2';
import { CloudFoundationAssessment, Task } from '../types';
import { Console } from 'node:console'
import { Transform } from 'node:stream'
import * as fs from 'fs';

const ts = new Transform({ transform(chunk, enc, cb) { cb(null, chunk) } })
const logger = new Console({ stdout: ts })

function getTable (data:any) {
  logger.table(data)
  return (ts.read() || '').toString()
}

async function createReport(assessment:CloudFoundationAssessment): Promise<Task[]> {
  let tasks:Task[] = [];
  let dateTime = new Date()
  const reportFile = "./cfat.txt"
  let report:string = "Cloud Foundation Assessment Tool"
	report+=`\nGenerated on: ${dateTime.toUTCString()} \n\n`;
  let score:number = 0;
  let totalRequiredLoe:number = 0;
	let totalScore:number= 0;
	let cfatStatus:string = "COMPLETE";
  if(assessment.cfatChecks && assessment.cfatChecks.length > 0){
	  report+= `\nIncomplete Requirements:`;
    for (const check of assessment.cfatChecks) {
      totalScore += check.weight;
      if (check.required === true && check.status === 'incomplete') {
        report+=`\n    INCOMPLETE: ${check.check}`;
        totalRequiredLoe += check.loe
        cfatStatus = "INCOMPLETE";
      }
      if(check.status === 'complete'){
        score += check.weight;
      }
    }
    report+= `\n\n====================================\n`;
    report+= `\nFoundation Status: ${cfatStatus}`;
    if(cfatStatus === "INCOMPLETE"){
      report+= `\nEstimate of Required Level of Effort (LOE): ${totalRequiredLoe} hours`;
    }
	  report+= `\nCFAT Score: ${score} out of ${totalScore}`;
    report+= `\n\n====================================\n`;
    report+= `\nFoundation Checks:\n`;
    if(assessment.cfatChecks && assessment.cfatChecks.length > 0){
      const strTable = getTable(assessment.cfatChecks)
      report+= `${strTable}`
    }
  }
  report+= `\n\nStart Detailed Report:\n\n`;
	report+=`\n*********************************************************`;
	report+=`\n                   MANAGEMENT ACCOUNT`;
	report+=`\n*********************************************************`;
	report+=`\n\nAWS ACCOUNT TYPE\n`;
  report+=`\n  Is in AWS Organization: ${assessment.organizationDeploy}`;
  report+=`\n  Assessing AWS Management Account: ${assessment.managementAccount}`;

  report+=`\n\nIAM USERS CHECK\n`;
  if (assessment.iamUserChecks && assessment.iamUserChecks.length > 0) {
		for(const iamUser of assessment.iamUserChecks){
			report+=`\n  IAM User: ${iamUser.userName}`;
			if(iamUser.accessKeyId){
				report+=`\n    User API Key ID: ${iamUser.accessKeyId}`;
			}
			report+=`\n`;
		}
	} else {
		report+=`\n  No IAM Users found.`;
	}
  report+=`\n\nEC2 INSTANCE CHECK\n`;
  if(assessment.ec2Checks && assessment.ec2Checks.find(param => param.ec2Found === true)){
		for (const ec2 of assessment.ec2Checks ){
			if(ec2.ec2Found){
				report+=`\n  ${ec2.region} - found EC2 Instance(s).`;
			}
		}
	}else {
		report+=`\n  No EC2 instances found.`;
	}
  report+=`\n\nVPC CHECK\n`;
  if(assessment.vpcChecks && assessment.vpcChecks.length >0){
		for(const vpcFind of assessment.vpcChecks){
			if(vpcFind.vpcFound){
				report+=`\n  ${vpcFind.region} - found VPC(s).`;
			}
		}
	} else {
		report+=`\n  No VPCs found.`;
	}
  report+=`\n\nAWS CONFIG CHECK\n`;
	if(assessment.configDetails && assessment.configDetails.find(param => param.configRecorderFound === true)){
		for (const configFind of assessment.configDetails){
			if(configFind.configRecorderFound){
				report+=`\n  ${configFind.region} - Config Recorder found`;
			}
			if(configFind.configDeliveryChannelFound){
				report+=`\n  ${configFind.region} - Config Delivery Channel found`;
			}
		}
	} else{
		report+=`\n  No AWS Config resource discovered`;
	}
  report+=`\n\nMANAGEMENT ACCOUNT TASKS:`;
  const maCategory:string = "Management Account"
  if (assessment.iamUserChecks && assessment.iamUserChecks.length > 0) {
    for(const iamUser of assessment.iamUserChecks){
      let iamTask:Task={title:`Remove IAM user ${iamUser.userName}`, category: maCategory, detail: `Review and determine if IAM user ${iamUser.userName} can be deleted.`}
      const message:string = `${iamTask.title} - ${iamTask.category} - ${iamTask.detail}`
      tasks.push(iamTask);
      report+=`\n  ${ message }`;
      if(iamUser.accessKeyId){
        let iamApiTask:Task={title:`Remove IAM user ${iamUser.userName} API key ${iamUser.accessKeyId} `, category: maCategory, detail: `Review and determine if IAM user API key ${iamUser.accessKeyId} for ${iamUser.userName} can be removed.`}
        const message:string = `${iamApiTask.title} - ${iamApiTask.category} - ${iamApiTask.detail}`
        report+=`\n  ${ message }`;
        tasks.push(iamApiTask);
      }
    }
  }
  if(assessment.ec2Checks && assessment.ec2Checks.find(param => param.ec2Found === true)){
    for (const ec2 of assessment.ec2Checks){
      if(ec2.ec2Found && ec2.region){
        let ec2Task:Task={title:`Delete EC2 instance in ${ec2.region}`, category: maCategory, detail: `Delete any unnecessary EC2 instance in ${ec2.region}`}
        const message:string = `${ec2Task.title} - ${ec2Task.category} - ${ec2Task.detail}`
        report+=`\n  ${ message }`;
        tasks.push(ec2Task);
      }
    }
  }
  if(assessment.vpcChecks && assessment.vpcChecks.length >0){
    for(const vpcFind of assessment.vpcChecks){
      if(vpcFind.vpcFound && vpcFind.region){
        let vpcTask:Task={title:`Delete VPC in ${vpcFind.region}`, category: maCategory, detail: `Delete any unnecessary VPC in ${vpcFind.region} to include the default VPC.`}
        const message:string = `${vpcTask.title} - ${vpcTask.category} - ${vpcTask.detail}`
        report+=`\n  ${ message }`;
        tasks.push(vpcTask);
      }
    }
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                    GOVERNANCE`;
  report+=`\n*********************************************************`;
  report+=`\n\nAWS ORGANIZATION POLICY TYPES\n`;
  report+=`\n  Service Control Policies (SCP) enabled: ${assessment.scpEnabled}`;
  report+=`\n  Tag Policies enabled: ${assessment.tagPolicyEnabled}`;
  report+=`\n  Backup Policies enabled: ${assessment.backupPolicyEnabled}`;
  report+=`\n\nAWS ORGANIZATION CLOUDFORMATION\n`;
  report+=`\n  AWS CloudFormation Organization stack sets status : ${assessment.orgCloudFormationStatus}`;
  report+=`\n\nCLOUDTRAIL CHECK\n`;
  if(assessment.cloudTrailDetails && assessment.cloudTrailDetails.length > 0) {
    for(const ctFind of assessment.cloudTrailDetails){
      if(ctFind.trailFound){
        report+=`\n  CloudTrail found in ${ctFind.region}`;
        report+=`\n    Is Organization Trail: ${ctFind.isOrgTrail}`;
        report+=`\n    Is MultiRegion: ${ctFind.isMultiRegion}`;
        report+=`\n`;
      }
    }
  }else {
    report+=`\n  No AWS CloudTrail resource discovered`;
  }
  report+=`\n\nGOVERNANCE SERVICES ENABLED IN AWS ORGANIZATION:\n`;
  if(assessment.orgServices){
    if(assessment.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
      report+=`\n  AWS CloudTrail`;
    }
    if(assessment.orgServices.find(param=> param.service === 'config.amazonaws.com')){
      report+=`\n  AWS Config`;
    }
  }else{
    report+=`\n  No governance service enabled`;
  }

  ///// SET THE BACKLOG TASK FOR GOVERNANCE /////
  report+=`\n\nGOVERNANCE TASKS:`;
  const govCategory:string = "Governance"
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
    const ctOrgServiceTask:Task = {title:'Enable AWS CloudTrail', category: govCategory, detail: `Enable AWS CloudTrail in AWS Organization`}
    tasks.push(ctOrgServiceTask);
    const message:string = `${ctOrgServiceTask.title} - ${ctOrgServiceTask.category} - ${ctOrgServiceTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'config.amazonaws.com')){
    const configOrgServiceTask:Task = {title: 'Enable AWS Config', category: govCategory, detail: `Enable AWS Config in AWS Organization`}
    tasks.push(configOrgServiceTask);
    const message:string = `${configOrgServiceTask.title} - ${configOrgServiceTask.category} - ${configOrgServiceTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.scpEnabled) {
    const scpEnabledTask:Task = {title: 'Enable SCP', category: govCategory, detail: `Enable SCP in AWS Organization`}
    tasks.push(scpEnabledTask);
    const message:string = `${scpEnabledTask.title} - ${scpEnabledTask.category} - ${scpEnabledTask.detail}`
    report+=`\n  ${message}`;

  }
  if(!assessment.tagPolicyEnabled) {
    let tagPolicyEnabledTask:Task = {title: 'Enable Tag Policy', category: govCategory, detail: `Enable Tag Policy in AWS Organization`}
    tasks.push(tagPolicyEnabledTask);
    const message:string = `${tagPolicyEnabledTask.title} - ${tagPolicyEnabledTask.category} - ${tagPolicyEnabledTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.backupPolicyEnabled) {
    let backupPolicyEnabledTask:Task = {title: 'Enable Backup Policy', category: govCategory, detail: `Enable Backup Policy in AWS Organization`}
    tasks.push(backupPolicyEnabledTask);
    const message:string = `${backupPolicyEnabledTask.title} - ${backupPolicyEnabledTask.category} - ${backupPolicyEnabledTask.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                FINANCIAL MANAGEMENT`;
  report+=`\n*********************************************************`;
  report+=`\n\nLegacy CUR`;
  report+=`\n  Is legacy CUR setup: ${assessment.isLegacyCurSetup}`;
  report+=`\n\nCLOUD FINANCIAL MANAGEMENT TASKS:`;
  const finCategory:string = "Cloud Financial Management"
  if(!assessment.isLegacyCurSetup){
    const legacyCurSetupTask:Task={title:'Setup legacy CUR', category: finCategory, detail: `Setup legacy CUR in AWS Organization`}
    tasks.push(legacyCurSetupTask);
    const message:string = `${legacyCurSetupTask.title} - ${legacyCurSetupTask.category} - ${legacyCurSetupTask.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                MULTI-ACCOUNT STRATEGY`;
  report+=`\n*********************************************************`;
  report+=`\n\nAWS ORGANIZATION DETAILS\n`;
  report+=`\n  AWS Organization Id: ${assessment.orgId}`;
  report+=`\n  AWS Organization ARN: ${assessment.orgArn}`;
  report+=`\n  AWS Organization Root OU Id: ${assessment.orgRootOuId}`;
  report+=`\n\nAWS ORGANIZATION CLOUDFORMATION\n`;
  report+=`\n  AWS CloudFormation Organization stack sets status : ${assessment.orgCloudFormationStatus}`;
  let transitionalFound,suspendedFound,infrastructureFound:boolean = false;
	let workloadsFound:boolean = false;
	let securityFound:boolean = false;
  if(assessment.orgRootOuId){
    report+=`\n\nAWS ORGANIZATION TOP-LEVEL ORGANIZATION UNITS\n`;
    report+=`\n  List of Organization's top-level OUs and AWS accounts:`;
    if(assessment.orgOuInfo && assessment.orgOuInfo.length > 0){
      for (const ou of assessment.orgOuInfo){
        if(ou.name?.toLowerCase() === 'suspended'){suspendedFound = true}
        if(ou.name?.toLowerCase() === 'transitional'){transitionalFound = true}
        if(ou.name?.toLowerCase() === 'workloads'){workloadsFound=true}
        if(ou.name?.toLowerCase() === 'security'){securityFound=true}
        if(ou.name?.toLowerCase() === 'infrastructure'){infrastructureFound=true}
        report+=`\n    Organizational Unit: ${ou.name}`;
        report+=`\n      Organizational Unit Id: ${ou.id}`;
        if(ou.accounts && ou.accounts.length > 0){
          report+=`\n      AWS Accounts:`;
          for (const account of ou.accounts){
            report+=`\n        ${account.Name}`;
          }
          report+=`\n`;
        }
        else{
          report+=`\n      AWS Accounts: None`;
          report+=`\n`;
        }
      }

    } else {
      report+=`\n  No top level OUs found.`;
    }
  }
  report+=`\n\nAWS ORGANIZATION MEMBER ACCOUNTS\n`;
  if(assessment.orgMemberAccounts && assessment.orgMemberAccounts.length > 0){
    for (const memberAccount of assessment.orgMemberAccounts){
      report+=`\n  Account: ${memberAccount.accountName}`;
      report+=`\n  Account Email: ${memberAccount.accountEmail}\n`;
    }
  } else {
    report+=`No member accounts found which is amazing as this is running from one.`;
  }
  report+=`\n\nAWS ORGANIZATION ENABLED SERVICES\n`;
  report+=`\n  The following AWS Services are enabled within your AWS Organization:`;
  if(assessment.orgServices && assessment.orgServices.length > 0){
    for (const orgService of assessment.orgServices){
      report+=`\n    ${orgService.service}`;
    }
  } else{
    report+=`\n    No trusted access enabled in the AWS Organization`;
  }
  let identityDelegated:boolean = false
  let securityHubDelegated:boolean = false
  let guardDutyDelegated:boolean = false
  let configDelegated:boolean = false
  let iamAccessAnalyzerDelegated:boolean = false
  let s3StorageLensDelegated:boolean = false
  let ipamDelegated:boolean = false
  let accountDelegated:boolean = false
  let backupDelegated:boolean = false
  report+=`\n\nAWS ORGANIZATION INTEGRATED SERVICE REGISTERED DELEGATED ADMINS\n`;
  if(assessment.orgDelegatedAdminAccounts && assessment.orgDelegatedAdminAccounts.length > 0){
    for (const account of assessment.orgDelegatedAdminAccounts){
      report+=`\n  Account: ${account.accountName}`;
      if(account.services && account.services.length > 0 ){
        report+=`\n  Delegated Services:`;
        for (const srv of account.services){
          report+=`\n    ${srv.ServicePrincipal}`;
          if(srv.ServicePrincipal === 'securityhub.amazonaws.com'){securityHubDelegated=true}
          if(srv.ServicePrincipal === 'guardduty.amazonaws.com'){guardDutyDelegated=true}
          if(srv.ServicePrincipal === 'sso.amazonaws.com'){identityDelegated=true}
          if(srv.ServicePrincipal === 'config.amazonaws.com'){configDelegated=true}
          if(srv.ServicePrincipal === 'access-analyzer.amazonaws.com'){iamAccessAnalyzerDelegated=true}
          if(srv.ServicePrincipal === 'storage-lens.s3.amazonaws.com'){s3StorageLensDelegated=true}
          if(srv.ServicePrincipal === 'ipam.amazonaws.com'){ipamDelegated=true}
          if(srv.ServicePrincipal === 'account.amazonaws.com'){accountDelegated=true}
          if(srv.ServicePrincipal === 'backup.amazonaws.com'){backupDelegated=true}
        }
      }
      report+=`\n `;
    }
  } else {
    report+=`\n  No delegated admin accounts in AWS Organization`;
  }
  report+=`\n\nMULTI-ACCOUNT STRATEGY TASKS:`;
  let masCategory:string = 'Multi-Account Strategy';
  const accountEmailReviewTask:Task = {title: 'Review Account Email Addresses', category: masCategory, detail: `Review Account Email Addresses in AWS Organization`}
  const message:string = `${accountEmailReviewTask.title} - ${accountEmailReviewTask.category} - ${accountEmailReviewTask.detail}`
    report+=`\n  ${message}`;
  if(!assessment.scpEnabled) {
    const scpEnabledTask:Task = {title: 'Enable Service Control Policy', category: masCategory, detail: `Enable Service Control Policy in AWS Organization`}
    tasks.push(scpEnabledTask);
    const message:string = `${scpEnabledTask.title} - ${scpEnabledTask.category} - ${scpEnabledTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!transitionalFound){
    const transitionalTask:Task = {title: 'Deploy Transitional OU', category: masCategory, detail: `Deploy Transitional OU in AWS Organization`}
    tasks.push(transitionalTask);
    const message:string = `${transitionalTask.title} - ${transitionalTask.category} - ${transitionalTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!suspendedFound){
    const suspendedTask:Task = {title: 'Deploy Suspended OU', category: masCategory, detail: `Deploy Suspended OU in AWS Organization`}
    tasks.push(suspendedTask);
    const message:string = `${suspendedTask.title} - ${suspendedTask.category} - ${suspendedTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!workloadsFound){
    const workloadsTask:Task = {title: 'Deploy Workloads OU', category: masCategory, detail: `Deploy Workloads OU in AWS Organization`}
    tasks.push(workloadsTask);
    const message:string = `${workloadsTask.title} - ${workloadsTask.category} - ${workloadsTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!securityFound){
    const securityTask:Task = {title: 'Deploy Security OU', category: masCategory, detail: `Deploy Security OU in AWS Organization`}
    tasks.push(securityTask);
    const message:string = `${securityTask.title} - ${securityTask.category} - ${securityTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!infrastructureFound){
    const infrastructureTask:Task = {title: 'Deploy Infrastructure OU', category: masCategory, detail: `Deploy Infrastructure OU in AWS Organization`}
    tasks.push(infrastructureTask);
    const message:string = `${infrastructureTask.title} - ${infrastructureTask.category} - ${infrastructureTask.detail}`
    report+=`\n  ${message}`;
  }

  report+=`\n\n*********************************************************`;
  report+=`\n                  LANDING ZONE`;
  report+=`\n*********************************************************`;
  report+=`\n\nAWS CONTROL TOWER\n`;
  if(assessment.controlTowerRegion){
    report+=`\n  Control Tower home region: ${assessment.controlTowerRegion}`;
    report+=`\n  Control Tower status: ${assessment.controlTowerStatus}`;
    report+=`\n  Control Tower Landing Zone version: ${assessment.controlTowerDeployedVersion}`;
    report+=`\n  Latest available version: ${assessment.controlTowerLatestAvailableVersion}`;
    report+=`\n  Drift Status: ${assessment.controlTowerDriftStatus}`;
  }else {
    report+=`\n  AWS Control Tower is not deployed in the AWS Organization`;
  }
  report+=`\n\nLANDING ZONE TASKS:`;
  let lzTaskNumber: number = 1
  const lzWaypoint:string = "Landing Zone"
  if(assessment.controlTowerRegion === undefined){
    const deployControlTowerTask:Task = {title: 'Deploy AWS Control Tower', category: lzWaypoint, detail: `Deploy AWS Control Tower in AWS Organization`}
    tasks.push(deployControlTowerTask);
    const message:string = `${deployControlTowerTask.title} - ${deployControlTowerTask.category} - ${deployControlTowerTask.detail}`
    report+=`\n  ${message}`;
  }
  if(assessment.controlTowerDriftStatus === 'DRIFTED'){
    const fixLzDriftTask:Task = {title: 'Fix drift in deployed landing zone', category: lzWaypoint, detail: `Fix drift in deployed landing zone`}
    tasks.push(fixLzDriftTask);
    const message:string = `${fixLzDriftTask.title} - ${fixLzDriftTask.category} - ${fixLzDriftTask.detail}`
    report+=`\n  ${message}`;
  }
  if(assessment.controlTowerDeployedVersion !== assessment.controlTowerLatestAvailableVersion){
    const updateControlTowerTask:Task = {title: `Update AWS Control Tower to latest version`, category: lzWaypoint, detail: `Update AWS Control Tower to version ${assessment.controlTowerLatestAvailableVersion}`}
    tasks.push(updateControlTowerTask);
    const message:string = `${updateControlTowerTask.title} - ${updateControlTowerTask.category} - ${updateControlTowerTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'member.org.stacksets.cloudformation.amazonaws.com')){
    const orgServiceCfnEnableTask:Task = {title: 'Enable AWS CloudFormation', category: lzWaypoint, detail: `Enable AWS CloudFormation in AWS Organization`}
    tasks.push(orgServiceCfnEnableTask);
    const message:string = `${orgServiceCfnEnableTask.title} - ${orgServiceCfnEnableTask.category} - ${orgServiceCfnEnableTask.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                    IDENTITY`;
  report+=`\n*********************************************************`;
  if(assessment.idcInfo){
    report+=`\n\nAWS IAM IDENTITY CENTER\n`;
    report+=`\n  IdC Region: ${assessment.idcInfo.region}`;
    report+=`\n  IdC ARN: ${assessment.idcInfo.arn}`;
    report+=`\n  IdC Instance Id: ${assessment.idcInfo.id}`;
  }else{
    report+=`\n\nAWS IAM IDENTITY CENTER NOT FOUND\n`;
  }
  report+=`\n\nIDENTITY TASKS:`;
  const ssoCategory:string = 'Identity'

  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'sso.amazonaws.com')){
    const ssoTask:Task = {title: 'Enable AWS Single Sign-On', category: ssoCategory, detail: `Enable AWS Single Sign-On in AWS Organization`}
    tasks.push(ssoTask);
    const message:string = `${ssoTask.title} - ${ssoTask.category} - ${ssoTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!identityDelegated){
    const identityDelegatedTask:Task = {title: 'Delegate administration to AWS IAM Identity Center', category: ssoCategory, detail: `Delegate administration to AWS IAM Identity Center`}
    tasks.push(identityDelegatedTask);
    const message:string = `${identityDelegatedTask.title} - ${identityDelegatedTask.category} - ${identityDelegatedTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.scpEnabled) {
    const ssoTask:Task = {title: 'Enable AWS Single Sign-On', category: ssoCategory, detail: `Enable AWS Single Sign-On in AWS Organization`}
    tasks.push(ssoTask);
    const message:string = `${ssoTask.title} - ${ssoTask.category} - ${ssoTask.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                    SECURITY`;
  report+=`\n*********************************************************`;
  report+=`\n\nAWS SECURITY SERVICES ENABLED IN AWS ORGANIZATION:\n`;
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'guardduty.amazonaws.com')){
    report+=`\n  AWS GuardDuty`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'securityhub.amazonaws.com')){
    report+=`\n  AWS Security Hub`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'access-analyzer.amazonaws.com')){
    report+=`\n  IAM Access Analyzer`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'macie.amazonaws.com')){
    report+=`\n  Macie`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'storage-lens.s3.amazonaws.com')){
    report+=`\n  Amazon S3 Storage Lens`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'inspector2.amazonaws.com')){
    report+=`\n  Amazon Inspector`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
    report+=`\n  AWS CloudTrail`;
  }
  if(assessment.orgServices && assessment.orgServices.find(param=> param.service === 'config.amazonaws.com')){
    report+=`\n  AWS Config`;
  }
  report+=`\n\nSECURITY TASKS:`;
  const secCategory:string = "Security"
  if(!assessment.scpEnabled) {
    const ssoTask:Task = {title: 'Enable AWS Single Sign-On', category: secCategory, detail: `Enable AWS Single Sign-On in AWS Organization`}
    tasks.push(ssoTask);
    const message:string = `${ssoTask.title} - ${ssoTask.category} - ${ssoTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'guardduty.amazonaws.com')){
    const taskGuardDutyDelegated:Task = {title: 'Delegate administration to AWS GuardDuty', category: secCategory, detail: `Delegate administration to AWS GuardDuty`}
    tasks.push(taskGuardDutyDelegated);
    const message:string = `${taskGuardDutyDelegated.title} - ${taskGuardDutyDelegated.category} - ${taskGuardDutyDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'securityhub.amazonaws.com')){
    const taskSecurityHubDelegated:Task = {title: 'Delegate administration to AWS Security Hub', category: secCategory, detail: `Delegate administration to AWS Security Hub`}
    tasks.push(taskSecurityHubDelegated);
    const message:string = `${taskSecurityHubDelegated.title} - ${taskSecurityHubDelegated.category} - ${taskSecurityHubDelegated.detail}`
    report+=`\n  ${message}`;
  }

  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'access-analyzer.amazonaws.com')){
    const taskIamAccessAnalyzerDelegated:Task = {title: 'Delegate administration to AWS IAM Access Analyzer', category: secCategory, detail: `Delegate administration to AWS IAM Access Analyzer`}
    tasks.push(taskIamAccessAnalyzerDelegated);
    const message:string = `${taskIamAccessAnalyzerDelegated.title} - ${taskIamAccessAnalyzerDelegated.category} - ${taskIamAccessAnalyzerDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
    const taskCloudTrailDelegated:Task = {title: 'Delegate administration to AWS CloudTrail', category: secCategory, detail: `Delegate administration to AWS CloudTrail`}
    tasks.push(taskCloudTrailDelegated);
    const message:string = `${taskCloudTrailDelegated.title} - ${taskCloudTrailDelegated.category} - ${taskCloudTrailDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'config.amazonaws.com')){
    const taskConfigDelegated:Task = {title: 'Delegate administration to AWS Config', category: secCategory, detail: `Delegate administration to AWS Config`}
    tasks.push(taskConfigDelegated);
    const message:string = `${taskConfigDelegated.title} - ${taskConfigDelegated.category} - ${taskConfigDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!securityHubDelegated){
    const taskSecurityHubDelegated:Task = {title: 'Delegate administration of AWS Security Hub', category: secCategory, detail: `Delegate administration to AWS Security Hub`}
    tasks.push(taskSecurityHubDelegated);
    const message:string = `${taskSecurityHubDelegated.title} - ${taskSecurityHubDelegated.category} - ${taskSecurityHubDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!guardDutyDelegated){
    const taskGuardDutyDelegated:Task = {title: 'Delegate administration of AWS GuardDuty', category: secCategory, detail: `Delegate administration to AWS GuardDuty`}
    tasks.push(taskGuardDutyDelegated);
    const message:string = `${taskGuardDutyDelegated.title} - ${taskGuardDutyDelegated.category} - ${taskGuardDutyDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!configDelegated){
    const taskConfigDelegated:Task = {title: 'Delegate administration of AWS Config', category: secCategory, detail: `Delegate administration to AWS Config`}
    tasks.push(taskConfigDelegated);
    const message:string = `${taskConfigDelegated.title} - ${taskConfigDelegated.category} - ${taskConfigDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!iamAccessAnalyzerDelegated){
    const taskIamAccessAnalyzerDelegated:Task = {title: 'Delegate administration of AWS IAM Access Analyzer', category: secCategory, detail: `Delegate administration to AWS IAM Access Analyzer`}
    tasks.push(taskIamAccessAnalyzerDelegated);
    const message:string = `${taskIamAccessAnalyzerDelegated.title} - ${taskIamAccessAnalyzerDelegated.category} - ${taskIamAccessAnalyzerDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!s3StorageLensDelegated){
    const taskS3StorageLensDelegated:Task = {title: 'Delegate administration of Amazon S3 Storage Lens', category: secCategory, detail: `Delegate administration to Amazon S3 Storage Lens`}
    tasks.push(taskS3StorageLensDelegated);
    const message:string = `${taskS3StorageLensDelegated.title} - ${taskS3StorageLensDelegated.category} - ${taskS3StorageLensDelegated.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                    NETWORK`;
  report+=`\n*********************************************************`;

  report+=`\n\nNETWORK TASKS:`;
  const networkCategory:string = 'Network'
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'guardduty.amazonaws.com')){
    const taskGuardDutyDelegated:Task = {title: 'Enable AWS GuardDuty', category: networkCategory, detail: `Enable AWS GuardDuty in AWS Organization`}
    tasks.push(taskGuardDutyDelegated);
    const message:string = `${taskGuardDutyDelegated.title} - ${taskGuardDutyDelegated.category} - ${taskGuardDutyDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'ipam.amazonaws.com')){
    const orgServiceIpamTask:Task={title: 'Enable AWS IPAM', category: networkCategory, detail: `Enable AWS IPAM in AWS Organization`}
    tasks.push(orgServiceIpamTask);
    const message:string = `${orgServiceIpamTask.title} - ${orgServiceIpamTask.category} - ${orgServiceIpamTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'ram.amazonaws.com')){
    const orgServiceRamTask:Task={title: 'Enable AWS Resource Access Manager', category: networkCategory, detail: `Enable AWS Resource Access Manager in AWS Organization`}
    tasks.push(orgServiceRamTask);
    const message:string = `${orgServiceRamTask.title} - ${orgServiceRamTask.category} - ${orgServiceRamTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!ipamDelegated){
    const taskIpamDelegated:Task = {title: 'Delegate administration of AWS IPAM', category: networkCategory, detail: `Delegate administration to AWS IPAM`}
    tasks.push(taskIpamDelegated);
    const message:string = `${taskIpamDelegated.title} - ${taskIpamDelegated.category} - ${taskIpamDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.scpEnabled) {
    const taskScpDelegated:Task = {title: 'Enable AWS Service Control Policy', category: networkCategory, detail: `Enable AWS Service Control Policy in AWS Organization`}
    tasks.push(taskScpDelegated);
    const message:string = `${taskScpDelegated.title} - ${taskScpDelegated.category} - ${taskScpDelegated.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                  OBSERVABILITY`;
  report+=`\n*********************************************************`;

  report+=`\n\nOBSERVABILITY TASKS:`;
  const obCategory:string = 'Observability'
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'account.amazonaws.com')){
    const orgServiceAccountTask:Task={title: 'Enable AWS Account', category: obCategory, detail: `Enable AWS Account in AWS Organization`}
    tasks.push(orgServiceAccountTask);
    const message:string = `${orgServiceAccountTask.title} - ${orgServiceAccountTask.category} - ${orgServiceAccountTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!accountDelegated){
    const taskAccountDelegated:Task = {title: 'Delegate administration of AWS Account', category: obCategory, detail: `Delegate administration to AWS Account`}
    tasks.push(taskAccountDelegated);
    const message:string = `${taskAccountDelegated.title} - ${taskAccountDelegated.category} - ${taskAccountDelegated.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n*********************************************************`;
  report+=`\n               BACKUP AND RECOVERY`;
  report+=`\n*********************************************************`;
  report+=`\n\nBACKUP AND RECOVERY TASKS:`;
  const backupWaypoint:string = 'Backup and Recovery'
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'backup.amazonaws.com')){
    const orgServiceBackupTask:Task={title: 'Enable AWS Backup', category: backupWaypoint, detail: `Enable AWS Backup in AWS Organization`}
    tasks.push(orgServiceBackupTask);
    const message:string = `${orgServiceBackupTask.title} - ${orgServiceBackupTask.category} - ${orgServiceBackupTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!backupDelegated){
    const taskBackupDelegated:Task = {title: 'Delegate administration of AWS Backup', category: backupWaypoint, detail: `Delegate administration to AWS Backup`}
    tasks.push(taskBackupDelegated);
    const message:string = `${taskBackupDelegated.title} - ${taskBackupDelegated.category} - ${taskBackupDelegated.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.backupPolicyEnabled) {
    const backupPolicyEnabledTask:Task = {title: 'Enable AWS Backup Policy', category: backupWaypoint, detail: `Enable AWS Backup Policy in AWS Organization`}
    tasks.push(backupPolicyEnabledTask);
    const message:string = `${backupPolicyEnabledTask.title} - ${backupPolicyEnabledTask.category} - ${backupPolicyEnabledTask.detail}`
    report+=`\n  ${message}`;
  }
  if(!assessment.scpEnabled) {
    const enablePolicyTypeTask:Task = {title: 'Enable AWS Service Control Policy', category: backupWaypoint, detail: `Enable AWS Service Control Policy in AWS Organization`}
    tasks.push(enablePolicyTypeTask);
    const message:string = `${enablePolicyTypeTask.title} - ${enablePolicyTypeTask.category} - ${enablePolicyTypeTask.detail}`
    report+=`\n  ${message}`;
  }
  report+=`\n\n\n  END REVIEW`;
  const reportFilePath:string = "./cfat.txt"
	console.log(`compiling report...`)
	console.log(`saving report to ./cfat/cfat.txt...`)
  fs.appendFileSync(reportFilePath, report);

  return tasks
}

export default createReport;