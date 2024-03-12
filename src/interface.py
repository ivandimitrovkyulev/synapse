from argparse import ArgumentParser

from src import __version__


# Create CLI interface
parser = ArgumentParser(
    usage="python3 %(prog)s <arg> <input file>\n",
    description="Synapse API bot that screens https://synapseprotocol.com for arbitrage using their APIs"
                "and alerts via a Telegram message."
                "Visit https://github.com/ivandimitrovkyulev/SynapseBridge for more info.",
    epilog=f"Version - {__version__}",
)

parser.add_argument(
    "-f",
    "--file",
    action="store",
    default="api.json",
    type=str,
    help=f"Path to 'api.json' file with all configuration settings as defined in README.md."
)

parser.add_argument(
    "-v",
    "--version",
    action="version",
    version=__version__,
    help="Prints the program's current version."
)
