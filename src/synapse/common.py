from typing import List
from itertools import permutations


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
