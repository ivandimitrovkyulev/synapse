import requests

from typing import Iterable

from src.synapse.logger import log_error
from src.synapse.variables import network_ids


def get_token_networks(token: str) -> list:
    """
    Returns all available networks for https://synapseprotocol.com for a given token.
    Return format:\n
    {'name': 'Ethereum Mainnet', 'chainId': 1, 'chainCurrency': 'ETH'}

    :param token: Token symbol, eg. ETH, USDC
    :return: List of network dictionaries
    """
    api = "https://syn-api-dev.herokuapp.com/v1/get_chains_for_token?token={token}"

    url = api.format(token=token)
    response = requests.get(url).json()

    return response


def get_bridge_output(amount: float, network_in: Iterable, network_out: Iterable,
                      attempts: int = 3) -> float or None:
    """
    Queries https://synapseprotocol.com for swap amount for a cross-chain bridge transaction.

    :param amount: Amount to swap
    :param network_in: Origin chain iterable with decimals and chain id
    :param network_out: Target chain iterable with decimals and chain id
    :param attempts: Max number of times to repeat GET request
    :return: Amount swapped out
    """
    decimals_in, chain_id_in, token_in = network_in
    decimals_out, chain_id_out, token_out = network_out
    name_in = network_ids[str(chain_id_in)]
    name_out = network_ids[str(chain_id_out)]

    api = "https://syn-api-dev.herokuapp.com/v1/estimate_bridge_output" \
          "?fromChain={chainIn}&toChain={chainOut}" \
          "&fromToken={tokenIn}&toToken={tokenOut}" \
          "&amountFrom={amountIn}"

    amount_in = amount * (10 ** decimals_in)

    url = api.format(amountIn=amount_in,
                     tokenIn=token_in,
                     tokenOut=token_out,
                     chainIn=chain_id_in,
                     chainOut=chain_id_out)

    counter = 1
    while True:
        try:
            message = requests.get(url).json()
            amount_out = int(message['amountToReceive']) / (10 ** decimals_out)

            return amount_out

        except Exception:
            log_error.warning(f"Error querying 'estimate_bridge_output' for "
                              f"{name_in}, {token_in} -> {name_out}, {token_out}. Attempt: {counter}")

            counter += 1
            if counter > attempts:
                # Break and return None
                return None
