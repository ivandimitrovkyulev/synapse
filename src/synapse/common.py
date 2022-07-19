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
    Returns the following scheme: [10, 'USDC', [100, 1100, 100], [6, 1, 'USDC'], [6, 10, 'USDC']]

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


def calculate_workers(schema: dict) -> int:
    """
    Calculates total number of unique network queries (50k USDC ETH -> BSC).

    :param schema: Dictionary with input information
    :return: Number of queries
    """
    workers = 0
    for coin in schema:
        ranges = schema[coin]['swap_amount']
        range_count = len([i for i in range(*ranges)])

        networks = schema[coin]['networks']
        network_count = len(list(permutations(networks, 2)))

        workers += network_count * range_count

    return workers


def arbitrage_alert(arguments: List) -> None:
    """
    Queries bridge swap output and if arbitrage > min then alerts for the highest arbitrage via Telegram.

    :param arguments: List of all network arguments in format:
    [10, 'USDC', [100, 1100, 100], [6, 1, 'USDC'], [6, 10, 'USDC']]
    :return: None
    """
    min_arbitrage, coin, *func_args = arguments

    # Query swap amount out
    data = get_bridge_output(*func_args)

    if not data:
        return None

    arbitrage = data[0]
    amount = data[1]

    # Execute only if swap_amount is Not None, eg. get request was successful
    if arbitrage >= min_arbitrage:

        decimals_in, chain_id_in, token_in = arguments[3]
        decimals_out, chain_id_out, token_out = arguments[4]
        network_in = network_ids[str(chain_id_in)]
        network_out = network_ids[str(chain_id_out)]
        timestamp = datetime.now().astimezone().strftime(time_format)

        arbitrage = round(arbitrage, int(decimals_in / 3))

        message = f"{timestamp}\n" \
                  f"Sell {amount:,} {token_in} {network_in} -> {network_out}\n" \
                  f"\t--->Arbitrage: <a href='https://synapseprotocol.com'>{arbitrage:,} {token_out}</a>"

        ter_msg = f"Sell {amount:,} {token_in} {network_in} -> {network_out}; " \
                  f"--->Arbitrage: {arbitrage:,} {token_out}"

        telegram_send_message(message)
        log_arbitrage.info(ter_msg)
        print(ter_msg)
