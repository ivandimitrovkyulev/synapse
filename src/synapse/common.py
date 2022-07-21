from datetime import datetime
from itertools import permutations
from typing import List
from hashlib import sha256

from src.synapse.message import telegram_send_message
from src.synapse.api import get_bridge_output
from src.synapse.logger import log_arbitrage
from src.synapse.variables import (
    time_format,
    network_ids,
    CHAT_ID_ALERTS,
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


def dict_complement_b(old_dict: dict, new_dict: dict,) -> dict:
    """
    Compares dictionary A & B and returns the relative complement of A in B.
    Basically returns a dictionary of all members in B that are not in A, as in Venn's diagrams.

    :param old_dict: dictionary A
    :param new_dict: dictionary B
    :returns: Python Dictionary
    """

    return {k: new_dict[k]
            for k in new_dict
            if k not in old_dict}


def hash_arb_data(network_in: str, network_out: str, arbitrage: float, rounding: int = 0) -> str:
    """
    Returns a str hash of (network_in + network_out + arbitrage).\n
    For example 'EthereumFantom256.1321' -> 'zynt2r6z7wugnfzhui...fwyfzm78mar4wz'

    :param network_in: Network sending from
    :param network_out: Network sending to
    :param arbitrage: Arbitrage amount
    :param rounding: Rounding precision
    :return: String of hashed data
    """
    arbitrage = round(arbitrage, rounding)

    arb_id = str(network_in) + str(network_out) + str(arbitrage)
    arb_id_bytes = bytes(str(arb_id), encoding='utf8')

    hashed_id = sha256(arb_id_bytes).hexdigest()

    return hashed_id


def check_arbitrage(arguments: List) -> dict or None:
    """
    Queries bridge swap output and if arbitrage > min_arb then returns a dict with hashed id and
    constructed message to send.

    :param arguments: List of all network arguments in format:
    [10, 'USDC', [100, 1100, 100], [6, 1, 'USDC'], [6, 10, 'USDC']]
    :return: Dictionary with id and message
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
                  f"--->Arbitrage: <a href='https://synapseprotocol.com'>{arbitrage:,} {token_out}</a>"

        ter_msg = f"Sell {amount:,} {token_in} {network_in} -> {network_out}; " \
                  f"--->Arbitrage: {arbitrage:,} {token_out}"

        # Send arbitrage to ALL alerts channel and log
        telegram_send_message(message, telegram_chat_id=CHAT_ID_ALERTS)
        log_arbitrage.info(ter_msg)
        print(ter_msg)

        # Hash id to compare arbs later
        id_hash = hash_arb_data(network_in, network_out, arbitrage)

        return {"id": id_hash, "message": message,
                "networks": str(network_in) + str(network_out), "arbitrage": arbitrage}
