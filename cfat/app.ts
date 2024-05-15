import {defineAccountType} from './src/actions/define-account-type.js';
import checkIamUsers from './src/actions/check-iam-users.js';
import getEnabledOrgPolicyTypes from './src/actions/get-enabled-org-policy-types.js';
import getEnabledOrgServices from './src/actions/get-enabled-org-services.js'
import getOrgCloudFormation from './src/actions/check-org-cloudformation.js';
import getIdcInfo from './src/actions/get-idc-info.js';
import getOrgDetails from './src/actions/get-org-details.js'
import getOrgTopLevelOus from './src/actions/get-org-ous.js';
import getAllRegions from './src/actions/get-regions.js';
import checkEc2Exists from './src/actions/check-ec2-existence.js';
import checkVpcExists from './src/actions/check-vpc-existence.js';
import checkCloudTrailExists from './src/actions/check-cloudtrail-existence.js';
import getOrgDaAccounts from './src/actions/get-org-da-accounts.js';
import checkConfigExists from './src/actions/check-config-existence.js';
import getOrgMemberAccounts from './src/actions/get-org-member-accounts.js';
import getControlTower from './src/actions/check-control-tower.js';
import checkLegacyCur from './src/actions/check-legacy-cur.js';
import createReport from './src/actions/create-report.js'
import * as tasks from './src/actions/tasks.js';
import { CfatCheck, CloudFoundationAssessment } from './src/types/index.js';
import * as fs from 'fs';

const main = async (): Promise<void> => {
	let report:CloudFoundationAssessment = {};
  let CfatChecks:CfatCheck[] = [];
	const region =  process.env.AWS_REGION || 'us-east-1';
	const allRegions = await getAllRegions();
	console.log("discovering your AWS environment...")
	const accountType = await defineAccountType(region);
	let transitionalFound,suspendedFound,infrastructureFound:boolean = false;
	let workloadsFound:boolean = false;
	let securityFound:boolean = false;
	let cfatIamUserPass:boolean = false;
	let cfatIamIdPOrgServicePass:boolean = false;
	let cfatIamIdcConfiguredPass:boolean = false;
	let cfatCloudTrailPass:boolean = false;
	let cfatCloudTrailOrgTrailPass:boolean = false;
	let cfatVpcPass:boolean = true;
	let cfatEc2Pass:boolean = false;
	let cfatConfigManagementAccountPass:boolean = false;
	let cfatConfigRecorderManagementAccountPass:boolean = false;
	let cfatCloudTrailOrgServiceEnabledPass:boolean = false;
	let cfatTagPoliciesEnabledPass:boolean = false;
	let cfatScpEnabledPass:boolean = false;
	let cfatBackupPoliciesEnabledPass:boolean = false;
	let cfatOrgCloudFormationEnabledPass:boolean = false;
	let cfatOrgCloudFormationStatusPass:boolean = false;
	let cfatOrgServiceGuardDutyEnabledPass:boolean = false;
	let cfatOrgServiceSecurityHubEnabledPass:boolean = false;
	let cfatOrgServiceIamAccessAnalyzerEnabledPass:boolean = false;
	let cfatOrgServiceAwsConfigEnabledPass:boolean = false;
	let cfatOrgServiceRamEnabledPass:boolean = false;
	let cfatControlTowerDeployedPass:boolean = false;
	let cfatControlTowerNotDriftedPass:boolean = false;
	let cfatControlTowerLatestVersionPass:boolean = false;
	let cfatLogArchiveAccountPass:boolean = false;
	let cfatAuditAccountPass:boolean = false;
	let cfatManagementAccountPass:boolean = true;
	let cfatOrgServiceBackupEnabledPass = false

	if (accountType) {
		report.organizationDeploy = accountType.isInOrganization
		report.managementAccount = accountType.isManagementAccount
		if(accountType.isManagementAccount === undefined){
			accountType.isManagementAccount = false
			console.log("AWS account is not the Management Account of an AWS Organization")
		}
		cfatManagementAccountPass = accountType.isManagementAccount;
	}

	console.log("discovering IAM Users...")
	const iamUserResult = await checkIamUsers();

	if (iamUserResult && iamUserResult.length > 0) {
		console.log("IAM Users discovered.")
		report.iamUserChecks = iamUserResult;
	} else {
		cfatIamUserPass = true
	}
	console.log("discovering EC2 instances across all AWS Regions...")
	const ec2Check = await checkEc2Exists(allRegions);
	if(ec2Check && ec2Check.find(param => param.ec2Found === true)){
		report.ec2Checks = ec2Check
		console.info("warning: EC2 instances discovered.")
		for (const ec2 of ec2Check ){
			cfatEc2Pass = false;
		}
	}
	console.log("discovering VPCs across all AWS Regions...")
	const vpcCheck = await checkVpcExists(allRegions);
	report.vpcChecks = vpcCheck;
	if(vpcCheck && vpcCheck.length >0){
		cfatVpcPass = false;
		console.log("warning: VPCs discovered.")
	}
	console.log("discovering AWS Config configurations across all AWS Regions...")
	report.cloudTrailDetails = await checkCloudTrailExists(allRegions);
	report.configDetails = await checkConfigExists(allRegions);
	if(report.configDetails && report.configDetails.find(param => param.configRecorderFound === true)){
		for (const configFind of report.configDetails){
			if(configFind.configRecorderFound){
				cfatConfigManagementAccountPass = true
			}
			if(configFind.configDeliveryChannelFound){
				cfatConfigRecorderManagementAccountPass = true
			}
		}
	}
	// all the following calls require an AWS Organization to exist and the account be a management account
	if (accountType.isInOrganization && accountType.isManagementAccount) {
		console.log("collecting general AWS Organization details...")
		const orgDetails = await getOrgDetails('us-east-1');
		console.log("collecting CUR details...")
		const legacyCurCheck = await checkLegacyCur('us-east-1');
		console.log("collecting AWS Organization Policy details...")
		const enableOrgPoliciesCheck = await getEnabledOrgPolicyTypes('us-east-1');
		console.log("collecting AWS Organization service trusted access details...")
		report.orgServices = await getEnabledOrgServices('us-east-1');
		console.log("collecting AWS Organization CloudFormation status details...")
		const cfnOrgStatus = await getOrgCloudFormation(region);
		console.log("collecting AWS Control Tower details...")
		const controlTowerDetails = await getControlTower(region);
		report.idcInfo= await getIdcInfo(allRegions);
		console.log("collecting AWS Organization service delegated admin details...")
		report.orgDelegatedAdminAccounts = await getOrgDaAccounts();
		console.log("collecting AWS Organization member account details...")
		report.orgMemberAccounts = await getOrgMemberAccounts();
		report.isLegacyCurSetup = legacyCurCheck.isLegacyCurSetup
		report.orgArn = orgDetails.arn
		report.orgId = orgDetails.id
		report.orgRootOuId = orgDetails.rootOuId
		report.backupPolicyEnabled = enableOrgPoliciesCheck.backupPolicyEnabled;
		report.scpEnabled = enableOrgPoliciesCheck.scpEnabled;
		report.tagPolicyEnabled = enableOrgPoliciesCheck.tagPolicyEnabled;
		report.orgCloudFormationStatus = cfnOrgStatus.status
		report.controlTowerDeployedVersion = controlTowerDetails.deployedVersion
		report.controlTowerDriftStatus= controlTowerDetails.driftStatus
		report.controlTowerLatestAvailableVersion = controlTowerDetails.latestAvailableVersion
		report.controlTowerRegion = controlTowerDetails.controlTowerRegion
		report.controlTowerStatus = controlTowerDetails.status
		if(report.idcInfo.arn){
			cfatIamIdcConfiguredPass = true;
		}
		if(report.cloudTrailDetails && report.cloudTrailDetails.length > 0) {
			cfatCloudTrailPass = true;
			for(const ctFind of report.cloudTrailDetails){
				if(ctFind.trailFound){
					if(ctFind.isOrgTrail){cfatCloudTrailOrgTrailPass = true}
				}
			}
		}
		if(report.orgServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
			cfatCloudTrailOrgServiceEnabledPass = true;
		}
		if(report.orgServices.find(param=> param.service === 'config.amazonaws.com')){
			cfatOrgServiceAwsConfigEnabledPass = true;
		}
		if(enableOrgPoliciesCheck.scpEnabled) {
			cfatScpEnabledPass = true;
		}
		if(enableOrgPoliciesCheck.tagPolicyEnabled) {
			cfatTagPoliciesEnabledPass = true;
		}
		if(enableOrgPoliciesCheck.backupPolicyEnabled) {
			cfatBackupPoliciesEnabledPass = true;
		}
		if(orgDetails.rootOuId){
			console.log("collecting OU and member account details...")
			report.orgOuInfo = await getOrgTopLevelOus('us-east-1', orgDetails.rootOuId);
			if(report.orgOuInfo && report.orgOuInfo.length > 0){
				for (const ou of report.orgOuInfo){
					if(ou.name?.toLowerCase() === 'suspended'){suspendedFound = true}
					if(ou.name?.toLowerCase() === 'transitional'){transitionalFound = true}
					if(ou.name?.toLowerCase() === 'workloads'){workloadsFound=true}
					if(ou.name?.toLowerCase() === 'security'){securityFound=true}
					if(ou.name?.toLowerCase() === 'infrastructure'){infrastructureFound=true}
				}
			}
		}
		if(report.orgMemberAccounts && report.orgMemberAccounts.length > 0){
			for (const memberAccount of report.orgMemberAccounts){
				if(memberAccount.accountName){
					if(memberAccount.accountName.toLowerCase() === 'log archive'){cfatLogArchiveAccountPass = true;}
					if(memberAccount.accountName.toLowerCase() === 'audit'){cfatAuditAccountPass = true;}
					if(memberAccount.accountName.toLowerCase() === 'security tooling'){cfatAuditAccountPass = true;}
				}
			}
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
		if(report.orgDelegatedAdminAccounts && report.orgDelegatedAdminAccounts.length > 0){
			for (const account of report.orgDelegatedAdminAccounts){
				if(account.services && account.services.length > 0 ){
					for (const srv of account.services){
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
			}
		}
		if(controlTowerDetails.controlTowerRegion){
			cfatControlTowerDeployedPass = true;
		}
		if(controlTowerDetails.driftStatus !== 'DRIFTED'){
			cfatControlTowerNotDriftedPass = true;
		}
		if(controlTowerDetails.deployedVersion === controlTowerDetails.latestAvailableVersion){
			cfatControlTowerLatestVersionPass = true;
		}
		if(report.orgServices.find(param=> param.service === 'member.org.stacksets.cloudformation.amazonaws.com')){
			cfatOrgCloudFormationStatusPass = true
		}
		if(report.orgServices.find(param=> param.service === 'sso.amazonaws.com')){
			cfatIamIdPOrgServicePass = true;
		}
		if(report.orgServices.find(param=> param.service === 'guardduty.amazonaws.com')){
			cfatOrgServiceGuardDutyEnabledPass = true;
		}
		if(report.orgServices.find(param=> param.service === 'securityhub.amazonaws.com')){
			cfatOrgServiceSecurityHubEnabledPass = true;
		}
		if(report.orgServices.find(param=> param.service === 'access-analyzer.amazonaws.com')){
			cfatOrgServiceIamAccessAnalyzerEnabledPass = true;
		}
		if(report.orgServices.find(param=> param.service === 'ram.amazonaws.com')){
			cfatOrgServiceRamEnabledPass = true;
		}
		if(report.orgServices.find(param=> param.service === 'backup.amazonaws.com')){
			cfatOrgServiceBackupEnabledPass = true;
		}


	} else if (accountType.isInOrganization && !accountType.isManagementAccount) {
		const message:string = '\nWARNING: You are running CFAT from an account that is a member of your AWS Organization. Please run the solution from your AWS Management account.'
		console.warn(message);
	} else {
		const message:string = '\nWARNING: You are running CFAT from an account that not part of an AWS Organization. This account will be treated as a standalone account.'
		console.warn(message);
	}

	////SCORING
	let OrgCheck:CfatCheck = {
		task: "AWS Organization created",
		description: "AWS Organization is enabled.",
		status: accountType.isInOrganization ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1
	}
	CfatChecks.push(OrgCheck);

	let MACheck:CfatCheck = {
		task: "Management Account created",
		description: "AWS Management account exists.",
		status: cfatManagementAccountPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1
	}
	CfatChecks.push(MACheck);

	const cfatIamUserCheck:CfatCheck = {
		task: "Management Account IAM Users removed",
		description: "IAM Users should not exist in Management Account.",
		status: cfatIamUserPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatIamUserCheck);

	const cfatEc2Check:CfatCheck = {
		task: "Management Account EC2 instances removed",
		description: "EC2 Instances should not exist in Management Account.",
		status: cfatEc2Pass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatEc2Check);

	const cfatVpcCheck:CfatCheck = {
		task: "Management Account VPCs removed",
		description: "Management Account should not have any VPCs.",
		status: cfatVpcPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1,
		remediationLink: "https://github.com/cloud-foundations-on-aws/cloud-foundations-templates/blob/main/network/network-default-vpc-deletion/README.md"
	}
	CfatChecks.push(cfatVpcCheck);

	const cfatCloudTrailCheck:CfatCheck = {
		task: "CloudTrail Trail created",
		description: "CloudTrail should be enabled within the account.",
		status: cfatCloudTrailPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 3,
		remediationLink: "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html"
	}
	CfatChecks.push(cfatCloudTrailCheck);

	const cfatCloudTrailOrgServiceEnabledCheck:CfatCheck = {
		task: "CloudTrail Organization Service enabled",
		description: "CloudTrail should be enabled on the Organization.",
		status: cfatCloudTrailOrgServiceEnabledPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1,
		remediationLink:"https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-cloudtrail.html"
	}
	CfatChecks.push(cfatCloudTrailOrgServiceEnabledCheck);

	const cfatCloudTrailOrgTrailCheck:CfatCheck = {
		task: "CloudTrail Org Trail deployed",
		description: "At least one CloudTrail Organization Trail should be enabled.",
		status: cfatCloudTrailOrgTrailPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1,
		remediationLink:"https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html"
	}
	CfatChecks.push(cfatCloudTrailOrgTrailCheck);

	const cfatConfigManagementAccountCheck:CfatCheck = {
		task: "Config Recorder in Management Account configured",
		description: "Config Recorder in the Management Account should be enabled.",
		status: cfatConfigManagementAccountPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 2,
		remediationLink: "https://aws.amazon.com/blogs/mt/managing-aws-organizations-accounts-using-aws-config-and-aws-cloudformation-stacksets/"
	}
	CfatChecks.push(cfatConfigManagementAccountCheck);

	const cfatConfigRecorderManagementAccountCheck:CfatCheck= {
		task: "Config Delivery Channel in Management Account configured",
		description: "Config Delivery Channel in Management Account should be enabled.",
		status: cfatConfigRecorderManagementAccountPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 2,
		remediationLink: "https://aws.amazon.com/blogs/mt/managing-aws-organizations-accounts-using-aws-config-and-aws-cloudformation-stacksets/"
	}
	CfatChecks.push(cfatConfigRecorderManagementAccountCheck);

	const cfatCloudFormationEnableCheck:CfatCheck = {
		task: "CloudFormation StackSets activated",
		description: "CloudFormation StackSets should be activated in the CloudFormation console.",
		status: cfatOrgCloudFormationEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 5,
		loe: 1,
		remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-cloudformation.html#integrate-enable-ta-cloudformation"
	}
	CfatChecks.push(cfatCloudFormationEnableCheck);

	const cfatOrgServiceGuardDutyCheck:CfatCheck = {
		task: "GuardDuty Organization service enabled",
		description: "GuardDuty Organization services should be enabled.",
		status: cfatOrgServiceGuardDutyEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatOrgServiceGuardDutyCheck);

	const cfatOrgServiceRamCheck:CfatCheck = {
		task: "RAM Organization service enabled",
		description: "Resource Access Manager (RAM) trusted access should be enabled in the AWS Organization.",
		status: cfatOrgServiceRamEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatOrgServiceRamCheck);

	const cfatOrgServiceSecurityHubCheck:CfatCheck = {
		task: "Security Hub Organization service enabled",
		description: "Security Hub trusted access should be enabled in the AWS Organization.",
		status: cfatOrgServiceSecurityHubEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatOrgServiceSecurityHubCheck);

	const cfatOrgServiceIamAccessAnalyzerCheck:CfatCheck = {
		task: "IAM Access Analyzer Organization service enabled",
		description: "IAM Access Analyzer trusted access should be enabled in the AWS Organization.",
		status: cfatOrgServiceIamAccessAnalyzerEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatOrgServiceIamAccessAnalyzerCheck);

	const cfatOrgServiceConfigCheck:CfatCheck = {
		task: "Config Organization service enabled",
		description: "AWS Config trusted access should be enabled in the AWS Organization.",
		status: cfatOrgServiceAwsConfigEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 4,
		loe: 1
	}
	CfatChecks.push(cfatOrgServiceConfigCheck);

	const cfatOrgServiceCloudFormationCheck:CfatCheck = {
		task: "CloudFormation Organization service enabled",
		description: "CloudFormation trusted access should be enabled in the AWS Organization.",
		status: cfatBackupPoliciesEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 5,
		loe: 1,
		remediationLink: "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-activate-trusted-access.html"
	}
	CfatChecks.push(cfatOrgServiceCloudFormationCheck)

	const cfatInfraOuCheck:CfatCheck = {
		task: "Top-level Infrastructure OU deployed",
		description: "Top-level Infrastructure OU should exist.",
		status: infrastructureFound ? "complete": "incomplete",
		required: false,
		weight: 5,
		loe: 2,
		remediationLink: "https://catalog.workshops.aws/control-tower/en-US/introduction/manage-ou"
	}
	CfatChecks.push(cfatInfraOuCheck);

	const cfatSecurityOuCheck:CfatCheck = {
		task: "Top-level Security OU deployed",
		description: "Top-level Security OU should exist.",
		status: securityFound ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 2,
		remediationLink: "https://catalog.workshops.aws/control-tower/en-US/introduction/manage-ou"
	}
	CfatChecks.push(cfatSecurityOuCheck);

	const cfatWorkloadOuCheck:CfatCheck = {
		task: "Top-level Workloads OU deployed",
		description: "Top-level Workloads OU should exist.",
		status: workloadsFound ? "complete": "incomplete",
		required: false,
		weight: 5,
		loe: 2,
		remediationLink: "https://catalog.workshops.aws/control-tower/en-US/introduction/manage-ou"
	}
	CfatChecks.push(cfatWorkloadOuCheck);

	const cfatIamIdCOrgServiceCheck:CfatCheck = {
		task: "IAM IdC Organization service enabled",
		description: "IAM Identity Center trusted access should be enabled in the AWS Organization",
		status: cfatIamIdPOrgServicePass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1,
		remediationLink: "https://docs.aws.amazon.com/singlesignon/latest/userguide/get-set-up-for-idc.html"
	}
	CfatChecks.push(cfatIamIdCOrgServiceCheck);

	const cfatIamIdcConfiguredCheck:CfatCheck = {
		task: "IAM IdC configured",
		description: "IAM Identity Center should be configured.",
		status: cfatIamIdcConfiguredPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 3,
		remediationLink: "https://docs.aws.amazon.com/singlesignon/latest/userguide/tutorials.html"
	}
	CfatChecks.push(cfatIamIdcConfiguredCheck);

	const cfatOrgPolicyScpEnabled:CfatCheck = {
		task: "Service Control Policies Enabled",
		description: "Service Control Policy should be enabled within the AWS Organization.",
		status: cfatScpEnabledPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1,
		remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html"
	}
	CfatChecks.push(cfatOrgPolicyScpEnabled);

	const cfatOrgPolicyTagPolicyCheck:CfatCheck = {
		task: "Organization Tag Policy Enabled",
		description: "Tag Policy should be enabled within the AWS Organization.",
		status: cfatTagPoliciesEnabledPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 1,
		remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html"
	}
	CfatChecks.push(cfatOrgPolicyTagPolicyCheck);

	const cfatBackupPoliciesEnabledCheck:CfatCheck = {
		task: "Organization Backup Policy Enabled",
		description: "Backup Policy should be enabled within the AWS Organization.",
		status: cfatBackupPoliciesEnabledPass ? "complete": "incomplete",
		required: false,
		weight: 5,
		loe: 1,
		remediationLink: "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html"
	}
	CfatChecks.push(cfatBackupPoliciesEnabledCheck);

	const cfatControlTowerDeployedCheck:CfatCheck= {
		task: "Control Tower Deployed",
		description: "Control Tower should be deployed.",
		status: cfatControlTowerDeployedPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 6,
		remediationLink: "https://catalog.workshops.aws/control-tower/en-US/prerequisites/deploying"
	}
	CfatChecks.push(cfatControlTowerDeployedCheck);

	const cfatControlTowerLatestVersionCheck:CfatCheck = {
		task: "Control Tower Latest Version",
		description: "Control Tower should be the latest version.",
		status: cfatControlTowerLatestVersionPass ? "complete": "incomplete",
		required: false,
		weight: 5,
		loe: 2,
		remediationLink: "https://docs.aws.amazon.com/controltower/latest/userguide/update-controltower.html"
	}
	CfatChecks.push(cfatControlTowerLatestVersionCheck);

	const cfatControlTowerNotDriftedCheck:CfatCheck = {
		task: "Control Tower not drifted",
		description: "Control Tower should not be drifted.",
		status: cfatControlTowerNotDriftedPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 2,
		remediationLink:"https://docs.aws.amazon.com/controltower/latest/userguide/resolve-drift.html"
	}
	CfatChecks.push(cfatControlTowerNotDriftedCheck);

	const cfatLogArchiveAccountCheck:CfatCheck = {
		task: "Log Archive account deployed",
		description: "Log Archive Account should exist.",
		status: cfatLogArchiveAccountPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 2
	}
	CfatChecks.push(cfatLogArchiveAccountCheck);

	const cfatAuditAccountCheck:CfatCheck = {
		task: "Audit account deployed",
		description: "Audit account should exist.",
		status: cfatAuditAccountPass ? "complete": "incomplete",
		required: true,
		weight: 6,
		loe: 2
	}
	CfatChecks.push(cfatAuditAccountCheck);

	report.cfatChecks = CfatChecks

	console.table(CfatChecks, ["task", "status","required", "loe"]);
	const reportFile = "./cfat.txt"
	console.log(`compiling report...`)
	const assessment:string = await createReport(report)
	console.log(`saving report to ./cfat/cfat.txt...`)
	fs.appendFileSync(reportFile, assessment);
	console.log(`cloud foundation assessment complete. Access your report at ./cfat/cfat.txt`)
};
main();