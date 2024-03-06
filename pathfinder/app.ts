import { defineAccountType }  from './src/actions/define-account-type.js';
import  checkIamUsers from './src/actions/check-iam-users.js';
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
import * as tasks from './src/actions/tasks.js';
import * as fs from 'fs';

const main = async (): Promise<void> => {
	const reportFile = "./Pathfinder.txt"
	let dateTime = new Date()
	const region =  process.env.AWS_REGION || 'us-east-1';
	const allRegions = await getAllRegions();
	console.log("Discovering your AWS environment....")
	const accountType = await defineAccountType(region);

	fs.writeFileSync(reportFile, "Cloud Foundations - Pathfinder")
	fs.appendFileSync(reportFile, `\nGenerated on: ${dateTime.toUTCString()} \n\n`);
	fs.appendFileSync(reportFile, `\n*********************************************************`);
	fs.appendFileSync(reportFile, `\n                   MANAGEMENT ACCOUNT`);
	fs.appendFileSync(reportFile, `\n*********************************************************`);

	fs.appendFileSync(reportFile, `\n\nAWS ACCOUNT TYPE\n`);
	if (accountType) {
		console.dir(accountType, {depth: null, colors: true})
		fs.appendFileSync(reportFile, `\n  Is in AWS Organization: ${accountType.isInOrganization}`);
		fs.appendFileSync(reportFile, `\n  Assessing AWS Management Account: ${accountType.isManagementAccount}`);
	}
	console.log("Discovering IAM Users....")
	const iamUserResult = await checkIamUsers();
	fs.appendFileSync(reportFile, `\n\nIAM USERS CHECK\n`);
	if (iamUserResult && iamUserResult.length > 0) {
		console.dir(iamUserResult, {depth: null, colors: true});
		for(const iamUser of iamUserResult){
			fs.appendFileSync(reportFile, `\n  IAM User: ${iamUser.userName}`);
			if(iamUser.accessKeyId){
				fs.appendFileSync(reportFile, `\n    User API Key ID: ${iamUser.accessKeyId}`);
			}
			fs.appendFileSync(reportFile, `\n`);
		}
	} else {
		fs.appendFileSync(reportFile, `\n  No IAM Users found.`);
	}
	console.log("Discovering EC2 instances across all AWS Regions....")
	const ec2Check = await checkEc2Exists(allRegions);
	fs.appendFileSync(reportFile, `\n\nEC2 INSTANCE CHECK\n`);
	if(ec2Check && ec2Check.find(param => param.ec2Found === true)){
		console.dir(ec2Check, {depth: null, colors: true});
		for ( const ec2 of ec2Check ){
			if(ec2.ec2Found){
				fs.appendFileSync(reportFile, `\n  ${ec2.region} - found EC2 Instance(s).`);
			}
		}
	}else {
		fs.appendFileSync(reportFile, `\n  No EC2 instances found.`);
	}
	console.log("Discovering VPCs across all AWS Regions....")
	const vpcCheck = await checkVpcExists(allRegions);
	fs.appendFileSync(reportFile, `\n\nVPC CHECK\n`);
	if(vpcCheck && vpcCheck.length >0){
		console.dir(vpcCheck, {depth: null, colors: true});
		for(const vpcFind of vpcCheck){
			if(vpcFind.vpcFound){
				fs.appendFileSync(reportFile, `\n  ${vpcFind.region} - found VPC(s).`);
			}
		}
	} else {
		fs.appendFileSync(reportFile, `\n  No VPCs found.`);
	}
	console.log("Discovering AWS Config configurations across all AWS Regions....")
	const cloudTrailCheck = await checkCloudTrailExists(allRegions);
	const configCheck = await checkConfigExists(allRegions);
	fs.appendFileSync(reportFile, `\n\nAWS CONFIG CHECK\n`);
	if(configCheck && configCheck.find(param => param.configRecorderFound === true)){
		console.dir(configCheck, {depth: null, colors: true});
		for (const configFind of configCheck){
			if(configFind.configRecorderFound){
				fs.appendFileSync(reportFile, `\n  ${configFind.region} - Config Recorder found`);
			}
			if(configFind.configDeliveryChannelFound){
				fs.appendFileSync(reportFile, `\n  ${configFind.region} - Config Delivery Channel found`);
			}
		}
	} else{
		fs.appendFileSync(reportFile, `\n  No AWS Config resource discovered`);
	}

	// all calls require an AWS Organization exist and the account be a management account
	if (accountType.isInOrganization && accountType.isManagementAccount) {
		const orgDetails = await getOrgDetails('us-east-1');
		console.dir(orgDetails, {depth: null, colors: true});
		const legacyCurCheck = await checkLegacyCur('us-east-1');
		const enableOrgPoliciesCheck = await getEnabledOrgPolicyTypes('us-east-1');
		console.dir(enableOrgPoliciesCheck, {depth: null, colors: true});
		const orgEnabledServices = await getEnabledOrgServices('us-east-1');
		console.dir(orgEnabledServices, {depth: null, colors: true});
		const cfnOrgStatus = await getOrgCloudFormation(region);
		console.dir(cfnOrgStatus, {depth: null, colors: true});
		const controlTowerDetails = await getControlTower(region);
		const idcInformation = await getIdcInfo(allRegions);
		console.dir(idcInformation, {depth: null, colors: true});
		const orgDelAdminDetails = await getOrgDaAccounts();
		console.dir(orgDelAdminDetails, {depth: null, colors: true});
		const orgMemberAccountDetails = await getOrgMemberAccounts();
		console.dir(orgMemberAccountDetails, {depth: null, colors: true});

		///// SET THE BACKLOG TASK FOR MANAGEMENT ACCOUNT ////
		fs.appendFileSync(reportFile, `\n\nMANAGEMENT ACCOUNT RECOMMENDED TASKS:`);
		let mgtTaskNumber:number = 1
		const managementAccountWaypoint:string = "Management Account"
		if (iamUserResult && iamUserResult.length > 0) {
			for(const iamUser of iamUserResult){
				const message:string = await tasks.removeIamUserTask(mgtTaskNumber, managementAccountWaypoint, iamUser.userName)
				fs.appendFileSync(reportFile, `\n  ${ message }`);
				mgtTaskNumber++
				if(iamUser.accessKeyId){
					const message:string = await tasks.removeIamUserApiKeyTask(mgtTaskNumber, managementAccountWaypoint, iamUser.userName, iamUser.accessKeyId)
					fs.appendFileSync(reportFile, `\n  ${ message }`);
					mgtTaskNumber++
				}
			}
		}
		if(ec2Check && ec2Check.find(param => param.ec2Found === true)){
			for ( const ec2 of ec2Check ){
				if(ec2.ec2Found && ec2.region){
					const message:string = await tasks.deleteEc2(mgtTaskNumber, managementAccountWaypoint, ec2.region );
					fs.appendFileSync(reportFile, `\n  ${ message }`);
					mgtTaskNumber++
				}
			}
		}
		if(vpcCheck && vpcCheck.length >0){
			for(const vpcFind of vpcCheck){
				if(vpcFind.vpcFound && vpcFind.region){
					const message:string = await tasks.deleteVpc(mgtTaskNumber, managementAccountWaypoint, vpcFind.region)
					fs.appendFileSync(reportFile, `\n  ${ message }`);
					mgtTaskNumber++
				}
			}
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                    GOVERNANCE`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION POLICY TYPES\n`);
		fs.appendFileSync(reportFile, `\n  Service Control Policies (SCP) enabled: ${enableOrgPoliciesCheck.scpEnabled}`);
		fs.appendFileSync(reportFile, `\n  Tag Policies enabled: ${enableOrgPoliciesCheck.tagPolicyEnabled}`);
		fs.appendFileSync(reportFile, `\n  Backup Policies enabled: ${enableOrgPoliciesCheck.backupPolicyEnabled}`);

		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION CLOUDFORMATION\n`);
		fs.appendFileSync(reportFile, `\n  AWS CloudFormation Organization stack sets status : ${cfnOrgStatus.status}`);

		fs.appendFileSync(reportFile, `\n\nCLOUDTRAIL CHECK\n`);
		if(cloudTrailCheck && cloudTrailCheck.length > 0) {
			console.dir(cloudTrailCheck, {depth: null, colors: true});
			for(const ctFind of cloudTrailCheck){
				if(ctFind.trailFound){
					fs.appendFileSync(reportFile, `\n  CloudTrail found in ${ctFind.region}`);
					fs.appendFileSync(reportFile, `\n    Is Organization Trail: ${ctFind.isOrgTrail}`);
					fs.appendFileSync(reportFile, `\n    Is MultiRegion: ${ctFind.isMultiRegion}`);
					fs.appendFileSync(reportFile, `\n`);
				}
			}
		}else {
			fs.appendFileSync(reportFile, `\n  No AWS CloudTrail resource discovered`);
		}

		fs.appendFileSync(reportFile, `\n\nGOVERNANCE SERVICES ENABLED IN AWS ORGANIZATION:\n`);
		if(orgEnabledServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  AWS CloudTrail`);
		}
		if(orgEnabledServices.find(param=> param.service === 'config.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  AWS Config`);
		}

		///// SET THE BACKLOG TASK FOR GOVERNANCE /////
		fs.appendFileSync(reportFile, `\n\nGOVERNANCE RECOMMENDED TASKS:`);
		const govWaypoint:string = "Governance"
		let govTaskNumber: number = 1
		if(!orgEnabledServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(govTaskNumber, govWaypoint, "AWS CloudTrail");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			govTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'config.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(govTaskNumber, govWaypoint, "AWS Config");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			govTaskNumber++
		}
		if(!enableOrgPoliciesCheck.scpEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(govTaskNumber, govWaypoint, "Service Control Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			govTaskNumber++
		}
		if(!enableOrgPoliciesCheck.tagPolicyEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(govTaskNumber, govWaypoint, "Tag Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			govTaskNumber++
		}
		if(!enableOrgPoliciesCheck.backupPolicyEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(govTaskNumber, govWaypoint, "Backup Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			govTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                FINANCIAL MANAGEMENT`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		fs.appendFileSync(reportFile, `\n\nLegacy CUR`);
		fs.appendFileSync(reportFile, `\n  Is legacy CUR setup: ${legacyCurCheck.isLegacyCurSetup}`);

		///// SET THE BACKLOG TASK FOR FINANCIAL MANAGEMENT /////
		fs.appendFileSync(reportFile, `\n\nCLOUD FINANCIAL MANAGEMENT RECOMMENDED TASKS:`);
		let finTaskNumber: number = 1
		const finWaypoint:string = "Cloud Financial Management"
		if(!legacyCurCheck.isLegacyCurSetup){
			const message:string = await tasks.enableAwsCur(finTaskNumber, finWaypoint);
			fs.appendFileSync(reportFile, `\n  ${message}`);
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                MULTI-ACCOUNT STRATEGY`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION DETAILS\n`);
		fs.appendFileSync(reportFile, `\n  AWS Organization Id: ${orgDetails.id}`);
		fs.appendFileSync(reportFile, `\n  AWS Organization ARN: ${orgDetails.arn}`);
		fs.appendFileSync(reportFile, `\n  AWS Organization Root OU Id: ${orgDetails.rootOuId}`);

		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION CLOUDFORMATION\n`);
		fs.appendFileSync(reportFile, `\n  AWS CloudFormation Organization stack sets status : ${cfnOrgStatus.status}`);
		let transitionalFound,suspendedFound,workloadsFound,securityFound: boolean = false;
		if(orgDetails.rootOuId){
			const orgOus = await getOrgTopLevelOus('us-east-1', orgDetails.rootOuId);
			console.dir(orgOus, {depth: null, colors: true});
			fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION TOP-LEVEL ORGANIZATION UNITS\n`);
			fs.appendFileSync(reportFile, `\n  List of Organization's top-level OUs and AWS accounts:`);
			if(orgOus && orgOus.length > 0){
				for (const ou of orgOus){
					if(ou.name?.toLowerCase() === 'suspended'){suspendedFound = true}
					if(ou.name?.toLowerCase() === 'transitional'){transitionalFound = true}
					if(ou.name?.toLowerCase() === 'workloads'){workloadsFound=true}
					if(ou.name?.toLowerCase() === 'security'){securityFound=true}
					fs.appendFileSync(reportFile, `\n    Organizational Unit: ${ou.name}`);
					fs.appendFileSync(reportFile, `\n      Organizational Unit Id: ${ou.id}`);
					if(ou.accounts && ou.accounts.length > 0){
						fs.appendFileSync(reportFile, `\n      AWS Accounts:`);
						for (const account of ou.accounts){
							fs.appendFileSync(reportFile, `\n        ${account.Name}`);
						}
						fs.appendFileSync(reportFile, `\n`);
					}
					else{
						fs.appendFileSync(reportFile, `\n      AWS Accounts: None`);
						fs.appendFileSync(reportFile, `\n`);
					}
				}

			} else {
				fs.appendFileSync(reportFile, `\n  No top level OUs found.`);
			}
		}
		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION MEMBER ACCOUNTS\n`);

		if(orgMemberAccountDetails && orgMemberAccountDetails.length > 0){
			for (const memberAccount of orgMemberAccountDetails){
				fs.appendFileSync(reportFile, `\n  Account: ${memberAccount.accountName}`);
				fs.appendFileSync(reportFile, `\n  Account Email: ${memberAccount.accountEmail}\n`);
			}
		} else {
			fs.appendFileSync(reportFile, `No member accounts found which is amazing as this is running from one.`);
		}

		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION ENABLED SERVICES\n`);
		fs.appendFileSync(reportFile, `\n  The following AWS Services are enabled within your AWS Organization:`);
		for (const orgService of orgEnabledServices){
			fs.appendFileSync(reportFile, `\n    ${orgService.service}`);
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

		fs.appendFileSync(reportFile, `\n\nAWS ORGANIZATION INTEGRATED SERVICE REGISTERED DELEGATED ADMINS\n`);
		if(orgDelAdminDetails && orgDelAdminDetails.length > 0){
			for (const account of orgDelAdminDetails){
				fs.appendFileSync(reportFile, `\n  Account: ${account.accountName}`);

				if(account.services && account.services.length > 0 ){
					fs.appendFileSync(reportFile, `\n  Delegated Services:`);
					for (const srv of account.services){
						fs.appendFileSync(reportFile, `\n    ${srv.ServicePrincipal}`);
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
				fs.appendFileSync(reportFile, `\n `);
			}
		} else {
			fs.appendFileSync(reportFile, `\n  No delegated admin accounts in AWS Organization`);
		}

		///// SET THE BACKLOG TASK FOR MULTI-ACCOUNT STRATEGY /////
		fs.appendFileSync(reportFile, `\n\nMULTI-ACCOUNT STRATEGY RECOMMENDED TASKS:`);
		let masTaskNumber: number = 1;
		let masWaypoint:string = 'Multi-Account Strategy';
		const message:string = await tasks.reviewAccountEmailAddresses(masTaskNumber, masWaypoint);
			fs.appendFileSync(reportFile, `\n  ${message}`);
			masTaskNumber++
		if(!enableOrgPoliciesCheck.scpEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(masTaskNumber, masWaypoint, "Service Control Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			masTaskNumber++
		}
		if(!transitionalFound){
			const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Transitional");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			masTaskNumber++
		}
		if(!suspendedFound){
			const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Suspended");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			masTaskNumber++
		}
		if(!workloadsFound){
			const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Workloads");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			masTaskNumber++
		}
		if(!securityFound){
			const message:string = await tasks.deployOuTask(masTaskNumber, masWaypoint, "Security");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			masTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                  LANDING ZONE`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		fs.appendFileSync(reportFile, `\n\nAWS CONTROL TOWER\n`);
		if(controlTowerDetails.controlTowerRegion){
			console.dir(controlTowerDetails, {depth: null, colors: true});
			fs.appendFileSync(reportFile, `\n  Control Tower home region: ${controlTowerDetails.controlTowerRegion}`);
			fs.appendFileSync(reportFile, `\n  Control Tower status: ${controlTowerDetails.status}`);
			fs.appendFileSync(reportFile, `\n  Control Tower Landing Zone version: ${controlTowerDetails.deployedVersion}`);
			fs.appendFileSync(reportFile, `\n  Latest available version: ${controlTowerDetails.latestAvailableVersion}`);
			fs.appendFileSync(reportFile, `\n  Drift Status: ${controlTowerDetails.driftStatus}`);
		}else {
			fs.appendFileSync(reportFile, `\n  AWS Control Tower is not deployed in the AWS Organization`);
		}

		///// SET THE BACKLOG TASK FOR LANDING ZONE /////
		fs.appendFileSync(reportFile, `\n\nLANDING ZONE RECOMMENDED TASKS:`);
		let lzTaskNumber: number = 1
		const lzWaypoint:string = "Landing Zone"
		if(controlTowerDetails.controlTowerRegion === undefined){
			const message:string = await tasks.deployControlTowerTask(lzTaskNumber, lzWaypoint);
			fs.appendFileSync(reportFile, `\n  ${message}`);
			lzTaskNumber++
		}
		if(controlTowerDetails.driftStatus === 'DRIFTED'){
			const message:string = await tasks.fixLzDrift(lzTaskNumber, lzWaypoint);
			fs.appendFileSync(reportFile, `\n  ${message}`);
			lzTaskNumber++
		}
		if(controlTowerDetails.deployedVersion !== controlTowerDetails.latestAvailableVersion){
			const currentVersion:string = controlTowerDetails.deployedVersion ?? ""
			const latestVersion:string = controlTowerDetails.latestAvailableVersion ?? ""
			const message:string = await tasks.updateLzControlTowerTask(lzTaskNumber, lzWaypoint, currentVersion, latestVersion);
			fs.appendFileSync(reportFile, `\n  ${message}`);
			lzTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'member.org.stacksets.cloudformation.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(lzTaskNumber, lzWaypoint, "AWS CloudFormation");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			lzTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                    IDENTITY`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		fs.appendFileSync(reportFile, `\n\nAWS IAM IDENTITY CENTER\n`);
		fs.appendFileSync(reportFile, `\n  IdC Region: ${idcInformation.region}`);
		fs.appendFileSync(reportFile, `\n  IdC ARN: ${idcInformation.arn}`);
		fs.appendFileSync(reportFile, `\n  IdC Instance Id: ${idcInformation.id}`);

		///// SET THE BACKLOG TASK FOR IDENTITY /////
		fs.appendFileSync(reportFile, `\n\nIDENTITY RECOMMENDED TASKS:`);
		let ssoTaskNumber: number = 1
		const ssoWaypoint:string = 'Identity'
		if(!orgEnabledServices.find(param=> param.service === 'sso.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(ssoTaskNumber, ssoWaypoint, "AWS IAM Identity Center");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			ssoTaskNumber++
		}
		if(!identityDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(ssoTaskNumber, ssoWaypoint, "AWS IAM Identity Center");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			ssoTaskNumber++
		}
		if(!enableOrgPoliciesCheck.scpEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(ssoTaskNumber, ssoWaypoint, "Service Control Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			ssoTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                    SECURITY`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n\nAWS SECURITY SERVICES ENABLED IN AWS ORGANIZATION:\n`);
		if(orgEnabledServices.find(param=> param.service === 'guardduty.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  AWS GuardDuty`);
		}
		if(orgEnabledServices.find(param=> param.service === 'securityhub.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  AWS Security Hub`);
		}
		if(orgEnabledServices.find(param=> param.service === 'access-analyzer.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  IAM Access Analyzer`);
		}
		if(orgEnabledServices.find(param=> param.service === 'macie.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  Macie`);
		}
		if(orgEnabledServices.find(param=> param.service === 'storage-lens.s3.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  Amazon S3 Storage Lens`);
		}
		if(orgEnabledServices.find(param=> param.service === 'inspector2.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  Amazon Inspector`);
		}
		if(orgEnabledServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  AWS CloudTrail`);
		}
		if(orgEnabledServices.find(param=> param.service === 'config.amazonaws.com')){
			fs.appendFileSync(reportFile, `\n  AWS Config`);
		}

		///// SET THE BACKLOG TASK FOR SECURITY /////
		fs.appendFileSync(reportFile, `\n\nSECURITY RECOMMENDED TASKS:`);
		let secTaskNumber: number = 1
		const secWaypoint:string = "Security"
		if(!enableOrgPoliciesCheck.scpEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(secTaskNumber, secWaypoint, "Service Control Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'guardduty.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS GuardDuty");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'securityhub.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS SecurityHub");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'access-analyzer.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS IAM Access Analyzer");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'cloudtrail.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS CloudTrail");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'config.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(secTaskNumber, secWaypoint, "AWS Config");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!securityHubDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "Security Hub");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!guardDutyDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "GuardDuty");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!configDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "AWS Config");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!iamAccessAnalyzerDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "AWS IAM Access Analyzer");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}
		if(!s3StorageLensDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(secTaskNumber, secWaypoint, "S3 Storage Lens");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			secTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                    NETWORK`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		///// SET THE BACKLOG TASK FOR NETWORK /////
		fs.appendFileSync(reportFile, `\n\nNETWORK RECOMMENDED TASKS:`);
		let netTaskNumber: number = 1
		const networkWaypoint:string = 'Network'

		if(!orgEnabledServices.find(param=> param.service === 'guardduty.amazonaws.com')){
			const netGuardDutyEnableMessage:string = await tasks.enableAwsOrganizationService(netTaskNumber, networkWaypoint, "AWS GuardDuty");
			fs.appendFileSync(reportFile, `\n  ${netGuardDutyEnableMessage}`);
			netTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'ipam.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(netTaskNumber, networkWaypoint, "AWS IPAM");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			netTaskNumber++
		}
		if(!orgEnabledServices.find(param=> param.service === 'ram.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(netTaskNumber, networkWaypoint, "AWS Resource Access Manager");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			netTaskNumber++
		}
		if(!ipamDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(netTaskNumber, networkWaypoint, "AWS IPAM");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			netTaskNumber++
		}
		if(!enableOrgPoliciesCheck.scpEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(netTaskNumber, networkWaypoint, "Service Control Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			netTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n                  OBSERVABILITY`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		///// SET THE BACKLOG TASK FOR OBSERVABILITY /////
		fs.appendFileSync(reportFile, `\n\nOBSERVABILITY RECOMMENDED TASKS:`);
		let obTaskNumber: number = 1
		const obWaypoint:string = 'Observability'

		if(!orgEnabledServices.find(param=> param.service === 'account.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(obTaskNumber, obWaypoint, "Account Manager");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			obTaskNumber++
		}
		if(!accountDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(obTaskNumber, obWaypoint, "Account Manager");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			obTaskNumber++
		}

		fs.appendFileSync(reportFile, `\n\n*********************************************************`);
		fs.appendFileSync(reportFile, `\n               BACKUP AND RECOVERY`);
		fs.appendFileSync(reportFile, `\n*********************************************************`);

		///// SET THE BACKLOG TASK FOR BACKUP AND RECOVERY /////
		fs.appendFileSync(reportFile, `\n\nBACKUP AND RECOVERY RECOMMENDED TASKS:`);
		let backTaskNumber: number = 1
		const backupWaypoint:string = 'Backup and Recovery'
		// check if AWS Backup is enabled
		if(!orgEnabledServices.find(param=> param.service === 'backup.amazonaws.com')){
			const message:string = await tasks.enableAwsOrganizationService(backTaskNumber, backupWaypoint, "AWS Backup");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			backTaskNumber++
		}
		if(!backupDelegated){
			const message:string = await tasks.delegateAdministrationAwsService(backTaskNumber, backupWaypoint, "AWS Backup");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			backTaskNumber++
		}
		if(!enableOrgPoliciesCheck.backupPolicyEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(backTaskNumber, backupWaypoint, "Backup Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			backTaskNumber++
		}
		if(!enableOrgPoliciesCheck.scpEnabled) {
			const message:string = await tasks.enablePolicyTypeTask(backTaskNumber, backupWaypoint, "Service Control Policy");
			fs.appendFileSync(reportFile, `\n  ${message}`);
			backTaskNumber++
		}

	} else if (accountType.isInOrganization && !accountType.isManagementAccount) {
		const message:string = '\nWARNING: You are running Pathfinder from an account that is a member of your AWS Organization. Please run the solution from your AWS Management account.'
		console.warn(message);
		fs.appendFileSync(reportFile, message);
	} else {
		const message:string = '\nWARNING: You are running Pathfinder from an account that not part of an AWS Organization. This account will be treated as a standalone account.'
		console.warn(message);
		fs.appendFileSync(reportFile, message);
	}

	fs.appendFileSync(reportFile, `\n\n\n  END REVIEW`);
};

main();
