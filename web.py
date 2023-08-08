import os
import sys
import json
from pprint import pprint

from time import sleep, perf_counter
from datetime import datetime
from atexit import register

from src.common.message import telegram_send_msg
from src.variables import time_format

from src.driver.driver import chrome_driver
from src.web.exceptions import exit_handler_driver
from src.web.price_query import (
    query_synapse,
    SynapseFrontEndExc,
    SynapseAmountOutExc,
)
from src.web.helpers import (
    parse_args_web,
    print_start_message,
)


if len(sys.argv) != 2:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} contracts.json\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler_driver, chrome_driver, program_name)

# Fetch variables
with open(sys.argv[-1], 'r') as file:
    info = json.loads(file.read())
timestamp = datetime.now().astimezone().strftime(time_format)
print(f"{timestamp} - Started screening:\n")
pprint(info)

sleep_time = info['settings']['sleep_time']
max_wait_time = info['settings']['max_wait_time']

arguments = parse_args_web(info)

print(f"\nScreening {len(arguments)} different network configurations...\n")
print_start_message(arguments)

telegram_send_msg(f"✅ SYNAPSE_WEB has started.")

loop_counter = 1
front_end_fails = 0
while True:
    start = perf_counter()

    for arg in arguments:
        try:
            query_synapse(*arg, max_wait_time)

        except SynapseFrontEndExc as ex:
            front_end_fails += 1

            if front_end_fails >= 100:
                telegram_send_msg(f"SynapseFrontEndExc encountered more than {front_end_fails} times", debug=True)
                front_end_fails = 0

        except SynapseAmountOutExc as ex:
            pass

    # Sleep and print loop info
    sleep(sleep_time)
    timestamp = datetime.now().astimezone().strftime(time_format)
    print(f"{timestamp} - Loop {loop_counter} executed in {perf_counter() - start} secs.")
    loop_counter += 1
