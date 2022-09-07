from datetime import datetime
from typing import (
    Iterable,
    List,
)
from json.decoder import JSONDecodeError

from requests.exceptions import ConnectionError

from src.synapse.api.helpers import hash_arb_data
from src.synapse.common.variables import network_ids
from src.synapse.common.message import telegram_send_message
from src.synapse.common.logger import (
    log_error,
    log_arbitrage,
)
from src.synapse.common.variables import (
    time_format,
    stablecoins,
    http_session,
    CHAT_ID_ALERTS,
    CHAT_ID_SPECIAL,
)


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
    response = http_session.get(url, timeout=10).json()

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
    response = http_session.get(url, timeout=10).json()

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
            response = http_session.get(api, params=payload, timeout=timeout)
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
        all_arbs[arbitrage] = (amount, amount_out)

    if len(all_arbs) > 0:
        # Return max arbitrage
        if token_in in stablecoins:
            return check_max_arb(all_arbs)
        else:
            max_arb = max(all_arbs)
            return max_arb, all_arbs[max_arb]
    else:
        return None


def alert_arbitrage(min_arb: float, coin: str, amounts: list,
                    network_in: Iterable, network_out: Iterable, special_chat: dict) -> dict or None:
    """
    Queries bridge swap output and if arbitrage > min_arb alerts and then returns a dict with hashed id and
    constructed message to send.

    :param min_arb: Min required arbitrage
    :param coin: Token name
    :param amounts: List of amounts to swap
    :param network_in: In network details, (decimal, id, name)
    :param network_out: Out network details, (decimal, id, name)
    :param special_chat: Send specific info, if empty ignore
    :return: Dictionary with id and message
    """

    # Query swap amount out
    data = get_bridge_output(amounts, network_in, network_out)

    if not data:
        return None

    arbitrage = data[0]
    amount_in, amount_out = data[1]

    # Execute only if swap_amount is Not None, eg. get request was successful
    if arbitrage >= min_arb:

        decimals_in, chain_id_in, token_in = network_in
        decimals_out, chain_id_out, token_out = network_out
        network_in = network_ids[str(chain_id_in)]
        network_out = network_ids[str(chain_id_out)]
        timestamp = datetime.now().astimezone().strftime(time_format)

        arbitrage = round(arbitrage, int(decimals_in // 3))

        message = f"{timestamp} - Synapse API\n" \
                  f"Sell {amount_in:,} {token_in} for {amount_out:,.2f} {token_out}, {network_in} -> {network_out}\n" \
                  f"--->Arbitrage: <a href='https://synapseprotocol.com'>{arbitrage:,.2f} {token_out}</a>"

        ter_msg = f"Sell {amount_in:,} {token_in} for {amount_out:,.2f} {token_out}, {network_in} -> {network_out}; " \
                  f"--->Arbitrage: {arbitrage:,} {token_out}"

        # Send arbitrage to ALL alerts channel and log
        telegram_send_message(message, telegram_chat_id=CHAT_ID_ALERTS)
        log_arbitrage.info(ter_msg)
        print(ter_msg)

        # If special chat required, send telegram msg to it
        if special_chat:
            if float(special_chat['max_swap_amount']) >= float(amount_in) and token_in.upper() in special_chat['coins']:
                telegram_send_message(message, telegram_chat_id=CHAT_ID_SPECIAL)

        # Hash id to compare arbs later
        id_hash = hash_arb_data(network_in, network_out, arbitrage)

        return {"id": id_hash, "message": message,
                "networks": str(network_in) + str(network_out), "arbitrage": arbitrage, "coin": coin}
