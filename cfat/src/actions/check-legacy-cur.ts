import { CostAndUsageReportServiceClient, DescribeReportDefinitionsCommand } from "@aws-sdk/client-cost-and-usage-report-service";
import { LegacyCurInfo } from '../types';

const checkLegacyCur = async (region: string): Promise<LegacyCurInfo> => {
	// Set up AWS SDK client for Cost Explorer
	const curClient = new CostAndUsageReportServiceClient({ region });
	let isLegacyCurSetup = false;

	try {
		// Check if Cost Explorer is set up
		const input = {};
		const command = new DescribeReportDefinitionsCommand(input);
		const response = await curClient.send(command);
		if (response.ReportDefinitions && response.ReportDefinitions.length > 0) {
			isLegacyCurSetup = true;
		}

		return { isLegacyCurSetup };
	} catch (error) {
		// Check if the error is related to Cost Explorer setup
		console.error(`Error: ${error}`);
		isLegacyCurSetup = false;
		return { isLegacyCurSetup };
	} finally {
		// Close the AWS SDK client
		curClient.destroy();
	}
};

export default checkLegacyCur;
