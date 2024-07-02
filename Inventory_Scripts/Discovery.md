Using these Inventory Scripts as Discovery
================

Lately, I've been asked to come up with a way of combining many of these scripts together to come up with a way to perform a reasonable Discovery on an Org - and find issues that need to be remediated, as well as assess the level of maturity of a Landing Zone. What follows here is the list of scripts (with expected parameters) and what I'd expect you'll find given the output.

--------
The following script runs for all accounts within either your specified profile, or (if no profile is used) your default credentials (could be environment variables). This will assess whether ALL of your accounts are suitable to be migrated to Control Tower or not, and if not - what the issues preventing their adoption would be. The "-r global" specifies that ALL regions (even those you have not opted into) should be looked at. The script will (because of the "-v") inform you of the failure to connect to an account in the excluded region, but won't fail because of it. This script executes 10 commands for every account in every region, so it will take a **long** time to run. I have NOT enabled the output to be saved to an output file yet, but that's next on my list. For now - you'll have to pipe the output to a file and import that to Excel.    
```commandline
CT_CheckAccount.py -v -r global --timing [-p <profile of Org Account>]
```

This script will go through your Org and find all Child Accounts and their statuses - thereby showing you which accounts should - perhaps - be moved to a "SUSPENDED" OU or otherwise treated specially. It's useful because the output is very purposeful and it's pretty fast. 
```commandline
all_my_orgs.py -v
```

This next script will find the status of all of your accounts and regions and whether you have CloudTrail enabled in each. I'm working on enhancing the script to also summarize whether there are multiple CloudTrails for a given account / region, so you can be notified to TURN THAT OFF - and save a bunch of money. You only get 1 CloudTrail per account / region for free, and the second one costs more than you think.
```commandline
check_all_cloudtrail.py -v -r global --timing --filename cloudtrail_check.out [-p <profile of Org Account>]
```

The following script can draw out the Organization. The output will be a file in the current directory called “aws_organization.png” - please either get that file, or a screenshot of it. Assuming the user has the graphviz tool installed within their environment, running this tool should end with the diagram itself being shown. The parameter "--policy" can also be mitigated by "--aws" to include those policies which AWS owns (like the AWSFullAccess policy assigned by default to every OU and account). The default (below) excludes that AWS-managed policy for diagram clarity's sake. 
```commandline
DrawOrg.py --policy --timing
```

The following script can do soooo much _(Yeah - I'm pretty proud of this one)_. As it's shown here, it doesn't yet support the "--filename" parameter, since I haven't decided how to write out the data. The goal of using this output in Discovery, is to find those accounts which have been closed (and may no longer be in the Org at all), but are still represented in the stacksets of the Org - and therefore may (eventually) cause stacksets to slow down or fail. Best to find these issues ahead of time, rather than after the fact. For instance - I found a customer with 450 accounts in their Org, but their largest stackset had over 100 closed (and already dropped out) accounts, so while the stackset was still considered "CURRENT", more than 20% of the time spent on that stackset was spent attempting to connect to previously closed accounts.
```commandline
mod_my_cfnstacksets.py -v -r <home region> --timing [-p <profile of Org Account>] -check
```

The following script shows whether the "Public S3 block" has been enabled on all accounts within the Org. While Control Tower has a control that can enable this on new accounts, it doesn't mean that it hasn't been removed somewhere. It's a good idea to run this, and you can use the same script to re-enable the block if it's been removed.
```commandline
put_s3_public_block.py -v
```

The following script finds any and all config recorders and delivery channels in your environment - again, this is a tool that is used when trying to determine what blockers exist before moving to Control Tower. It's also a good tool (if you don't need the full complement of checks in the CT_CheckAccount.py above) to find any accounts where Config isn't running at all. This tool also can be used to **delete** the config recorders and delivery channels - if needed. 
```commandline
all_my_config_recorders_and_delivery_channels.py -v -r global --timing
```

These scripts will find those IAM/ IDC users, local directories, or SAML providers in your child accounts which can be exposures to unwanted access, without you realizing it. It's always a good idea to look for these - since these can represent a significant threat vector to protect from.
```commandline
my_org_users.py -v
all_my_saml_providers.py -v
all_my_directories.py -v
```

While it's normal for this script to find nothing, it's very illuminating if it *does* find something... 
```commandline
find_orphaned_stacks.py --filename Drift_Detection -v 
```

The following scripts will just show very useful Inventory information that will help the Discovery process flesh out its understanding of the customer's environment.
```commandline
all_my_vpcs.py -v
all_my_phzs.py -v
```

Whenever we do Discovery, we always want to find possible money-savings areas for the customer as well. The script below will find any Log Groups and their retention settings. This gives the customer the opportunity (perhaps) to update those retention settings (from their default of "NEVER") to something that will purge data after a specific time. The bottom of the script gives an *idea* of how much you're spending on Log Groups anyway, so you have an idea if taking action is worthwhile. 
```commandline
update_retention_on_all_my_cw_groups.py
```

ALZ used Service Catalog to create and manage accounts. It's important that these Service Catalog products are properly terminated when ALZ  is decommissioned, so this tool will report on the accounts in the Org reconciled with the Service Catalog Products that were created and point out if there are products for already closed accounts, or whether there are more than one product for a given account (or no products for a given account). This is - again - useful in cleaning up what sometimes happens over time with any tool - organic mess...   
```commandline
SC_Products_to_CFN_Stacks.py -v --timing
```
