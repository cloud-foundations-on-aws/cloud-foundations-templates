#!/usr/bin/env python3


import logging
from ArgumentsClass import CommonArguments
from account_class import aws_acct_access
__version__ = "2023.05.04"

parser = CommonArguments()
parser.singleprofile()
parser.singleregion()
parser.verbosity()
parser.version(__version__)
parser.my_parser.add_argument(
	"-b", "--bucket",
	dest="pBucketName",
	metavar="bucket to empty and delete",
	required=True,
	help="To specify a bucket, use this parameter.")
parser.my_parser.add_argument(
	'+delete', '+force-delete',
	help="Whether or not to delete the bucket after it's been emptied",
	action="store_const",
	dest="pForceQuit",
	const=True,
	default=False)
args = parser.my_parser.parse_args()

pProfile = args.Profile
pRegion = args.Region
pBucketDelete = args.pForceQuit
pBucketName = args.pBucketName
verbose = args.loglevel
logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

aws_acct = aws_acct_access(pProfile)
s3 = aws_acct.session.resource(service_name='s3')

print()
print(f"This script is about to delete all versions of all objects from bucket {pBucketName}")
print()

bucket = s3.Bucket(pBucketName)
try:
	# print(len(list(bucket.object_versions.all)))# Deletes everything in the bucket
	bucket.object_versions.delete()
except Exception as my_Error:
	print(f"Error message: {my_Error}")

DeleteBucket = False
if pBucketDelete:  # They provided the parameter that said they wanted to delete the bucket
	print(f"As per your request, we're deleting the bucket {pBucketName}")
	bucket.delete()
	print(f"Bucket: {pBucketName} has been deleted")
else:
	DeleteBucket = (input("Now that the bucket is empty, do you want to delete the bucket? (y/n): ") in ["y", "Y"])
	if DeleteBucket:
		bucket.delete()
		print(f"Bucket: {pBucketName} has been deleted")
	else:
		print(f"Bucket: {pBucketName} has NOT been deleted")
print()
print("Thanks for using this script...")
print()
