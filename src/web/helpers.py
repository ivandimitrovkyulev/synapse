from typing import List
from tabulate import tabulate

from src.driver.driver import chrome_driver


def print_start_message(arguments: List[list]) -> None:
    """Prints script start message of all network configurations.

    :param arguments: List of argument lists. Output of func paser_args
    """

    table = []
    for arg in arguments:
        amounts = arg[1]
        min_arb = arg[2]
        src_network_name = arg[3]
        dest_network_name = arg[4]
        token = arg[5]

        swap_amounts = [f"{int(amount / 1000)}k" if amount > 1000 else amount for amount in amounts]

        line = [token, src_network_name, dest_network_name, swap_amounts, min_arb]
        table.append(line)

    columns = ["Token", "From", "To", "SwapAmounts", "MinArb"]

    print(tabulate(table, headers=columns, showindex=True,
                   tablefmt="fancy_grid", numalign="left", stralign="left", colalign="left"))


def parse_args_web(schema: dict) -> List[list]:
    """
    Parses input schema and returns a list of arguments ready to be passed to a function.

    >>> arguments = parse_args_web(schema)
    >>> print(arguments)
    [[driver, [10,000, 20,000, 50,000], 30, '1', '10'], {"max_swap_amount": 10000, "coins": ["USDC"]}...]

    >>>

    :param schema: Dictionary with input information
    :return: List of argument lists
    """
    special_chat = schema.get('settings').get('special_chat')
    coins: dict = schema.get('coins')

    args = []
    for coin_name, coin_info in coins.items():
        print(coin_name)

        amounts = coin_info.get('swap_amount')

        for network, info in coin_info.get('networks').items():
            arbitrage = info.get('arbitrage')
            args.append([chrome_driver, amounts, arbitrage, 'Ethereum', network, coin_name, special_chat])

    return args
