# Write Python3 code here
"""
How to use: 
	from ArgumentsClass import CommonArguments
	parser = CommonArguments()
	parser.extendedargs()
	parser.my_parser.add_argument(...
	< ... >
	< Add more arguments as you would like >
	< ... >
	args = parser.my_parser.parse_args()

	pProfile = args.Profile
	pRegionList = args.Regions
	verbose = args.loglevel

"""
__version__ = "2024.09.24"

import os


class CommonArguments:
	"""
	Class is created on the argparse class, and extends it for my purposes.
	"""

	def __init__(self):
		import argparse
		self.my_parser = argparse.ArgumentParser(
				description='Accept common arguments to the Inventory Scripts',
				allow_abbrev=True,
				prefix_chars='-+')

	def version(self, script_version):
		# self.my_parser.add_argument(
		# 	"--version", "-V",
		# 	dest="Version",
		# 	default=None,
		# 	help="Version #")
		self.my_parser.add_argument("--version", action="version", version=f"Version: {script_version}")

	def rootOnly(self):
		self.my_parser.add_argument(
			"--rootonly",
			dest="RootOnly",
			action="store_true",  # Defaults to False, so the script would continue to run
			help="Only run this code for the root account, not the children")

	def roletouse(self):
		self.my_parser.add_argument(
			"--access_rolename",
			dest="AccessRole",
			default=None,
			metavar="role to use for access to child accounts",
			help="This parameter specifies the single role that will allow this script to have access to the children accounts.")

	def rolestouse(self):
		self.my_parser.add_argument(
			"--access_rolename",
			dest="AccessRoles",
			nargs='*',
			default=None,
			metavar="roles to use for access to child accounts",
			help="This parameter specifies the list of roles that will allow this script to have access to the children accounts.")

	def deletion(self):
		# self.my_parser.add_argument(
		# 	"+forreal",
		# 	help="By default, we report results without changing anything. If you want to remediate or change your environment - include this parameter",
		# 	action="store_false",
		# 	dest="DryRun")              # Default to Dry Run (no changes)
		self.my_parser.add_argument(
			"+force",
			help="To force a change - despite indications to the contrary",
			action="store_true",
			dest="Force")  # Default to Dry Run (no changes)

	def confirm(self):
		self.my_parser.add_argument(
			"+confirm",
			help="To skip confirmation of a change",
			action="store_true",
			dest="Confirm")  # Default to Dry Run (no changes)

	def fix(self):
		self.my_parser.add_argument(
			"+fix",
			help="To intrusively fix something in your accounts",
			action="store_true",
			dest="Fix")

	def verbosity(self):
		import logging
		self.my_parser.add_argument(
				'-v',
				help="Be verbose (Error Statements)",
				action="store_const",
				dest="loglevel",
				const=logging.ERROR,  # args.loglevel = 40
				default=logging.CRITICAL)  # args.loglevel = 50
		self.my_parser.add_argument(
				'-vv', '--verbose',
				help="Be MORE verbose (Warning statements)",
				action="store_const",
				dest="loglevel",
				const=logging.WARNING,  # args.loglevel = 30
				default=logging.CRITICAL)  # args.loglevel = 50
		self.my_parser.add_argument(
				'-vvv',
				help="Print INFO statements",
				action="store_const",
				dest="loglevel",
				const=logging.INFO,  # args.loglevel = 20
				default=logging.CRITICAL)  # args.loglevel = 50
		self.my_parser.add_argument(
				'-d', '--debug',
				help="Print debugging statements",
				action="store_const",
				dest="loglevel",
				const=logging.DEBUG,  # args.loglevel = 10
				default=logging.CRITICAL)  # args.loglevel = 50

	def extendedargs(self):
		self.my_parser.add_argument(
			"-k", "-ka", "--skip", "--skipaccount", "--skipaccounts",
			dest="SkipAccounts",
			nargs="*",
			metavar="Accounts to leave alone",
			default=None,
			help="These are the account numbers you don't want to screw with. Likely the core accounts.")
		self.my_parser.add_argument(
			"-kp", "--skipprofile", "--skipprofiles",
			dest="SkipProfiles",
			nargs="*",
			metavar="Profile names",
			default=None,
			help="These are the profiles you don't want to examine. You can specify 'skipplus' to skip over all profiles using a plus in them.")
		self.my_parser.add_argument(
			"-a", "--account",
			dest="Accounts",
			default=None,
			nargs="*",
			metavar="Account",
			help="Just the accounts you want to check")

	def timing(self):
		self.my_parser.add_argument(
			"--timing", "--time",
			dest="Time",
			action="store_true",
			help="Use this parameter to add a timing for the scripts")

	def fragment(self):
		self.my_parser.add_argument(
			"-f", "--fragment",
			dest="Fragments",
			nargs='*',
			metavar="string fragment",
			default=["all"],
			help="List of fragments of the string(s) you want to check for.")
		self.my_parser.add_argument(
			"-e", "--exact",
			dest="Exact",
			action="store_true",
			help="Use this flag to make sure that ONLY the string you specified will be identified")

	def singleprofile(self):
		self.my_parser.add_argument(
				"-p", "--profile",
				dest="Profile",
				metavar="Profile",
				default=None,  # Default to boto3 defaults
				help="Which *single* profile do you want to run against?")

	def multiprofile(self):
		self.my_parser.add_argument(
				"-p", "-ps", "--profiles",
				dest="Profiles",
				nargs="*",
				metavar="Profiles",
				default=None,  # Defaults to default profile, but can support multiple profiles
				help="Which profiles do you want to run against?")

	def multiregion(self):
		self.my_parser.add_argument(
				"-rs", "--regions", "-r",
				nargs="*",
				dest="Regions",
				metavar="region name string",
				# default=["us-east-1"],
				default=[os.getenv("AWS_DEFAULT_REGION","us-east-1")],
				help="String fragment of the region(s) you want to check for resources. You can supply multiple fragments.\n"
				     "Use 'all' for everything you've opted into, and 'global' for everything, regardless of opted-in status")

	def multiregion_nodefault(self):
		self.my_parser.add_argument(
				"-r", "-rs", "--regions",
				nargs="*",
				dest="Regions",
				metavar="region name string",
				default=None,
				help="String fragment of the region(s) you want to check for resources. You can supply multiple fragments.")

	def singleregion(self):
		self.my_parser.add_argument(
				"-r", "--region",
				dest="Region",
				metavar="region name string",
				default="us-east-1",
				help="Name of the *single* region you want to check for resources.")

	def singleregion_nodefault(self):
		self.my_parser.add_argument(
				"-r", "--region",
				dest="Region",
				metavar="region name string",
				default=None,
				help="Name of the *single* region you want to check for resources.")

	def save_to_file(self):
		self.my_parser.add_argument(
			"--filename",
			dest="Filename",
			metavar="filename",
			default=None,
			help="Name of the filename you want to save results to.")
