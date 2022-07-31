import os
import sys
import json

from copy import deepcopy
from pprint import pprint
from atexit import register
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from time import (
    sleep,
    perf_counter,
)

from src.synapse.exceptions import exit_handler
from src.synapse.message import telegram_send_message
from src.synapse.logger import log_arbitrage
from src.synapse.interface import args
from src.synapse.variables import (
    time_format,
    CHAT_ID_ALERTS_FILTER,
)
from src.synapse.common import (
    parse_args,
    calculate_workers,
    check_arbitrage,
    dict_complement_b,
)


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
info.pop('settings')

if args.screen:

    configurations = calculate_workers(info)
    print(f"Screening {configurations} different network configurations...")

    loop_counter = 1
    old_arbs = {}
    while True:
        start = perf_counter()
        arguments = parse_args(info)

        with ThreadPoolExecutor(max_workers=configurations) as pool:
            results = pool.map(check_arbitrage, arguments, timeout=90)

        new_arbs = {arb['id']: arb['message'] for arb in results if arb}

        # Send filtered arbs only
        found_arbs = dict_complement_b(old_arbs, new_arbs)
        for arb_msg in found_arbs.values():
            telegram_send_message(arb_msg, telegram_chat_id=CHAT_ID_ALERTS_FILTER)

        # Save current arbs to compare later; then sleep
        old_arbs = deepcopy(new_arbs)
        sleep(sleep_time)

        timestamp = datetime.now().astimezone().strftime(time_format)
        terminal_mesg = f"{timestamp}: Loop {loop_counter} executed in {(perf_counter() - start):,.2f} secs."
        log_arbitrage.info(terminal_mesg)
        print(terminal_mesg)
        loop_counter += 1
