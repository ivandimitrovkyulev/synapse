"""
Set up program variables.
"""
import os
from dotenv import load_dotenv


load_dotenv()
# Get env variables
TOKEN = os.getenv("TOKEN")
CHAT_ID_ALERTS = os.getenv("CHAT_ID_ALERTS")
CHAT_ID_DEBUG = os.getenv("CHAT_ID_DEBUG")


time_format = "%Y-%m-%d %H:%M:%S, %Z"

log_format = "%(asctime)s - %(levelname)s - %(message)s"
