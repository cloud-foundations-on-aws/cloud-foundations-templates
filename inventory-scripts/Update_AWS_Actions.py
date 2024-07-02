import sys
import boto3
from ArgumentsClass import CommonArguments
from os.path import split
from time import time
from datetime import datetime
from tqdm.auto import tqdm, trange
import logging
from colorama import Fore, Style, init
from threading import Thread
from queue import Queue

__version__ = "2024.04.24"

from tqdm import trange

init()


##################
# Functions
##################

def parse_args(f_arguments):
	"""
	Description: Parses the arguments passed into the script
	@param f_arguments: args represents the list of arguments passed in
	@return: returns an object namespace that contains the individualized parameters passed in
	"""
	script_path, script_name = split(sys.argv[0])
	parser = CommonArguments()
	parser.my_parser.description = "We're going to find all API actions within the available AWS services."
	parser.timing()
	parser.save_to_file()
	parser.verbosity()
	parser.version(__version__)
	local = parser.my_parser.add_argument_group(script_name, 'Parameters specific to this script')
	# local.add_argument(
	# 	"-s", "--status",
	# 	dest="pStatus",
	# 	choices=['running', 'stopped'],
	# 	type=str,
	# 	default=None,
	# 	help="Whether you want to limit the instances returned to either 'running', 'stopped'. Default is both")
	return parser.my_parser.parse_args(f_arguments)


def random_string(stringLength=10):
	"""
	Description: Generates a random string
	@param stringLength: to determine the length of the random number generated
	@return: returns a random string of characters of length "stringlength"
	"""
	import random
	import string
	# Generate a random string of fixed length
	letters = string.ascii_lowercase
	randomstring = (''.join(random.choice(letters) for _ in range(stringLength)))
	return randomstring


def get_aws_actions():
	"""
	Description: Gets all the actions for all the services in AWS
	@return: list of actions
	"""

	class AWSActionThread(Thread):
		def __init__(self, queue):
			Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				# existing code to get actions for a service
				c_service = self.queue.get()
				client = boto3.client(c_service)
				try:
					list_of_operations = client.meta.method_to_api_mapping.keys()
					# print(f"{ERASE_LINE}Checking actions for {c_service}", end='\r', flush=True)
					for operation in tqdm(list_of_operations, desc=f'actions for {c_service}', leave=False):
						action_list.append({'Service': c_service, 'Operation': operation})
				except AttributeError as myError:
					print(myError)
					action_list.append({'Service': c_service, 'Operation': None})
					pass
				finally:
					self.queue.task_done()

	checkqueue = Queue()
	action_list = []
	workerthreads = 10

	for x in trange(workerthreads, desc=f"Creating {workerthreads} worker threads", leave=False
	                # , position=0
	                ):
		worker = AWSActionThread(checkqueue)
		worker.daemon = True
		worker.start()

	# Create a thread for every service.
	print(f"Capturing all available AWS Services...")
	for service in tqdm(list_of_services, desc=f"Checking actions for each service"
	                    # , position=0
	                    ):
		# for service in list_of_services:
		checkqueue.put(service)
		checkqueue.join()

	return action_list


def save_file(file_to_save_to: str = None, input_data: list = None):
	"""
	Description: Saves the data to a file
	@param file_to_save_to:
	@param input_data:
	@return: None
	"""
	if input_data is None:
		print(f"Input data cannot be none. Exiting...")
		raise SystemExit(1)
	elif len(input_data) == 0:
		print(f"No data to save. Exiting...")
		raise SystemExit(1)

	if file_to_save_to is None:
		print(f"No filename provided to save data.\n"
		      f"Using a randomized name.")
		file_to_save_to = random_string(15) + ".txt"
	else:
		logging.info(f"Saving data to {file_to_save_to}")
	with open(file_to_save_to, 'w', encoding="utf-8") as f:
		for item in input_data:
			f.write(f"{item['Service']}:{item['Operation']}\n")
	return file_to_save_to

##################
# Main
##################
ERASE_LINE = '\x1b[2K'
begin_time = time()

if __name__ == "__main__":
	arguments = parse_args(sys.argv[1:])
	pTiming = arguments.Time
	file_to_save = arguments.Filename
	verbose = arguments.loglevel
	logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
	logging.getLogger("boto3").setLevel(logging.CRITICAL)
	logging.getLogger("botocore").setLevel(logging.CRITICAL)
	logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)

	list_of_services = boto3.Session().get_available_services()
	all_actions = get_aws_actions()
	if pTiming:
		print(ERASE_LINE)
		print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
	print(ERASE_LINE)
	print(f"Found {len(all_actions)} actions across {len(list_of_services)} services")
	filename = save_file(file_to_save, all_actions)
	print(f"Saved to {filename}")
	print("Thank you for using this script")
	print()
