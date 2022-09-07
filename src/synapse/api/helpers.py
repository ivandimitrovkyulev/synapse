from itertools import permutations
from typing import List
from hashlib import sha256
from tabulate import tabulate


def parse_args(schema: dict) -> List[list]:
    """
    Parses input schema and returns a list of arguments ready to be passed to a function.

    >>> arguments = parse_args(schema)
    >>> print(arguments)
    [[10, 'USDC', [100, 200, 500], [6, 1, 'USDC'], [6, 10, 'USDC'], {"max_swap_amount": 10000, "coins": ["USDC"]}]...]
      ^     ^     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾   ‾‾‾‾‾‾‾‾‾‾‾‾‾   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
     arb   name        amounts         taken_A          token_B                      special_chat
                                  (deci, id, name)  (deci, id, name)
    >>>

    :param schema: Dictionary with input information
    :return: List of argument lists
    """
    special_chat = schema['settings']['special_chat']

    args = []
    for coin in schema['coins']:
        amounts = schema['coins'][coin]['swap_amount']
        networks = schema['coins'][coin]['networks']
        arbitrage = schema['coins'][coin]['arbitrage']

        networks = [[networks[i]['decimals'], networks[i]['chain_id'], networks[i]['token']]
                    for i in networks]
        pairs = list(permutations(networks, 2))

        for pair in pairs:
            temp_list = [arbitrage, coin, amounts, pair[0], pair[1], special_chat]
            args.append(temp_list)

    return args


def print_start_message(arguments: List[list]) -> None:
    """Prints script start message of all network configurations.

    :param arguments: List of argument lists. Output of func paser_args
    """

    table = []
    for arg in arguments:
        min_arb = arg[0]
        token = arg[1]
        amounts = arg[2]
        src_network_name = arg[3]
        dest_network_name = arg[4]

        swap_amounts = [f"{int(amount / 1000)}k" if amount > 1000 else amount for amount in amounts]

        line = [token, src_network_name, dest_network_name, swap_amounts, min_arb]
        table.append(line)

    columns = ["Token", "From", "To", "SwapAmounts", "MinArb"]

    print(tabulate(table, headers=columns, showindex=True,
                   tablefmt="fancy_grid", numalign="left", stralign="left", colalign="left"))


def hash_arb_data(network_in: str, network_out: str, arbitrage: float, rounding: int = 0) -> str:
    """
    Returns a str hash of (network_in + network_out + arbitrage).\n
    For example 'EthereumFantom256.39' -> 'zynt2r6z7wugnfzhui...fwyfzm78mar4wz'

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
