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
from src.synapse.logger import log_arbitrage
from src.synapse.interface import args
from src.synapse.variables import time_format
from src.synapse.common import (
    parse_args,
    calculate_workers,
    arbitrage_alert,
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


if args.screen:

    workers = calculate_workers(info)

    loop_counter = 1
    old_arbitrages = {}
    while True:
        start = perf_counter()
        arguments = parse_args(info)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = pool.map(arbitrage_alert, arguments, timeout=90)

        arbs = [result for result in results]
        new_arbitrages = {arb['id']: arb['arbitrage'] for arb in arbs}
        Z
        
        old_arbitrages = deepcopy(new_arbitrages)

        message = f"Loop {loop_counter} executed in {(perf_counter() - start):,.2f} secs"
        log_arbitrage.info(message)

        sleep(10)
        loop_counter += 1
