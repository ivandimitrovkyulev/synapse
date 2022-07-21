"""
Set up program variables.
"""
import os
from dotenv import load_dotenv


load_dotenv()
# Get env variables
TOKEN = os.getenv("TOKEN")
CHAT_ID_ALERTS = os.getenv("CHAT_ID_ALERTS")
CHAT_ID_ALERTS_FILTER = os.getenv("CHAT_ID_ALERTS_FILTER")
CHAT_ID_DEBUG = os.getenv("CHAT_ID_DEBUG")


time_format = "%Y-%m-%d %H:%M:%S, %Z"

log_format = "%(asctime)s - %(levelname)s - %(message)s"

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
