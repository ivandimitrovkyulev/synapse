from itertools import permutations


def calculate_workers(schema: dict) -> int:
    """
    Calculates total number of unique network queries (50k USDC ETH -> BSC).

    :param schema: Dictionary with input information
    :return: Number of queries
    """

    workers = 0
    for coin in schema['coins']:
        ranges = schema['coins'][coin]['swap_amount']
        range_count = len(ranges)

        networks = schema['coins'][coin]['networks']
        network_count = len(list(permutations(networks, 2)))

        workers += network_count * range_count

    return workers
