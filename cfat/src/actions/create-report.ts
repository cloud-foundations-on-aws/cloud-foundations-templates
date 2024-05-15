import { CloudFoundationAssessment } from '../types';
import * as tasks from './tasks.js';
import { Console } from 'node:console'
import { Transform } from 'node:stream'

const ts = new Transform({ transform(chunk, enc, cb) { cb(null, chunk) } })
const logger = new Console({ stdout: ts })

function getTable (data:any) {
  logger.table(data)
  return (ts.read() || '').toString()
}

async function createReport(assessment:CloudFoundationAssessment): Promise<string> {
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
        report+=`\n    INCOMPLETE: ${check.task}`;
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
  report+=`\n\nMANAGEMENT ACCOUNT RECOMMENDED TASKS:`;
  let mgtTaskNumber:number = 1
  const managementAccountWaypoint:string = "Management Account"
  if (assessment.iamUserChecks && assessment.iamUserChecks.length > 0) {
    for(const iamUser of assessment.iamUserChecks){
      const message:string = await tasks.removeIamUserTask(mgtTaskNumber, managementAccountWaypoint, iamUser.userName)
      report+=`\n  ${ message }`;
      mgtTaskNumber++
      if(iamUser.accessKeyId){
        const message:string = await tasks.removeIamUserApiKeyTask(mgtTaskNumber, managementAccountWaypoint, iamUser.userName, iamUser.accessKeyId)
        report+=`\n  ${ message }`;
        mgtTaskNumber++
      }
    }
  }
  if(assessment.ec2Checks && assessment.ec2Checks.find(param => param.ec2Found === true)){
    for (const ec2 of assessment.ec2Checks){
      if(ec2.ec2Found && ec2.region){
        const message:string = await tasks.deleteEc2(mgtTaskNumber, managementAccountWaypoint, ec2.region );
        report+=`\n  ${ message }`;
        mgtTaskNumber++
      }
    }
  }
  if(assessment.vpcChecks && assessment.vpcChecks.length >0){
    for(const vpcFind of assessment.vpcChecks){
      if(vpcFind.vpcFound && vpcFind.region){
        const message:string = await tasks.deleteVpc(mgtTaskNumber, managementAccountWaypoint, vpcFind.region)
        report+=`\n  ${ message }`;
        mgtTaskNumber++
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
  report+=`\n\nGOVERNANCE RECOMMENDED TASKS:`;
  const govWaypoint:string = "Governance"
  let govTaskNumber: number = 1
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(govTaskNumber, govWaypoint, "AWS CloudTrail");
    report+=`\n  ${message}`;
    govTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'config.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(govTaskNumber, govWaypoint, "AWS Config");
    report+=`\n  ${message}`;
    govTaskNumber++
  }
  if(!assessment.scpEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(govTaskNumber, govWaypoint, "Service Control Policy");
    report+=`\n  ${message}`;
    govTaskNumber++
  }
  if(!assessment.tagPolicyEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(govTaskNumber, govWaypoint, "Tag Policy");
    report+=`\n  ${message}`;
    govTaskNumber++
  }
  if(!assessment.backupPolicyEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(govTaskNumber, govWaypoint, "Backup Policy");
    report+=`\n  ${message}`;
    govTaskNumber++
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                FINANCIAL MANAGEMENT`;
  report+=`\n*********************************************************`;
  report+=`\n\nLegacy CUR`;
  report+=`\n  Is legacy CUR setup: ${assessment.isLegacyCurSetup}`;
  report+=`\n\nCLOUD FINANCIAL MANAGEMENT RECOMMENDED TASKS:`;
  let finTaskNumber: number = 1
  const finWaypoint:string = "Cloud Financial Management"
  if(!assessment.isLegacyCurSetup){
    const message:string = await tasks.enableAwsCur(finTaskNumber, finWaypoint);
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
  report+=`\n\nMULTI-ACCOUNT STRATEGY RECOMMENDED TASKS:`;
  let masTaskNumber: number = 1;
  let masWaypoint:string = 'Multi-Account Strategy';
  const message:string = await tasks.reviewAccountEmailAddresses(masTaskNumber, masWaypoint);
    report+=`\n  ${message}`;
    masTaskNumber++
  if(!assessment.scpEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(masTaskNumber, masWaypoint, "Service Control Policy");
    report+=`\n  ${message}`;
    masTaskNumber++
  }
  if(!transitionalFound){
    const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Transitional");
    report+=`\n  ${message}`;
    masTaskNumber++
  }
  if(!suspendedFound){
    const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Suspended");
    report+=`\n  ${message}`;
    masTaskNumber++
  }
  if(!workloadsFound){
    const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Workloads");
    report+=`\n  ${message}`;
    masTaskNumber++
  }
  if(!securityFound){
    const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Security");
    report+=`\n  ${message}`;
    masTaskNumber++
  }
  if(!infrastructureFound){
    const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Infrastructure");
    report+=`\n  ${message}`;
    masTaskNumber++
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
  report+=`\n\nLANDING ZONE RECOMMENDED TASKS:`;
  let lzTaskNumber: number = 1
  const lzWaypoint:string = "Landing Zone"
  if(assessment.controlTowerRegion === undefined){
    const message:string = await tasks.deployControlTowerTask(lzTaskNumber, lzWaypoint);
    report+=`\n  ${message}`;
    lzTaskNumber++
  }
  if(assessment.controlTowerDriftStatus === 'DRIFTED'){
    const message:string = await tasks.fixLzDrift(lzTaskNumber, lzWaypoint);
    report+=`\n  ${message}`;
    lzTaskNumber++
  }
  if(assessment.controlTowerDeployedVersion !== assessment.controlTowerLatestAvailableVersion){
    const currentVersion:string = assessment.controlTowerDeployedVersion ?? ""
    const latestVersion:string = assessment.controlTowerLatestAvailableVersion ?? ""
    const message:string = await tasks.updateLzControlTowerTask(lzTaskNumber, lzWaypoint, currentVersion, latestVersion);
    report+=`\n  ${message}`;
    lzTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'member.org.stacksets.cloudformation.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(lzTaskNumber, lzWaypoint, "AWS CloudFormation");
    report+=`\n  ${message}`;
    lzTaskNumber++
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
  report+=`\n\nIDENTITY RECOMMENDED TASKS:`;
  let ssoTaskNumber: number = 1
  const ssoWaypoint:string = 'Identity'

  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'sso.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(ssoTaskNumber, ssoWaypoint, "AWS IAM Identity Center");
    report+=`\n  ${message}`;
    ssoTaskNumber++
  }
  if(!identityDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(ssoTaskNumber, ssoWaypoint, "AWS IAM Identity Center");
    report+=`\n  ${message}`;
    ssoTaskNumber++
  }
  if(!assessment.scpEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(ssoTaskNumber, ssoWaypoint, "Service Control Policy");
    report+=`\n  ${message}`;
    ssoTaskNumber++
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
  report+=`\n\nSECURITY RECOMMENDED TASKS:`;
  let secTaskNumber: number = 1
  const secWaypoint:string = "Security"
  if(!assessment.scpEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(secTaskNumber, secWaypoint, "Service Control Policy");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'guardduty.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS GuardDuty");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'securityhub.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS SecurityHub");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'access-analyzer.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS IAM Access Analyzer");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS CloudTrail");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'config.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS Config");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!securityHubDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "Security Hub");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!guardDutyDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "GuardDuty");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!configDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "AWS Config");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!iamAccessAnalyzerDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "AWS IAM Access Analyzer");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  if(!s3StorageLensDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "S3 Storage Lens");
    report+=`\n  ${message}`;
    secTaskNumber++
  }
  report+=`\n\n*********************************************************`;
  report+=`\n                    NETWORK`;
  report+=`\n*********************************************************`;

  report+=`\n\nNETWORK RECOMMENDED TASKS:`;
  let netTaskNumber: number = 1
  const networkWaypoint:string = 'Network'
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'guardduty.amazonaws.com')){
    const netGuardDutyEnableMessage:string = await tasks.enableAwsOrganizationService(netTaskNumber, networkWaypoint, "AWS GuardDuty");
    report+=`\n  ${netGuardDutyEnableMessage}`;
    netTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'ipam.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(netTaskNumber, networkWaypoint, "AWS IPAM");
    report+=`\n  ${message}`;
    netTaskNumber++
  }
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'ram.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(netTaskNumber, networkWaypoint, "AWS Resource Access Manager");
    report+=`\n  ${message}`;
    netTaskNumber++
  }
  if(!ipamDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(netTaskNumber, networkWaypoint, "AWS IPAM");
    report+=`\n  ${message}`;
    netTaskNumber++
  }
  if(!assessment.scpEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(netTaskNumber, networkWaypoint, "Service Control Policy");
    report+=`\n  ${message}`;
    netTaskNumber++
	}
  report+=`\n\n*********************************************************`;
  report+=`\n                  OBSERVABILITY`;
  report+=`\n*********************************************************`;
  
  report+=`\n\nOBSERVABILITY RECOMMENDED TASKS:`;
  let obTaskNumber: number = 1
  const obWaypoint:string = 'Observability'
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'account.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(obTaskNumber, obWaypoint, "Account Manager");
    report+=`\n  ${message}`;
    obTaskNumber++
  }
  if(!accountDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(obTaskNumber, obWaypoint, "Account Manager");
    report+=`\n  ${message}`;
    obTaskNumber++
  }
  report+=`\n\n*********************************************************`;
  report+=`\n               BACKUP AND RECOVERY`;
  report+=`\n*********************************************************`;
  report+=`\n\nBACKUP AND RECOVERY RECOMMENDED TASKS:`;
  let backTaskNumber: number = 1
  const backupWaypoint:string = 'Backup and Recovery'
  if(!assessment.orgServices || !assessment.orgServices.find(param=> param.service === 'backup.amazonaws.com')){
    const message:string = await tasks.enableAwsOrganizationService(backTaskNumber, backupWaypoint, "AWS Backup");
    report+=`\n  ${message}`;
    backTaskNumber++
  }
  if(!backupDelegated){
    const message:string = await tasks.delegateAdministrationAwsService(backTaskNumber, backupWaypoint, "AWS Backup");
    report+=`\n  ${message}`;
    backTaskNumber++
  }
  if(!assessment.backupPolicyEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(backTaskNumber, backupWaypoint, "Backup Policy");
    report+=`\n  ${message}`;
    backTaskNumber++
  }
  if(!assessment.scpEnabled) {
    const message:string = await tasks.enablePolicyTypeTask(backTaskNumber, backupWaypoint, "Service Control Policy");
    report+=`\n  ${message}`;
    backTaskNumber++
  }
  report+=`\n\n\n  END REVIEW`;
  return report
}

export default createReport;