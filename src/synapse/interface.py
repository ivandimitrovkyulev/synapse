from argparse import ArgumentParser

from src.synapse import __version__


# Create CLI interface
parser = ArgumentParser(
    usage="python3 %(prog)s <arg> <input file>\n",
    description="Program that screens https://synapseprotocol.com for arbitrage "
                "and alerts via a Telegram message."
                "Visit https://github.com/ivandimitrovkyulev/SynapseBridge for more info.",
    epilog=f"Version - {__version__}",
)

parser.add_argument(
    "-s", "--screen", action="store", type=str, nargs=1, metavar="\b", dest="screen",
    help=f"Screens for a new  Erc20 Token contract transaction and alerts via a Telegram message if it satisfies"
         f" filter criteria."
)

parser.add_argument(
    "-v", "--version", action="version", version=__version__,
    help="Prints the program's current version."
)

# Parse arguments
args = parser.parse_args()
