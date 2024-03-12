#! /usr/bin/env python3
import os
import json

from pprint import pprint
from atexit import register
from datetime import datetime
from time import (
    sleep,
    perf_counter,
)
from concurrent.futures import ThreadPoolExecutor

from src.interface import parser
from src.api.rpc import alert_arbitrage
from src.api.exceptions import exit_handler
from src.api.helpers import (
    parse_args,
    print_start_message,
)

from src.common.message import telegram_send_msg
from src.variables import time_format


# Parse arguments
args = parser.parse_args()


# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler, program_name)

# Fetch variables
with open(args.file, 'r') as file:
    configs = json.loads(file.read())

timestamp = datetime.now().astimezone().strftime(time_format)
print(f"{timestamp} - Started Synapse API({configs['settings']['bridge_api']}) Bot")
pprint(configs)

sleep_time = configs['settings']['sleep_time']
bridge_api = configs['settings']['bridge_api']

arguments = parse_args(configs)
network_configs = len(arguments)

print(f"\nQuerying {bridge_api}\n"
      f"Screening {network_configs} different network configurations...\n")
print_start_message(arguments)

telegram_send_msg(f"✅ SYNAPSE_API has started.")

loop_counter = 1
while True:
    start = perf_counter()

    with ThreadPoolExecutor(max_workers=network_configs) as pool:
        results = pool.map(lambda p: alert_arbitrage(*p), arguments, timeout=20)

    sleep(sleep_time)

    timestamp = datetime.now().astimezone().strftime(time_format)
    terminal_mesg = f"{timestamp}: Loop {loop_counter} executed in {(perf_counter() - start):,.2f} secs."
    print(terminal_mesg)
    loop_counter += 1
