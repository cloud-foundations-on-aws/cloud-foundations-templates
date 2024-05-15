
export async function deployConfigRecorderTask(taskNumber:number, waypoint:string,  region:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Deploy AWS Config Recorder to the ${region} region.`;
  return task
}

export async function deployConfigDeliveryChannelTask(taskNumber:number, waypoint:string,  region:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Add AWS Config Delivery Channel to the ${region} region.`;
  return task
}

export async function deployCloudTrailOrgTrailTask(taskNumber:number, waypoint:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Create a multi-region CloudTrail Organization Trail in your home AWS Region.`;
  return task
}

export async function deployControlTowerTask(taskNumber:number, waypoint:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Deploy AWS Control Tower in your home AWS Region.`;
  return task
}

export async function updateLzControlTowerTask(taskNumber:number, waypoint:string, currentVersion:string, latestVersion: string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Update your AWS Control Tower Landing Zone from ${currentVersion} to ${latestVersion}.`;
  return task
}

export async function fixLzDrift(taskNumber:number, waypoint:string): Promise<string>{
  const task:string = `${waypoint} - Task ${taskNumber} - Fix drift in deployed landing zone.`;
  return task
}

export async function deployOuTask(taskNumber:number, waypoint:string, OuName:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Deploy top-level OU ${OuName}.`;
  return task
}

export async function removeIamUserTask(taskNumber:number, waypoint:string, IamUserName:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Remove IAM user ${IamUserName}`;
  return task
}

export async function removeIamUserApiKeyTask(taskNumber:number, waypoint:string, IamUserName:string, IamUserApiKeyId:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Remove IAM user ${IamUserName} API key: ${IamUserApiKeyId}`;
  return task
}

export async function deleteVpc(taskNumber:number, waypoint:string,  region:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Delete VPC in the ${region} region.`;
  return task
}

export async function deleteEc2(taskNumber:number, waypoint:string,  region:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Delete VPC in the ${region} region.`;
  return task
}

export async function enableAwsOrganizationService(taskNumber:number, waypoint:string,  serviceName:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Enable the AWS service ${serviceName} within your AWS Organization`;
  return task
}

export async function delegateAdministrationAwsService(taskNumber:number, waypoint:string,  serviceName:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Delegate the AWS service ${serviceName} within your AWS Organization to a member account`;
  return task
}

export async function enableAwsCur(taskNumber:number, waypoint:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Enable and create a Cost and Utilization Report (CUR) in the billing console.`;
  return task
}

export async function reviewAccountEmailAddresses(taskNumber:number, waypoint:string): Promise<string> {
  const task:string = `${waypoint} - Task ${taskNumber} - Review and validate your email addresses and their domains for the root user administrator for management and all member accounts.`;
  return task
}

export async function enablePolicyTypeTask(taskNumber:number, waypoint:string, policyType:string): Promise<string>{
  const task:string = `${waypoint} - Task ${taskNumber} - Enable the policy type ${policyType} within your AWS Organization.`;
  return task
}