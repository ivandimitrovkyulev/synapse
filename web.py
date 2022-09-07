import os
import sys
import json
from pprint import pprint

from time import sleep, perf_counter
from datetime import datetime
from atexit import register

from src.synapse.common.message import telegram_send_message
from src.synapse.common.variables import time_format
from src.synapse.common.helpers import calculate_workers

from src.synapse.driver.driver import chrome_driver
from src.synapse.web.exceptions import exit_handler_driver
from src.synapse.web.price_query import query_synapse
from src.synapse.web.helpers import (
    parse_args_web,
    print_start_message,
)


if len(sys.argv) != 2:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} contracts.json\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler_driver, chrome_driver, program_name)

# Fetch variables
info = json.loads(sys.argv[-1])
timestamp = datetime.now().astimezone().strftime(time_format)
print(f"{timestamp} - Started screening:\n")
pprint(info)

sleep_time = info['settings']['sleep_time']
max_wait_time = info['settings']['max_wait_time']

arguments = parse_args_web(info)

print(f"\nScreening {calculate_workers(info)} different network configurations...\n")
print_start_message(arguments)

telegram_send_message(f"✅ SYNAPSE_WEB has started.")

loop_counter = 1
while True:
    start = perf_counter()

    for arg in arguments:
        query_synapse(*arg, max_wait_time)

    # Sleep and print loop info
    sleep(sleep_time)
    timestamp = datetime.now().astimezone().strftime(time_format)
    print(f"{timestamp} - Loop {loop_counter} executed in {perf_counter() - start} secs.")
    loop_counter += 1
