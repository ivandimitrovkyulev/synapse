import os
import sys
import json

from time import sleep, perf_counter
from pprint import pprint
from atexit import register
from datetime import datetime

from src.synapse.exceptions import exit_handler
from src.synapse.interface import args
from src.synapse.common import parse_args
from src.synapse.api import get_bridge_output
from src.synapse.message import telegram_send_message
from src.synapse.logger import log_arbitrage
from src.synapse.variables import (
    time_format,
    network_ids,
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
            min_arbitrage, coin, *func_args = arg

            # Query swap amount out
            swap_amount = get_bridge_output(*func_args)
            # Execute only if swap_amount is Not None, eg. get request was successful
            if swap_amount and swap_amount >= min_arbitrage:
                amount = func_args[0]
                arbitrage = swap_amount - amount

                decimals_in, chain_id_in, token_in = arg[3]
                decimals_out, chain_id_out, token_out = arg[4]
                network_in = network_ids[str(chain_id_in)]
                network_out = network_ids[str(chain_id_out)]
                timestamp = datetime.now().astimezone().strftime(time_format)

                message = f"{timestamp}\n" \
                          f"Sell {amount:,} {token_in} {network_in} -> {network_out}\n" \
                          f"\t--->Arbitrage: <a href='https://synapseprotocol.com'>{arbitrage:,} {token_out}</a>"

                ter_msg = f"Sell {amount:,} {network_in}, {token_in} -> {network_out}, {token_out}\n" \
                          f"\t--->Arbitrage: {arbitrage:,} {token_out}"

                telegram_send_message(message)
                log_arbitrage.info(ter_msg)
                print(ter_msg)

        # sleep(10)
        end = perf_counter()
        print(f"Loop executed in {(end - start):,} secs.")
