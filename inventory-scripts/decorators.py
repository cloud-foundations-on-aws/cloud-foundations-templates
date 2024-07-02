import functools
import time

from colorama import Fore, init

init()


#############
# Functions
#############
def timer(to_time_or_not: bool = False):
	def decorator_timer(func):
		@functools.wraps(func)
		def wrapper_timer(*args, **kwargs):
			start_time = time.perf_counter()  # 1
			value = func(*args, **kwargs)
			end_time = time.perf_counter()  # 2
			run_time = end_time - start_time  # 3
			if to_time_or_not:
				print()
				print(f"{Fore.GREEN}Finished function {func.__name__!r} in {run_time:.4f} seconds{Fore.RESET}")
				print()
			return value

		return wrapper_timer

	return decorator_timer
