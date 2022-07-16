import os
import sys
import json

from time import sleep, perf_counter
from pprint import pprint
from atexit import register
from datetime import datetime

from src.synapse.exceptions import exit_handler
from src.synapse.interface import args
from src.synapse.variables import time_format
from src.synapse.common import (
    parse_args,
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

    while True:

        start = perf_counter()
        for arg in parse_args(info):
            arbitrage_alert(arg)

        sleep(10)
        end = perf_counter()
        print(f"Loop time - {(end - start):,} secs.")
