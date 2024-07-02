#!/usr/bin/env python3

import sys
import Inventory_Modules
import boto3
from Inventory_Modules import get_all_credentials
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
from colorama import init, Fore
from botocore.exceptions import ClientError
import logging

init()
__version__ = "2023.07.18"

parser = CommonArguments()
parser.singleprofile()
parser.multiregion_nodefault()
parser.extendedargs()
parser.deletion()
parser.rootOnly()
parser.rolestouse()
parser.timing()
parser.verbosity()
parser.version(__version__)
parser.my_parser.add_argument(
    "+delete", "+forreal", "+fix",
    dest="flagDelete",
    action="store_true",
    help="Whether to delete the detectors it finds.")
args = parser.my_parser.parse_args()

pProfile = args.Profile
pRegions = args.Regions
pSkipAccounts = args.SkipAccounts
pSkipProfiles = args.SkipProfiles
pAccounts = args.Accounts
pRootOnly = args.RootOnly
pRolesToUse = args.AccessRoles
verbose = args.loglevel
DeletionRun = args.flagDelete
# ForceDelete = args.ForceDelete
ForceDelete = args.Force
pTiming = args.Time
# Setup logging levels
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

##########################
ERASE_LINE = '\x1b[2K'

aws_acct = aws_acct_access(pProfile)

NumObjectsFound = 0
session_gd = aws_acct.session
# This check ensures that we're checking only those regions where GuardDuty is enabled.
if pRegions is None:
    pRegions = ['all']
gd_regions = Inventory_Modules.get_regions3(aws_acct, pRegions)
all_gd_detectors = []
all_gd_invites = []
GD_Admin_Accounts = []

AllCredentials = get_all_credentials(pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, gd_regions, pRolesToUse)
RegionList = list(set([x['Region'] for x in AllCredentials]))
AccountList = list(set([x['AccountId'] for x in AllCredentials]))
print(f"Searching {len(AccountList)} accounts and {len(RegionList)} regions")

sts_session = aws_acct.session
sts_client = sts_session.client('sts')
places_to_try = len(AllCredentials)
for credential in AllCredentials:
    logging.info(f"Checking Account: {credential['AccountId']}")
    # try:
    #     account_credentials = Inventory_Modules.get_child_access3(aws_acct, account['AccountId'])
    # except ClientError as my_Error:
    #     if "AuthFailure" in str(my_Error):
    #         print(f"Authorization Failure for account {account['AccountId']}")
    #     sys.exit("Credentials failure")
    # for region in gd_regions:
    logging.info(f"Checking Region: {credential['Region']}")
    places_to_try -= 1
    try:
        session_aws = boto3.Session(
            aws_access_key_id=credential['AccessKeyId'],
            aws_secret_access_key=credential['SecretAccessKey'],
            aws_session_token=credential['SessionToken'],
            region_name=credential['Region'])
        client_aws = session_aws.client('guardduty')
        logging.debug(f"Token Info: {credential} in region {credential['Region']}")
        # List Invitations
        logging.info(f"Finding any invites for account: {credential['AccountId']} in region {credential['Region']}")
        response = client_aws.list_invitations()
        logging.debug(f"Finished listing invites for account: {credential['AccountId']} in region {credential['Region']}")
    except ClientError as my_Error:
        if "AuthFailure" in str(my_Error):
            print(f"{credential['AccountId']}: Authorization Failure for account {credential['AccountId']}")
            continue
        if str(my_Error).find("security token included in the request is invalid") > 0:
            logging.error(f"Account #:{credential['AccountId']} - The region you're trying '{credential['Region']}' isn't enabled for your account")
            continue
    except Exception as my_Error:
        print(my_Error)
        continue
    try:
        if 'Invitations' in response.keys():
            for i in range(len(response['Invitations'])):
                all_gd_invites.append({
                    'AccountId': response['Invitations'][i]['AccountId'],
                    'InvitationId': response['Invitations'][i]['InvitationId'],
                    'Region': credential['Region'],
                    'AccessKeyId': credential['AccessKeyId'],
                    'SecretAccessKey': credential['SecretAccessKey'],
                    'SessionToken': credential['SessionToken']
                })
                logging.error(f"Found invite ID {response['Invitations'][i]['InvitationId']} in account {response['Invitations'][i]['AccountId']} in region {credential['Region']}")
    except NameError:
        pass
    try:
        print(
            f"{ERASE_LINE}Trying account {credential['AccountId']} in region {credential['Region']} -- {places_to_try} left of {len(AllCredentials)}",
            end='\r')
        response = client_aws.list_detectors()
        if len(response['DetectorIds']) > 0:
            NumObjectsFound = NumObjectsFound + len(response['DetectorIds'])
            admin_acct_response = client_aws.list_members(
                DetectorId=str(response['DetectorIds'][0]),
                OnlyAssociated='False',
            )
            logging.warning(
                f"Found another detector {str(response['DetectorIds'][0])} in account {credential['AccountId']} in region {credential['Region']} bringing the total found to {str(NumObjectsFound)}")
            if len(admin_acct_response['Members']) > 0:
                all_gd_detectors.append({
                    'AccountId': credential['AccountId'],
                    'Region': credential['Region'],
                    'DetectorIds': response['DetectorIds'],
                    'AccessKeyId': credential['AccessKeyId'],
                    'SecretAccessKey': credential['SecretAccessKey'],
                    'SessionToken': credential['SessionToken'],
                    'GD_Admin_Accounts': admin_acct_response['Members']
                })
                logging.error(f"Found account {credential['AccountId']} in region {credential['Region']} to be a GuardDuty Admin account."
                              f"It has {len(admin_acct_response['Members'])} member accounts connected to detector {response['DetectorIds'][0]}")
            else:
                all_gd_detectors.append({
                    'AccountId': credential['AccountId'],
                    'Region': credential['Region'],
                    'DetectorIds': response['DetectorIds'],
                    'AccessKeyId': credential['AccessKeyId'],
                    'SecretAccessKey': credential['SecretAccessKey'],
                    'SessionToken': credential['SessionToken'],
                    'GD_Admin_Accounts': "Not an Admin Account"
                })
        else:
            print(ERASE_LINE,
                  f"{Fore.RED}No luck in account: {credential['AccountId']} in region {credential['Region']}{Fore.RESET} -- {places_to_try} of {len(AllCredentials)}",
                  end='\r')
    except ClientError as my_Error:
        if "AuthFailure" in str(my_Error):
            print(f"Authorization Failure for account {credential['AccountId']}")

display_dict = {'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'},
                'MgmtAccount'  : {'DisplayOrder': 2, 'Heading': 'Mgmt Acct'},
                'AccountId'    : {'DisplayOrder': 3, 'Heading': 'Acct Number'},
                'Region'       : {'DisplayOrder': 4, 'Heading': 'Region', 'Condition': ['us-east-2']},
                'DetectorIds'    : {'DisplayOrder': 5, 'Heading': 'DetectorId', 'Condition': ['Never']},
                'DG_Admin_Accpunts'         : {'DisplayOrder': 7, 'Heading': 'CW Log Name'},
                'Size'         : {'DisplayOrder': 6, 'Heading': 'Size (Bytes)'}}

if args.loglevel < 50:
    print()
    fmt = '%-20s %-15s %-35s %-25s'
    print(fmt % ("Account ID", "Region", "Detector ID", "# of Member Accounts"))
    print(fmt % ("----------", "------", "-----------", "--------------------"))
    for i in range(len(all_gd_detectors)):
        try:
            if 'AccountId' in all_gd_detectors[i]['GD_Admin_Accounts'][0].keys():
                print(
                    fmt % (
                        all_gd_detectors[i]['AccountId'], all_gd_detectors[i]['Region'],
                        all_gd_detectors[i]['DetectorIds'], f"{len(all_gd_detectors[i]['GD_Admin_Accounts'])} Member Accounts"))
        except AttributeError:
            print(
                fmt % (
                    all_gd_detectors[i]['AccountId'], all_gd_detectors[i]['Region'],
                    all_gd_detectors[i]['DetectorIds'], "Not an Admin Account"))

print(ERASE_LINE)
print(f"We scanned {len(AccountList)} accounts and {len(RegionList)} regions totalling {len(AllCredentials)} possible areas for resources.")
print(f"Found {len(all_gd_invites)} Invites and {NumObjectsFound} Detectors")
print()

if DeletionRun and not ForceDelete:
    ReallyDelete = (input("Deletion of Guard Duty detectors has been requested. Are you still sure? (y/n): ") == 'y')
else:
    ReallyDelete = False

if DeletionRun and (ReallyDelete or ForceDelete):
    MemberList = []
    logging.warning("Deleting all invites")
    for y in range(len(all_gd_invites)):
        session_gd_child = boto3.Session(
            aws_access_key_id=all_gd_invites[y]['AccessKeyId'],
            aws_secret_access_key=all_gd_invites[y]['SecretAccessKey'],
            aws_session_token=all_gd_invites[y]['SessionToken'],
            region_name=all_gd_invites[y]['Region'])
        client_gd_child = session_gd_child.client('guardduty')
        # Delete Invitations
        try:
            print(ERASE_LINE, f"Deleting invite for Account {all_gd_invites[y]['AccountId']}", end="\r")
            Output = client_gd_child.delete_invitations(
                AccountIds=[all_gd_invites[y]['AccountId']]
            )
        except Exception as e:
            if e.response['Error']['Code'] == 'BadRequestException':
                logging.warning("Caught exception 'BadRequestException', handling the exception...")
                pass
            else:
                print("Caught unexpected error regarding deleting invites")
                print(e)
                sys.exit(9)
    print(f"Removed {len(all_gd_invites)} GuardDuty Invites")
    num_of_gd_detectors = len(all_gd_detectors)
    for y in range(len(all_gd_detectors)):
        logging.info(
            f"Deleting detector-id: {all_gd_detectors[y]['DetectorIds']} from account {all_gd_detectors[y]['AccountId']} in region {all_gd_detectors[y]['Region']}")
        print(
            f"Deleting detector in account {all_gd_detectors[y]['AccountId']} in region {all_gd_detectors[y]['Region']} {num_of_gd_detectors}/{len(all_gd_detectors)}")
        session_gd_child = boto3.Session(
            aws_access_key_id=all_gd_detectors[y]['AccessKeyId'],
            aws_secret_access_key=all_gd_detectors[y]['SecretAccessKey'],
            aws_session_token=all_gd_detectors[y]['SessionToken'],
            region_name=all_gd_detectors[y]['Region'])
        client_gd_child = session_gd_child.client('guardduty')
        # List Members
        Member_Dict = client_gd_child.list_members(
            DetectorId=str(all_gd_detectors[y]['DetectorIds'][0]), OnlyAssociated='FALSE')['Members']
        for i in range(len(Member_Dict)):
            MemberList.append(Member_Dict[i]['AccountId'])
        try:
            Output = 0
            client_gd_child.disassociate_from_master_account(
                DetectorId=str(all_gd_detectors[y]['DetectorIds'][0])
            )
        except Exception as e:
            if e.response['Error']['Code'] == 'BadRequestException':
                logging.warning("Caught exception 'BadRequestException', handling the exception...")
                pass
        # Disassociate Members
        if MemberList:  # This handles the scenario where the detectors aren't associated with the Master
            client_gd_child.disassociate_members(AccountIds=MemberList,
                                                 DetectorId=str(all_gd_detectors[y]['DetectorIds'][0])
                                                 )
            logging.warning(
                f"Account {str(all_gd_detectors[y]['AccountId'])} has been disassociated from master account")
            client_gd_child.delete_members(
                AccountIds=[all_gd_detectors[y]['AccountId']],
                DetectorId=str(all_gd_detectors[y]['DetectorIds'][0]))
            logging.warning(f"Account {str(all_gd_detectors[y]['AccountId'])} has been deleted from master account")
        client_gd_child.delete_detector(DetectorId=str(all_gd_detectors[y]['DetectorIds'][0]))
        logging.warning(f"Detector {str(all_gd_detectors[y]['DetectorIds'][0])} has been deleted from child account "
                        f"{str(all_gd_detectors[y]['AccountId'])}")
        num_of_gd_detectors -= 1
    """
    if StacksFound[y][3] == 'DELETE_FAILED':
        response=Inventory_Modules.delete_stack(StacksFound[y][0],StacksFound[y][1],StacksFound[y][2],RetainResources=True,ResourcesToRetain=["MasterDetector"])
    else:
        response=Inventory_Modules.delete_stack(StacksFound[y][0],StacksFound[y][1],StacksFound[y][2])
    """
elif not DeletionRun or (DeletionRun and not ReallyDelete):
    print("Client didn't want to delete detectors... ")

print()
print("Thank you for using this tool")
print()
