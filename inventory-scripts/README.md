## Project Overview

The tools presented below have evolved organically over time. They are presented in an order that aims to provide a logical flow, but were not necessarily created all at once or maintained to the same level of perfection.

>**Note:** some of the files still operate based on profiles, but the overall approach is transitioning towards a Federated model. The current implementation does not yet incorporate MFA token functionality.


## Common Parameters

> ***Note***: *The `verbose` and `debugging` options consistent across all the scripts to best effort.*

| Param | Description |
| --- | --- |
| -v | For those times when I decided to show less information on screen, to keep the output neat - you could use this level of logging to get what an interested user might want to see. |
| -vv | You could use this level of logging to get what a developer might want to see. |
| -vvv | This is generally the lowest level I would recommend anyone use. I started changing most scripts over from "-d" for INFO, to "-vvv" to align with standard practices. This is generally the lowest level I would recommend anyone use. |
| -d | I've updated the DEBUG to be the -d. Beware - this is a crazy amount of debugging, and it includes a lot of the open-source libraries that I use, since I don't disable that functionality within my scripts. |
| -h | Provide "-h" or "--help" on the command line and get a nicely formatted screen that describes all possible parameters. |
| -p | To specify the profile which the script will work with. In most cases, this could/ should be a Master Profile, but doesn't always have to be. Additionally - in many scripts, this parameter takes more than one possible profile AND ALSO allows you to specify a fragment of a profile, so it you have 3 profiles all with the same fragment, it will include all 3. |
| -r | To specify the single region for the script to work in. Most scripts take "all" as a valid parameter. Most scripts also assume "us-east-1" as a default if nothing is specified. |
| -rs | In many of the scripts, you can specify a fragment - so you can specify "us-east" and get both "us-east-1" and "us-east-2". Specify "us-" and you'll get all four "us-" regions. |
| -f | String fragment - some scripts (specifically ones dealing with CFN stacks and stacksets) take a parameter that allows you to specify a fragment of the stack name, so you can find that stack you can't quite remember the whole name of. |

## Less used common parameters

| Param | Description |
| --- | --- |
| --exact | It's possible that some fragments will exist both as a stackname, as well as part of other stacknames (think "xxx" and "xxx-global"). In these cases, you can use the "--exact" parameter, and it will only use the string you've entered. *Note that this means you must enter the entire string, and not just a fragment anymore.* |
| --skipprofile | Sometimes you want to specify a fragment of a profile, and you want 5 of the 6 profiles that fragment shows up in, but not the 6th. You can use this parameter to exclude that 6th profile (space delimited). |
| --skipaccount | Sometimes you want to exclude the production accounts from any script you're running. You can use this parameter to exclude a list of accounts (space delimited). |
| --filename | This parameter (hasn't been added to all the scripts yet) is my attempt to produce output suitable for use in an Excel sheet, or other analysis tooling. Eventually I'll come up with the Analysis tooling myself, but until then - the least I could do is output this data in a suitable format. You'll have to run the help (-h) to find out for each script if it supports this parameter / output yet or not. |
| +delete | I've tried to make it difficult to **accidentally** delete any resources, so that's why it's a "+" instead of a "-". |

## Purpose Built Scripts

Libraries, used by other scripts.

### [ALZ_CheckAccount.py](./ALZ_CheckAccount.py)

This script takes an Organization Management Account profile, and checks additional accounts to see if they meet the pre-reqs to be "adopted" by either Landing Zone or Control Tower.

If there are blockers to the adoption (like the default VPCs being present, or Config Recorder already being enabled), it can rectify those blockers it finds. However - to avoid mistakes - it only does this if you specifically select that in the submitted parameters.

While this script was focused on ALZ, it also *sort of* supports an account being adopted by Control Tower too.

### [check_all_cloudtrail.py](./check_all_cloudtrail.py)

This script is used to find whether CloudTrail is enabled on every account and region and whether it's enabled at the Org level, or within the Account itself. It also will show a listing of those accounts and regions which DO NOT have CloudTrail enabled - this is important!!

### [CT_CheckAccount.py](./CT_CheckAccount.py)

This script takes an Organization Management Account profile, and checks additional accounts to see if they meet the prereqs to be "adopted" by Control Tower.

If there are blockers to the adoption (like the Config Recorder already being enabled), it can rectify those blockers it finds. However - to avoid mistakes - it only does this if you specifically select that in the submitted parameters. This script is still being worked on.

### [DrawOrg.py](./DrawOrg.py)

This script can take a single profile and create a graphviz representation of the Org, with OUs (and the number of accounts under them), and the accounts shown as well.

Use `--policy` to see the policies (default is to not show) and `--managed` to see even the Managed Policies (which really make the diagram tougher to read).

This script may require multi-threading to make the most sense, because for every account and OU, we need to do 4 additional calls to find the policies associated with that account.

### [enable_drift_detection_stacksets.py](./enable_drift_detection.py)

This script's job is to go through all the stacksets you've asked it to (it takes stackset name fragments as parameters), and determine when the last time the stackset was drift-detected.

If you don't want to be bothered to respond to a prompt, it can run the drift-detection for you.

### [find_my_LZ_versions.py](./find_my_LZ_versions.py)

This script will take either a single profile, or the keyword "all" and determine whether your profile is the Management Account of a Landing Zone - or in the case of "all", go through all of your profiles and find those accounts which are Landing Zones roots, and tell you the version of the ALZ in that account.

### [find_orphaned_stacks.py](./find_orphaned_stacks.py)

This script was created as a "belt and suspenders" to double-check if the "move_stack_instances" script fails in the middle.

The scenario would be that the "move" script had already disassociated stack-instances from the old stack-set, but hadn't yet begun to create the new stack-set. Therefore, the stack-instances were only available within the child accounts, and not visible from the Management Account. This "helper" script can be used to find any instances where the child stack is present in the child account, but NOT present in the management's stackset.

This script is only non-intrusive, and doesn't make any changes.

### [lock_down_stack_sets_role.py](./lock_down_stack_sets_role.py)

I wrote this script to either lock or unlock the policy within child accounts after someone ran their ALZ tooling and locked things out.

### [move_stack_instances.py](./move_stack_instances.py)

In my work on migrating customer's from ALZ to ControlTower, I've found that many just need to move from ALZ-managed stacksets, to Control-Tower managed stacksets. I've written this script to be able to do that. Be careful tho - I've recently found that the CfCT pipeline REMOVES stack-instances that are not under Control Tower management, so this script should only be used in production with the full understanding and consent of a knowledgeable engineer who knows what they're doing.

To use this script, you'll want to supply the old stackset name and the new stackset name (which doesn't have to exist). This script takes the stack instances (optionally of only a specified account, so you can POC this script) and moves the underlying instances from one stackset to another.

It was brought to my attention that it's possible the child stack instances *could* have been changed since they were initially deployed, which means that the use of the same *template* within a CfCT pipeline could alter resources within a child account. My answer was to tell them to run a Drift-detection at the stackset level before running this code. They asked me to write it into this tool - so I did. Use "--drift-check" to enable that feature.

Since this script runs on the local machine, it's possible that something happens on the local machine that disturbs the script and causes it to fail or stop. In case that happens, there is a recovery file created during the run (without you doing anything) which can be referenced when the script is run again, and the script will pick up from where it left off when it stopped.

### [put_s3_public_block.py](./put_s3_public_block.py)

I wrote this script because we all need a way to ensure that we're following Best Security practices, without **too** much actual work. Therefore - this script will take either a profile of an Organization (typical -p format), or just run it with no parameters, and it will find all your Orgs, and all the accounts within your orgs, and lock down all the S3 buckets in all your accounts for you. It runs in "Dry-Run" mode by default, but when you run it with "+n", it will actually make the changes to your S3 config, without prompting for each change, so watch out that you aren't running this in a Production Org where you NEED an S3 bucket to be open (rare).

Additionally, I've added a parameter to accept a file of account numbers, as long as they're all reachable by the profile specified with the "-p" parameter.

### [RunOnMultiAccounts.py](./RunOnMultiAccounts.py)

So using the base of some of the other scripts, I realized that there were sometimes commands I just needed to run on multiple accounts - regardless of any meta-script stuff (think creating or deleting users). This script enabled me to simply change out the commands I'm running, for another set of commands - with the same framework around the script.

Maybe eventually - I'll generalize this script to where it takes another parameter of commands as input, but for now - you can simply go in an replace the command payloads, and this script will just run that on lots of accounts.

### [SC_Products_to_CFN_Stacks.py](./SC_Products_to_CFN_Stacks.py)

This script is focused on reconciling the SC Products with the CFN Stacks they create. It definitely can happen that a CFN stack can exist without a corresponding SC Product, and it can happen that an SC Product can exist without a corresponding CFN stack (I'm looking at you AWS Control Tower!). However, when an SC Product is in ERROR state and the CFN stack is in an error state - you're best served by terminating the SC Product and starting over. This script can help you find those instances and even offers to get rid of them for you.

### [update_retention_on_all_my_cw_groups.py](./update_retention_on_all_my_cw_groups.py)

This script checks all of your log groups and updates the retention of the logs.

### [UpdateRoleToMemberAccounts.py](./UpdateRoleToMemberAccounts.py)

Convert an ALZ account over to the CT model, before you have the necessary "AWSControlTowerExecutionRole" created within the member/ child account.

## Generic Scripts

General scripts for inventory and management

### [all_my_cfnstacks.py](./all_my_cfnstacks.py)

The objective of this script is to find that CloudFormation stack you know you created in some account within your Organization - but you just can't remember which one (and God forbid - in which region!). So here you can specify a stack fragment, and a region fragment and the script will search through all accounts within your Org (assuming you provided a profile of the Management Account-with appropriate rights) in only those regions that match your fragment, and find the stacks that match the fragment you provided.

>**Note:** If you provide the `+delete` parameter - it will **DELETE** those stacks WITHOUT ADDITIONAL CONFIRMATION! So please be careful about using this.

GuardDuty stacks sometimes need more care and feeding, so there's a special section in this script to handle those. It's a bit hard-coded (we expect that 'GuardDuty' was specified in its entirety in the fragment), but we'll fix that eventually.

### [all_my_cfnstacksets.py](./all_my_cfnstacksets.py)

The objective of this script is to find those CloudFormation StackSets you know you created in some account within your Organization.

### [all_my_config_recorders_and_delivery_channels.py](./all_my_config_recorders_and_delivery_channels.py)

List the config recorders and delivery channels in an account across regions.

### [all_my_directories.py](./all_my_directories.py)

There are a few tools you may try out which require you to create a directory in your account/ region. When you delete those tools (WorkSpaces), you sometimes forget to delete the directories you had to create as well. This tool will find and report on them for you.

### [all_my_ebs_volumes.py](./all_my_ebs_volumes.py)

Find all the EBS volumes in various accounts within your org.

### [all_my_elbs.py](./all_my_elbs.py)

Find all the various Load Balancers created in various accounts within your org.

### [all_my_enis.py](./all_my_enis.py)

This is a script to find devices across all of my Orgs when all I have is the public (or private) IP address. Having so many different accounts - regions and Orgs makes finding something a real pain in the butt.

### [all_my_functions.py](./all_my_functions.py)

The objective of this script was to find all the various Lambda functions you've created and left in various accounts.

If you specify the `+fix` parameter, and the new runtime, it will find the functions you specify, and then update the runtime for those functions (across your org and regions you specify) to the new runtime. If the Lambda functions aren't valid, the update will fail, but it will still succeed on those functions which work.

### [all_my_gd-detectors.py](./all_my_gd_detectors.py)

This script was created to help remove all the various GuardDuty pieces that are created when GuardDuty is enabled in an organization and its children. Trying to remove all the pieces by hand is crazy, so this script is really long and complex - but it does the job well.

### [all_my_instances.py](./all_my_instances.py)

Find all the EC2 instances available within your accounts and regions. The script can accept 1 or more profiles. If you specify a profile representing a Management Account - the script will assume you mean the entire organization, instead of just that one account - and will try to find all instances for all accounts within that Org.

### [all_my_orgs.py](./all_my_orgs.py)

Script will go through all of your profiles and find all the Management Accounts you may have access to - and list out all the accounts under all of the Management Accounts it can find.

If you provide a profile using the `-p` parameter, it will determine if that profile is a Master and only list out the accounts within that Org.

If you provide a profile (using the `-p` parameter) which is not a Management Account, it will admonish you and go through all of your profiles, assuming you _meant_ to provide a Root Profile.

If you provide one or more profiles using the `-l` parameter, it will limit its investigation to just those profiles and give you whatever information it can about those. If you provide a "Child" account, it won't give much information - since it's not available. But this way you can provide a list of Root Profiles (assuming you have proper access to all of them) and it will give the necessary info about each.

There are two additional parameters which are useful:
  - `-R` for listing only the root profiles it can find
  - `-s` for listing only the short form of the output

### [all_my_phzs.py](./all_my_phzs.py)

Find all of the Private Hosted Zones using cross-account functionality.

### [all_my_policies.py](./all_my_policies.py)

Find all the RDS instances within a profile, or an Org.

### [all_my_rds_instances.py](./all_my_rds_instances.py)

Find all the RDS instances within a profile, or an Org.

### [all_my_roles.py](./all_my_roles.py)

This script identifies all roles across the examined accounts, addressing the common use case of locating the specific account where a particular role has been created. While the current version lacks a search-by-fragment feature, users can leverage additional tools for filtering. The script's objective is to consolidate role inventories, enabling better management and governance of the cloud environment. Future updates may incorporate the ability to search by role name fragment, based on user feedback to enhance the script's capabilities.

### [all_my_saml_providers.py](./all_my_saml_providers.py)

This script aims to locate all Identity Providers (IDPs) across the user's organizational accounts. While the script also includes the capability to delete these IDPs, it is generally not a common requirement, as most users prefer to maintain visibility and control over their configured IDPs.

The primary purpose of this tool is to provide a comprehensive inventory of the IDPs within the user's environment. This information can be valuable for understanding the identity and access management landscape, ensuring compliance, and managing the overall security posture of the cloud infrastructure.

### [all_my_saml_providers.py](./all_my_saml_providers.py)

This script is designed to locate all SAML providers within the user's organization. While the script also includes the capability to delete these SAML providers, this functionality should be used with caution, as it can significantly impact access to the affected accounts, potentially making it challenging to regain access.

The primary purpose of this tool is to provide a comprehensive inventory of the SAML providers configured across the organization. This information can be valuable for understanding the identity and access management landscape, ensuring compliance, and managing the overall security posture of the cloud infrastructure.

By offering the ability to identify all configured SAML providers, this script empowers users to have a centralized view of their identity-related resources. The deletion functionality is included as a safeguard, but its usage should be carefully considered, as it can have significant consequences on the organization's access and authentication mechanisms.

### [all_my_subnets.py](./all_my_subnets.py)

This script is designed to provide users with the ability to locate all subnets across their organization, as well as identify a specific subnet that matches a provided IP address. This functionality facilitates the efficient identification of the account and region where a particular IP address is being utilized.

The primary objectives of this script are to:

1. Retrieve a comprehensive list of all subnets across the user's organization.
2. Identify a specific subnet that matches a provided IP address, enabling the user to quickly locate the corresponding account and region.

The read-only nature of the script ensures that users can safely explore and analyze their subnet configurations without the risk of inadvertent deletions or modifications. Additionally, the script's use of multi-threading has proven to be an effective optimization, resulting in improved processing times and enhanced user experience.

### [all_my_topics.py](./all_my_topics.py)

Find all SNS Topics.

### [all_my_vpcs.py](./all_my_vpcs.py)

This script retrieves a comprehensive list of VPCs across an organization's accounts, as determined by the management account's child accounts. Users can optionally filter the results to only include default VPCs. The script is read-only and does not support VPC deletion, ensuring a safe exploration of the VPC landscape.

The primary objectives are to provide users with a complete VPC inventory and the ability to focus on default VPCs if needed. User feedback is encouraged to further enhance the script's capabilities and alignment with evolving organizational requirements.

Specify `--default` to limit your searching to only default VPCs.

### [delete_bucket_objects.py](./delete_bucket_objects.py)

This is a tool that should delete buckets and the objects in them. I didn't write the original script, but I've been adapting it to my needs. This one should be considered alpha.

### [mod_my_cfnstacksets.py](./mod_my_cfnstacksets.py)

This script was originally conceived as part of a comprehensive library, with separate scripts dedicated to finding and deleting resources. However, upon further development, it became clear that the "finding" functionality should be integrated into the "deletion" script for a more streamlined and efficient approach.

The current iteration of the script focuses on traversing the CloudFormation StackSets in the management account and identifying those that match a provided fragment. This functionality is particularly useful when an account has been closed, but its association with existing StackSets has not been removed. The script can now reliably remove such accounts from the relevant StackSets.

Additionally, the script has been enhanced to handle StackSets that are tied to a specific Organizational Unit (OU) and utilize the `SERVICE_MANAGED` permission model. Furthermore, the script now includes the ability to re-run StackSets, enabling the remediation of any identified drift in the associated child stacks.

The goal is to consolidate all the useful features into a single, comprehensive script, ensuring a more coherent and maintainable solution. The development of this script is an ongoing process, and user feedback is welcomed to further refine and enhance its capabilities in alignment with evolving organizational requirements.

### [my_org_users.py](./my_org_users.py)

This script scans the child accounts within an organization to retrieve a comprehensive list of IAM users. The primary purpose is to verify that the existing IAM users align with the expected configuration, ensuring appropriate access controls and governance over the cloud infrastructure.

### [my_ssm_parameters.py](./my_ssm_parameters.py)

This script serves dual purposes: providing a comprehensive list of existing AWS Systems Manager (SSM) Parameters, and addressing an issue with the AWS Landing Zone tool, which can leave behind unused Parameters, potentially leading to the 10,000 entry limit. The script can identify and, with user confirmation, delete these orphaned Parameters to maintain a clean and optimized Parameter Store.

The `--ALZ` and `-b` parameters enable the identification and remediation of leftover Parameters, while the `+delete` parameter allows programmatic deletion to resolve this acknowledged issue.


### [update_retention_on_all_my_cw_groups.py](./update_retention_on_all_my_cw_groups.py)

The script generates a report outlining the potential savings, empowering users to make informed decisions about their log retention strategies.

## Utility Files

### [Inventory_Modules.py](./Inventory_Modules.py)

Utils referenced throughout the directory.

### [test_tools.sh](./test_tools.sh)

This is a great little bash script I wrote that will just test out the scripts that are most useful, and give timings on them.

### [vpc_modules.py](./vpc_modules.py)

This is another "utils" collection, generally specific to the "ALZ_CheckAccount" script as well as the all_my_vpcs.py script, because all of the VPC deletion functions are in this library file.

## Class Files

### [account_class.py](./account_class.py)

This class script enables the entire AWS account to be considered as its own object. This handles finding what kind of account it is (Root, Child, Standalone), the Child Accounts attached to it (if it's a Root account) among other attributes.

### [ArgumentsClass.py](./ArgumentsClass.py)

This class holds the argparse class I use to standardize te parameters across as many scripts as possible.

To use these scripts for Discovery for your environment, please see the "Discovery.md" file included in this repo.
