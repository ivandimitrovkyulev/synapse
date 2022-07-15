import requests


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


def get_bridge_output(amount: float, token: str, decimals_in: int, decimals_out: int,
                      chain_id_in: int, chain_id_out: int) -> float:
    """
    Queries https://synapseprotocol.com for swap amount for a cross-chain bridge transaction.

    :param amount: Amount to swap
    :param token: Token symbol, eg. USDC
    :param decimals_in: Decimals of token in origin chain
    :param decimals_out: Decimals of token in target chain
    :param chain_in: Origin chain
    :param chain_out: Target chain
    :return: Amount swapped out
    """
    api = "https://syn-api-dev.herokuapp.com/v1/estimate_bridge_output" \
          "?fromChain={chainIn}&toChain={chainOut}" \
          "&fromToken={tokenIn}&toToken={tokenOut}" \
          "&amountFrom={amountIn}"

    amount_in = amount * (10 ** decimals_in)
    token_in = token_out = token.upper()

    url = api.format(amountIn=amount_in,
                     tokenIn=token_in,
                     tokenOut=token_out,
                     chainIn=chain_id_in,
                     chainOut=chain_id_out)

    message = requests.get(url).json()

    amount_out = int(message['amountToReceive']) / (10 ** decimals_out)

    return amount_out


a = get_bridge_output(100000, "USDC", 6, 6, 1, 10)
print(a)