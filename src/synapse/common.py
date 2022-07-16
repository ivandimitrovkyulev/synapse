from datetime import datetime
from itertools import permutations
from typing import List

from src.synapse.api import get_bridge_output
from src.synapse.message import telegram_send_message
from src.synapse.logger import log_arbitrage
from src.synapse.variables import (
    time_format,
    network_ids,
)


def parse_args(schema: dict) -> List[list]:
    """
    Parses input schema and returns a list of arguments ready to be parsed to a function.

    :param schema: Dictionary with input information
    :return: List of all argument lists
    """

    args = []
    for coin in schema:
        amount = schema[coin]['swap_amount']
        networks = schema[coin]['networks']
        arbitrage = schema[coin]['arbitrage']

        networks = [[networks[i]['decimals'], networks[i]['chain_id'], networks[i]['token']]
                    for i in networks]
        pairs = list(permutations(networks, 2))

        for pair in pairs:
            temp_list = [arbitrage, coin, amount, pair[0], pair[1]]
            args.append(temp_list)

    return args


def arbitrage_alert(arguments: List) -> None:
    min_arbitrage, coin, *func_args = arguments
    amount = func_args[0]

    # Query swap amount out
    swap_amount = get_bridge_output(*func_args)
    # Execute only if swap_amount is Not None, eg. get request was successful
    if swap_amount and ((swap_amount - amount) >= min_arbitrage):
        decimals_in, chain_id_in, token_in = arguments[3]
        decimals_out, chain_id_out, token_out = arguments[4]
        network_in = network_ids[str(chain_id_in)]
        network_out = network_ids[str(chain_id_out)]
        timestamp = datetime.now().astimezone().strftime(time_format)

        arbitrage = round((swap_amount - amount), int(decimals_in / 3))

        message = f"{timestamp}\n" \
                  f"Sell {amount:,} {token_in} {network_in} -> {network_out}\n" \
                  f"\t--->Arbitrage: <a href='https://synapseprotocol.com'>{arbitrage:,} {token_out}</a>"

        ter_msg = f"Sell {amount:,} {token_in} {network_in} -> {network_out}\n" \
                  f"--->Arbitrage: {arbitrage:,} {token_out}"

        telegram_send_message(message)
        log_arbitrage.info(ter_msg)
        print(ter_msg)
