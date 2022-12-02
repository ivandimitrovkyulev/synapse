import os
import sys
import json

from pprint import pprint
from atexit import register
from datetime import datetime
from time import (
    sleep,
    perf_counter,
)
from concurrent.futures import ThreadPoolExecutor

from src.synapse.interface import args
from src.synapse.api.rpc import alert_arbitrage
from src.synapse.api.exceptions import exit_handler
from src.synapse.api.helpers import (
    parse_args,
    print_start_message,
)

from src.synapse.common.message import telegram_send_message
from src.synapse.common.variables import time_format


if len(sys.argv) != 3:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} <input_file>\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler, program_name)

# Fetch variables
info = json.loads(sys.argv[-1])
timestamp = datetime.now().astimezone().strftime(time_format)
print(f"{timestamp} - Started screening:\n")
pprint(info)

sleep_time = info['settings']['sleep_time']
bridge_api = info['settings']['bridge_api']

if args.screen:
    arguments = parse_args(info)
    network_configs = len(arguments)

    print(f"\nQuerying {bridge_api}\n"
          f"Screening {network_configs} different network configurations...\n")
    print_start_message(arguments)

    telegram_send_message(f"✅ SYNAPSE_API has started.")

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
