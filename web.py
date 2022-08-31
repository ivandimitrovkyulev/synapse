import os
import sys
import json
from pprint import pprint

from time import sleep, perf_counter
from datetime import datetime
from atexit import register

from src.synapse.common.exceptions import exit_handler
from src.synapse.common.message import telegram_send_message
from src.synapse.web.price_query import query_synapse
from src.synapse.common.variables import time_format
from src.synapse.common.helpers import (
    parse_args_web,
    calculate_workers,
    print_start_message,
)


if len(sys.argv) != 2:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} contracts.json\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler, program_name)

# Fetch variables
info = json.loads(sys.argv[-1])
timestamp = datetime.now().astimezone().strftime(time_format)
print(f"{timestamp} - Started screening:\n")
pprint(info)

sleep_time = info['settings']['sleep_time']
max_wait_time = info['settings']['max_wait_time']
info.pop('settings')

arguments = parse_args_web(info)

print(f"\nScreening {calculate_workers(info)} different network configurations...\n")
print_start_message(arguments)

telegram_send_message(f"✅ SYNAPSE_WEB has started.")

while True:
    start = perf_counter()

    for arg in arguments:
        query_synapse(*arg, max_wait_time)

    # Sleep and print loop info
    sleep(sleep_time)
    timestamp = datetime.now().astimezone().strftime(time_format)
    print(f"{timestamp} - Loop executed in {perf_counter() - start} secs.")
