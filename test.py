import sys
import os
import json

from itertools import permutations

from src.synapse.api import get_bridge_output
from src.synapse.common import parse_args


info = json.loads(sys.argv[-1])


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


a = calculate_workers(info)
print(a)
