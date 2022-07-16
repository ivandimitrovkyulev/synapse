import os
import sys
import json

from pprint import pprint
from atexit import register
from datetime import datetime

from src.synapse.exceptions import exit_handler
from src.synapse.variables import time_format
from src.synapse.interface import args
from src.synapse.api import get_bridge_output


if len(sys.argv) != 3:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} <input_file>\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler, program_name)

# Fetch variables
info = json.loads(sys.argv[-1])
timestamp = datetime.now().astimezone().strftime(time_format)
print(f"{timestamp} - Started screening:\n")

dictionaries = [dictionary for dictionary in info.values() if type(dictionary) is dict]
pprint(dictionaries)


if args.screen:

    while True:
        pass
