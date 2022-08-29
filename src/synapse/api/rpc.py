from typing import (
    Iterable,
    List,
)
from urllib3 import Retry
from json.decoder import JSONDecodeError

from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests import Session

from src.synapse.common.logger import log_error
from src.synapse.common.variables import network_ids


# Set up and configure requests session
session = Session()
retry_strategy = Retry(total=2, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


def get_token_networks(token: str) -> list:
    """
    Returns all available networks for https://synapseprotocol.com for a given token.
    Return format:\n
    {'name': 'Ethereum Mainnet', 'chainId': 1, 'chainCurrency': 'ETH'}

    :param token: Token symbol, eg. ETH, USDC
    :return: List of network dictionaries
    """
    api = "https://syn-api-dev.herokuapp.com/v1/get_chains_for_token?token={token}"
    token = token.upper()

    url = api.format(token=token)
    response = session.get(url, timeout=10).json()

    return response


def get_bridgeable_tokens(chain: str) -> list:
    """
    Returns all bridgeable tokens for a network on https://synapseprotocol.com.

    :param chain: Chain name, eg. Ethereum
    :return: List of briadgeable tokens
    """
    api = "https://syn-api-x.herokuapp.com/v1/get_bridgeable_tokens?chain={chain}"
    chain = chain.upper()

    url = api.format(chain=chain)
    response = session.get(url, timeout=10).json()

    return response


def check_max_arb(all_arbs: dict, min_diff: int = 5) -> tuple:
    """
    Checks for the optimal swap/arb ratio.

    :param all_arbs: Dictionary with all arbs, where key-arb, value-swap
    :param min_diff: Minimum difference between swaps
    :return: Tuple of (max_arb, swap_amount)
    """
    arb_list = [key for key in all_arbs.keys()]

    curr_arb = arb_list[0]
    for i, arb in enumerate(arb_list):
        if i > 0 and arb - arb_list[i - 1] > min_diff:
            curr_arb = arb

    if max(all_arbs) - curr_arb > 2 * min_diff:
        max_arb = max(all_arbs)
    else:
        max_arb = curr_arb

    return max_arb, all_arbs[max_arb]


def get_bridge_output(amounts: List, network_in: Iterable, network_out: Iterable,
                      timeout: float = 3) -> tuple or None:
    """
    Queries https://synapseprotocol.com for swap bridge output for a cross-chain transaction.

    :param amounts: List of amounts to swap
    :param network_in: Origin chain iterable with decimals, chain_id & token_name
    :param network_out: Target chain iterable with decimals, chain_id & token_name
    :param timeout: Max number of secs to wait per request
    :return: Tuple of max_arb & amount swapped in
    """
    api = "https://syn-api-dev.herokuapp.com/v1/estimate_bridge_output"

    decimals_in, chain_id_in, token_in = network_in
    decimals_out, chain_id_out, token_out = network_out
    name_in = network_ids[str(chain_id_in)]
    name_out = network_ids[str(chain_id_out)]

    all_arbs = {}
    for amount in amounts:

        # Add zeros to be a valid synapse api argument
        amount_in = amount * (10 ** decimals_in)

        payload = {'fromChain': chain_id_in, 'toChain': chain_id_out,
                   'fromToken': token_in, 'toToken': token_out, 'amountFrom': amount_in}

        try:
            response = session.get(api, params=payload, timeout=timeout)
        except ConnectionError as e:
            log_error.critical(f"'ConnectionError' - {e} - {name_in} --> {name_out}, {token_in} -> {token_out}")
            # If response not returned break for loop
            break

        try:
            message = response.json()
        except JSONDecodeError:
            log_error.critical(f"'JSONError' {response.status_code} - {response.url}")
            break

        try:
            amount_out = message['amountToReceive']
        except KeyError:
            log_error.warning(f"'ResponseError' {response.status_code} - {message} - "
                              f"{name_in} --> {name_out}, {token_in} -> {token_out}")
            # If response not returned break for loop
            break

        # Calculate arbitrage
        amount_out = int(amount_out) / (10 ** decimals_out)
        arbitrage = amount_out - amount
        # Add arb to arbs' dictionary
        all_arbs[arbitrage] = amount

    if len(all_arbs) > 0:
        # Return max arbitrage
        return check_max_arb(all_arbs)
    else:
        return None
