Project Overview
================
Inventory_Scripts is a git repository to aggregate a number of scripts I've written, with the intent to make it easier to keep track of what's created and/ or running in any one of your (possibly) many AWS accounts... The scripts in this repo are discussed below.

***Note***: *I'm trying to figure out the right way to support all types of customers with the same basic syntax for these scripts. Some scripts make sense to only run in one account. Some make sense to run across multiple accounts (possibly the whole Org) and some make sense to run across a subset of accounts within the org. Trying to come up with consistent parameter syntax for these different use-cases has been difficult. Any suggestions are appreciated.*  

***Note***:  *The tools I've written here have grown organically. They're presented below in an order I thought made sense, but they were definitely not created all at once, nor all kept up to the same level of perfection. I started this journey back in 2017 when there was no such thing as the Landing Zone, and Federation wasn't as prevalent a thing, so I assumed everyone would have profiles for every account they managed. Fast-forward to 2019 and we realize that most admin is done by authenticating to one account and using cross-account roles to authorize to other Child accounts. Hence - some of these files still work by profile, but I'm slowly moving everything over to being able to work with a Federated model. I still haven't baked in MFA token stuff, but I think I might just rely on the OS for that in the short term.*

***Note***: *I've tried to make the "verbose" and "debugging" options consistent across all the scripts. Apologies if they're not.*

***Note***: *I've also made this repo available at https://github.com/paulbayer/Inventory_Scripts for customers.*

Common Parameters
------------------
  - -v for some additional logging (level: ERROR)
    - For those times when I decided to show less information on screen, to keep the output neat - you could use this level of logging to get what an interested user might want to see.
  - -vv for even more logging (level: WARNING)
    - You could use this level of logging to get what a developer might want to see.
  - -vvv for even more logging (level: INFO)
    - This is generally the lowest level I would recommend anyone use.
    - I started changing most scripts over from "-d" for INFO, to "-vvv" to align with standard practices 
    - This is generally the lowest level I would recommend anyone use.
  - -d for lots of logging (level: DEBUG)
    - I've updated the DEBUG to be the -d. Beware - this is a crazy amount of debugging, and it includes a lot of the open-source libraries that I use, since I don't disable that functionality within my scripts.
  - -h: Provide "-h" or "--help" on the command line and get a nicely formatted screen that describes all possible parameters.
  - -p: to specify the profile which the script will work with. In most cases, this could/ should be a Master Profile, but doesn't always have to be. Additionally - in many scripts, this parameter takes more than one possible profile AND ALSO allows you to specify a fragment of a profile, so it you have 3 profiles all with the same fragment, it will include all 3.
  - -r: to specify the single region for the script to work in. Most scripts take "all" as a valid parameter. Most scripts also assume "us-east-1" as a default if nothing is specified. 
  - -rs: In many of the scripts, you can specify a fragment - so you can specify "us-east" and get both "us-east-1" and "us-east-2". Specify "us-" and you'll get all four "us-" regions.
  - -f: string fragment - some scripts (specifically ones dealing with CFN stacks and stacksets) take a parameter that allows you to specify a fragment of the stack name, so you can find that stack you can't quite remember the whole name of.

Less used common parameters:
------------------
  - --exact: It's possible that some fragments will exist both as a stackname, as well as part of other stacknames (think "xxx" and "xxx-global"). In these cases, you can use the "--exact" parameter, and it will only use the string you've entered. *Note that this means you must enter the entire string, and not just a fragment anymore.*
  - --skipprofile: Sometimes you want to specify a fragment of a profile, and you want 5 of the 6 profiles that fragment shows up in, but not the 6th. You can use this parameter to exclude that 6th profile (space delimited).
  - --skipaccount: Sometimes you want to exclude the production accounts from any script you're running. You can use this parameter to exclude a list of accounts (space delimited).
  - --filename: This parameter (hasn't been added to all the scripts yet) is my attempt to produce output suitable for use in an Excel sheet, or other analysis tooling. Eventually I'll come up with the Analysis tooling myself, but until then - the least I could do is output this data in a suitable format. You'll have to run the help (-h) to find out for each script if it supports this parameter / output yet or not.
  - +delete: I've tried to make it difficult to **accidentally** delete any resources, so that's why it's a "+" instead of a "-".

Purpose Built Scripts
------------------
- **ALZ_CheckAccount.py**
  - This script takes an Organization Master Account profile, and checks additional accounts to see if they meet the pre-reqs to be "adopted" by either Landing Zone or Control Tower.
  - If there are blockers to the adoption (like the default VPCs being present, or Config Recorder already being enabled), it can rectify those blockers it finds. However - to avoid mistakes - it only does this if you specifically select that in the submitted parameters.
  - While this script was focused on ALZ, it also *sort of* supports an account being adopted by Control Tower too.

- **check_all_cloudtrail.py**
  - This script is used to find whether CloudTrail is enabled on every account and region and whether it's enabled at the Org level, or within the Account itself. It also will show a listing of those accounts and regions which DO NOT have CloudTrail enabled - this is important!!

- **CT_CheckAccount.py**
  - This script takes an Organization Master Account profile, and checks additional accounts to see if they meet the pre-reqs to be "adopted" by Control Tower.
  - If there are blockers to the adoption (like the Config Recorder already being enabled), it can rectify those blockers it finds. However - to avoid mistakes - it only does this if you specifically select that in the submitted parameters. This script is still being worked on.
 
- **DrawOrg.py**
  - This script can take a single profile and create a graphviz representation of the Org, with OUs (and the number of accounts under them), and the accounts shown as well. Eventually, I'll make showing the accounts optional, but for now - it does both.
  - I added visualizing the policies (both managed or unmanaged) as a parameter too. Use "--policy" to see the policies (default is to not show) and "--managed" to see even the Managed Policies (which really make the diagram tougher to read).
  - This script will require multi-threading to make the most sense, because for every account and OU, we need to do 4 additional calls to find the policies associated with that account. These could definitely be mult-threaded.

- **enable_drift_detection_stacksets.py**
  - This script's job is to go through all the stacksets you've asked it to (it takes stackset name fragments as parameters), and determine when the last time the stackset was drift-detected.
  - If you don't want to be bothered to respond to a prompt, it can run the drift-detection for you. 

- **find_my_LZ_versions.py**
  - I wrote this script because I've noticed that many customers find it difficult to find their own ALZ versions, and some customers have multiple Landing Zones (like me), so it makes it even harder to keep track. This script will take either a single profile, or the keyword "all" and determine whether your profile is the Management Account of a Landing Zone - or in the case of "all", go through all of your profiles and find those accounts which are Landing Zones roots, and tell you the version of the ALZ in that account.  

- **find_orphaned_stacks.py**
  - This script was created as a "belt and suspenders" to double-check if the "move_stack_instances" script fails in the middle. 
  - The scenario would be that the "move" script had already disassociated stack-instances from the old stack-set, but hadn't yet begun to create the new stack-set. Therefore, the stack-instances were only available within the child accounts, and not visible from the Management Account. This "helper" script can be used to find any instances where the child stack is present in the child account, but NOT present in the management's stackset.
  - As usual, this script is only non-intrusive, and doesn't make any changes.

- **lock_down_stack_sets_role.py**
  - I wrote this script to either lock or unlock the policy within child accounts after someone ran their ALZ tooling and locked things out.

- **move_stack_instances.py**
  - In my work on migrating customer's from ALZ to ControlTower, I've found that many just need to move from ALZ-managed stacksets, to Control-Tower managed stacksets. I've written this script to be able to do that. Be careful tho - I've recently found that the CfCT pipeline REMOVES stack-instances that are not under Control Tower management, so this script should only be used in production with the full understanding and consent of a knowledgeable engineer who knows what they're doing.
  - To use this script, you'll want to supply the old stackset name and the new stackset name (which doesn't have to exist). This script takes the stack instances (optionally of only a specified account, so you can POC this script) and moves the underlying instances from one stackset to another.
  - It was brought to my attention that it's possible the child stack instances *could* have been changed since they were initially deployed, which means that the use of the same *template* within a CfCT pipeline could alter resources within a child account. My answer was to tell them to run a Drift-detection at the stackset level before running this code. They asked me to write it into this tool - so I did. Use "--drift-check" to enable that feature.
  - Since this script runs on the local machine, it's possible that something happens on the local machine that disturbs the script and causes it to fail or stop. In case that happens, there is a recovery file created during the run (without you doing anything) which can be referenced when the script is run again, and the script will pick up from where it left off when it stopped.

- **put_s3_public_block.py**
  - I wrote this script because we all need a way to ensure that we're following Best Security practices, without **too** much actual work. Therefore - this script will take either a profile of an Organization (typical -p format), or just run it with no parameters, and it will find all your Orgs, and all the accounts within your orgs, and lock down all the S3 buckets in all your accounts for you. It runs in "Dry-Run" mode by default, but when you run it with "+n", it will actually make the changes to your S3 config, without prompting for each change, so watch out that you aren't running this in a Production Org where you NEED an S3 bucket to be open (rare).
  - Additionally, I've added a parameter to accept a file of account numbers, as long as they're all reachable by the profile specified with the "-p" parameter.

- **RunOnMultiAccounts.py**
  - So using the base of some of the other scripts, I realized that there were sometimes commands I just needed to run on multiple accounts - regardless of any meta-script stuff (think creating or deleting users). This script enabled me to simply change out the commands I'm running, for another set of commands - with the same framework around the script. 
  - Maybe eventually - I'll generalize this script to where it takes another parameter of commands as input, but for now - you can simply go in an replace the command payloads, and this script will just run that on lots of accounts. 

- **SC_Products_to_CFN_Stacks.py**
  - This script is focused on reconciling the SC Products with the CFN Stacks they create. It definitely can happen that a CFN stack can exist without a corresponding SC Product, and it can happen that an SC Product can exist without a corresponding CFN stack (I'm looking at you AWS Control Tower!). However, when an SC Product is in ERROR state and the CFN stack is in an error state - you're best served by terminating the SC Product and starting over. This script can help you find those instances and even offers to get rid of them for you.

- **update_retention_on_all_my_cw_groups.py**
  - Originally, I thought that the expense of retaining logs within CloudWatch was hugely significant, and therefore this script could potentially save customers LOTS of money. It turns out that the cost of saving data within CloudWatch is fairly low, so this isn't a dramatic money saver, but it's still a cool script.
  - This script checks all of your log groups 

- **UpdateRoleToMemberAccounts.py**
  - I wrote this script realizing that there's no easy way to "convert" an ALZ account over to the CT model, before you have the necessary "AWSControlTowerExecutionRole" created within the member/ child account. This script does that for you - when given the proper parameters. Perhaps I'll add a default method to the script when I can.
  - I updated this script to also allow "removal" of a rolename (assuming it's been setup with this script). This way, the script can be used and also "backed out" - since it doesn't offer much of a confirmation on changes.

Generic Scripts
------------------
- **all_my_cfnstacks.py**
  - The objective of this script is to find that CloudFormation stack you know you created in some account within your Organization - but you just can't remember which one (and God forbid - in which region!). So here you can specify a stack fragment, and a region fragment and the script will search through all accounts within your Org (assuming you provided a profile of the Master Account-with appropriate rights) in only those regions that match your fragment, and find the stacks that match the fragment you provided.
  - If you provide the "+delete" parameter - it will DELETE those stacks WITHOUT ADDITIONAL CONFIRMATION! So please be careful about using this.
  - GuardDuty stacks sometimes need more care and feeding, so there's a special section in this script to handle those. It's a bit hard-coded (we expect that 'GuardDuty' was specified in its entirety in the fragment), but we'll fix that eventually.
- **all_my_cfnstacksets.py**
  - The objective of this script is to find those CloudFormation StackSets you know you created in some account within your Organization - but you just can't remember which one.
- **all_my_config_recorders_and_delivery_channels.py**
  - I wrote this script to help remove the Config Recorders and Delivery Channels for a given account, so that we could use this within the "adoption" of legacy accounts into the AWS Landing Zone.
  - Now that we have the ALZ_CheckAccount tool, I don't see a lot of use from this script, but it's complete - so why delete it?
- **all_my_directories.py**
  - There are a few tools you may try out which require you to create a directory in your account/ region. When you delete those tools (WorkSpaces), you sometimes forget to delete the directories you had to create as well. This tool will find and report on them for you.
- **all_my_ebs_volumes.py**
  - The objective of this script was to find all the EBS volumes in various accounts within your org.
  - At the end, I tried to give a summary of any volumes that are unattached, so you can take proper action on those (which could be costing you money).
- **all_my_elbs.py**
  - The objective of this script was to find all the various Load Balancers created in various accounts within your org.

- **all_my_enis.py**
  - This is a script to find devices across all of my Orgs when all I have is the public (or private) IP address. Having so many different accounts - regions and Orgs makes finding something a real pain in the butt.

- **all_my_functions.py**
  - The objective of this script was to find all the various Lambda functions you've created and left in various accounts.
  - I just added the ability to provide a new runtime at the command line, so if you specify the "+fix" parameter, and the new runtime, it will find the functions you specify, and then update the runtime for those functions (across your org and regions you specify) to the new runtime. If the Lambda functions aren't valid, the update will fail, but it will still succeed on those functions which work.

- **all_my_gd-detectors.py**
  - This script was created to help remove all the various GuardDuty pieces that are created when GuardDuty is enabled in an organization and its children. Trying to remove all the pieces by hand is crazy, so this script is really long and complex - but it does the job well.

- **all_my_instances.py**
  - The objective of this script is to find all the EC2 instances available within your accounts and regions. The script can accept 1 or more profiles. If you specify a profile representing a Master Account - the script will assume you mean the entire organization, instead of just that one account - and will try to find all instances for all accounts within that Org.

- **all_my_orgs.py**
  - I use this script almost every day. In its default form with no parameters provided - it will go through all of your profiles and find all the Master Accounts you may have access to - and list out all the accounts under all of the Master Accounts it can find.
  - If you provide a profile using the "-p" parameter, it will determine if that profile is a Master and only list out the accounts within that Org.
  - If you provide a profile (using the "-p" parameter) which is not a Master Account, it will admonish you and go through all of your profiles, assuming you _meant_ to provide a Root Profile.
  - If you provide one or more profiles using the "-l" parameter, it will limit its investigation to just those profiles and give you whatever information it can about those. If you provide a "Child" account, it won't give much information - since it's not available. But this way you can provide a list of Root Profiles (assuming you have proper access to all of them) and it will give you the necessary info about each.
  - There are two additional parameters which are useful:
    - "-R" for listing only the root profiles it can find
    - "-s" for listing only the short form of the output

- **all_my_phzs.py**
  - The objective of this script is to find all of the Private Hosted Zones in a cross-account fashion.

- **all_my_policies.py**
  - The objective of this script is to find all the RDS instances within a profile, or an Org.

- **all_my_rds_instances.py**
  - The objective of this script is to find all the RDS instances within a profile, or an Org.

- **all_my_roles.py**
  - The objective of this script is to find all the roles within the accounts it looks through.
  - There are most common use cases for this script:
    - "In which account did I put that role?" (you'd have to use 'grep', since I didn't update this to take a string fragment - yet)
  - **all_my_saml_providers.py**
    - The objective of this script is to find all Identity Providers within your accounts within your org.
    - There is also the capability to delete these idps - but I don't see people doing that all that often.

- **all_my_saml_providers.py**
  - The objective of this script is to find the saml providers within the Org. 
  - It's possible with this script to delete those providers you find, making it easier to remove a SAML provider across all of your Org, all at once. Obviously this should not be used lightly, as gaining access BACK to those accounts may be very difficult. 

- **all_my_subnets.py**
  - The objective of this script is to allow the user to find all their subnets across their org, but ALSO to find a specific subnet that matches a provided IP address, to make it easier to find that account and region where that one IP is being used.
  - This is a READ-ONLY script, since there's likely no scenario where you want to delete subnets from your environment.
  - I have experimented with multi-threading in this script, and it seems to make a world of difference. As always - all comments are welcome!
- **all_my_topics.py**
  - Again - sometimes I create an SQS topic and I completely forget where I put it. This script will help you find it.
- **all_my_vpcs.py**
  - The objective of this script is to find all the vpcs within your set of accounts - as determined by your Master Account's list of children.
  - You can also specify "--default" to limit your searching to only default VPCs.
  - This does not currently allow any deletion of your (default) VPCs...

- **delete_bucket_objects.py**
  - This is a tool that should delete buckets and the objects in them. I didn't write the original script, but I've been adapting it to my needs. This one should be considered alpha.

- **mod_my_cfnstacksets.py**
  - So, originally, when I was creating this library, I had the idea that I would create scripts that found resources - and different scripts that deleted those resources. Hence - both the "all_my_cfnstacksets" as well as "del_my_cfnstacksets". However, I quickly realized that you had to do the finding before you could do the deleting - so I decided to put more effort into the "del\*" tool instead of the "find\*" tool. Of course - then I realized that having the "deletion" be action in the find script made way more sense, so I tried to put everything I had done from one script into the other. At the end of it all - I had a mish-mash of useful and stale features in both scripts.
  - The truth is that I need to go through this script and make sure everything useful here has gotten into the "all_my_cfnstacksets.py" script and simply move forward with that one only. Still a work in progress, I guess.
  - This script goes through the stacksets in the Management Account and looks for stacksets that match the fragment you supplied.
  - The usefulness of this script is that it can remove specific accounts from all the stacksets it finds, so that if you know you've closed an account, but forgotten to remove it from existing stacksets, this script will remove that account from the stacksets found.
  - Most recent update - this script can now affect stacksets that are tied to a specific OU and use the "SERVICE_MANAGED" permission model. 
  - Another update - this script can now re-run stacksets, thereby remediating drift if any is found in the child stacks.

- **my_org_users.py**
  - The objective of this script is to go through all of your child accounts within an Org and pull out any IAM users you have - to ensure it's only what you expect.

- **my_ssm_parameters.py**
  - The objective of this script was two fold -
    - One is to just list out your SSM Parameters, so you know how many and which ones you have.
    - The other is to resolve a problem that exists with the AWS Landing Zone tool - which creates Parameter Store entries and doesn't clean them up when needed. Since the Parameter Store has a limit of 10,000 entries - some sophisticated, long-time customers could hit this limit and be frustrated by the inability to easily remediate this acknowledged bug.
  - This script can solve that problem by using the "--ALZ" parameter and the "-b" parameter to identify any left-over parameters that should be cleaned up since so many days back (ideally further back than your last successful Pipeline run).
  - As usual - provide the "+delete" parameter to allow the script to programmatically remediate the problem.

- **update_retention_on_all_my_cw_groups.py**
  - Ok - so I thought that perhaps the default behavior of CW to make all log groups set to "Never Delete" was wrong, and how much money could I save if I changed all my groups to be 90 days instead? I was really excited, except then I found out (after I wrote the thing) that you weren't really saving all that much.
  - Just in case people want to use this to save money - it runs and shows you how much you could save, if you want to update the retention periods across your environment.

Utility Files
----------------
- **Inventory_Modules.py**
  - This is the "utils" file that is referenced by nearly every other script I've written. I didn't know Python well enough when I started to know that I should have named this "utils". If I get ambitious, maybe I'll go through and rename it within every script.

- **test_tools.sh**
  - This is a great little bash script I wrote that will just test out the scripts that are most useful, and give timings on them. I'm planning to use this bash script to help me prioritize which python scripts to enable for multi-threading first.

- **vpc_modules.py**
  - This is another "utils" collection, generally specific to the "ALZ_CheckAccount" script as well as the all_my_vpcs(2).py script, because all of the VPC deletion functions are in this library file. Props to

Class Files
----------------
- **account_class.py**
  - This class script enables the entire AWS account to be considered as its own object. This handles finding what kind of account it is (Root, Child, Standalone), the Child Accounts attached to it (if it's a Root account) among other attributes.

- **ArgumentsClass.py**
  - This class holds the argparse class I use to standardize te parameters across as many scripts as possible.


To use these scripts for Discovery for your environment, please see the "Discovery.md" file included in this repo.
