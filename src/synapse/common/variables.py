"""
Set up program variables.
"""
import os
from re import compile
from dotenv import load_dotenv
from urllib3 import Retry

from requests import Session
from requests.adapters import HTTPAdapter


load_dotenv()
# Get env variables
TOKEN = os.getenv("TOKEN")
CHAT_ID_ALERTS = os.getenv("CHAT_ID_ALERTS")
CHAT_ID_ALERTS_FILTER = os.getenv("CHAT_ID_ALERTS_FILTER")
CHAT_ID_SPECIAL = os.getenv("CHAT_ID_SPECIAL")
CHAT_ID_DEBUG = os.getenv("CHAT_ID_DEBUG")

# Set up and configure requests session
http_session = Session()
retry_strategy = Retry(total=2, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)

time_format = "%Y-%m-%d %H:%M:%S, %Z"
time_format_regex = compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}, [A-Za-z]*")

log_format = "%(asctime)s - %(levelname)s - %(message)s"

stablecoins = ['USDC', 'USDT', 'DAI']

network_ids = {
    "1": "Ethereum",
    "10": "Optimism",
    "25": "Cronos",
    "56": "Binance",
    "137": "Polygon",
    "250": "Fantom",
    "288": "Boba",
    "1088": "Metis",
    "1284": "Moonbeam",
    "1285": "Moonriver",
    "42161": "Arbitrum",
    "43114": "Avalanche",
    "1313161554": "Aurora",
    "1666600000": "Harmony",
}

network_names = {
    "Ethereum": '1',
    "Optimism": '10',
    "Cronos": '25',
    "Binance": '56',
    "Polygon": '137',
    "Fantom": '250',
    "Boba": '288',
    "Metis": '1088',
    "Moonbeam": '1284',
    "Moonriver": '1285',
    "Arbitrum": '42162',
    "Avalanche": '43114',
    "Aurora": '1313161554',
    "Harmony": '1666600000',
}
