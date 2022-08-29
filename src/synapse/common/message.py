from time import sleep
from typing import Optional

from urllib3 import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ConnectionError,
    ReadTimeout,
)
from requests import (
    Session,
    Response,
)
from src.synapse.common.logger import log_telegram

from src.synapse.common.variables import (
    TOKEN,
    CHAT_ID_ALERTS,
    CHAT_ID_DEBUG,
)


session = Session()
retry_strategy = Retry(total=2, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


def telegram_send_message(
        message_text: str,
        disable_web_page_preview: bool = True,
        telegram_token: Optional[str] = "",
        telegram_chat_id: Optional[str] = "",
        debug: bool = False,
        timeout: float = 10,
) -> Response or None:
    """
    Sends a Telegram message to a specified chat.
    Must have a .env file with the following variables:
    TOKEN: your Telegram access token.
    CHAT_ID: the specific id of the chat you want the message sent to
    Follow telegram's instruction on how to set up a bot using the bot father
    and configure it to be able to send messages to a chat.

    :param message_text: Text message to send
    :param disable_web_page_preview: Set web preview on/off
    :param telegram_token: Telegram TOKEN API, default is 'TOKEN' from .env file
    :param telegram_chat_id: Telegram chat ID for alerts, default is 'CHAT_ID_ALERTS' from .env file
    :param debug: If true sends message to Telegram 'CHAT_ID_DEBUG' chat taken from .env file
    :param timeout: Max secs to wait for POST request
    :return: requests.Response
    """
    telegram_token = str(telegram_token)
    telegram_chat_id = str(telegram_chat_id)
    message_text = str(message_text)

    # if Token not provided - try TOKEN variable from the .env file
    if telegram_token == "":
        telegram_token = TOKEN

    # if Chat ID not provided - try CHAT_ID_ALERTS or CHAT_ID_DEBUG variable from the .env file
    if telegram_chat_id == "":
        if debug:
            telegram_chat_id = CHAT_ID_DEBUG
        else:
            telegram_chat_id = CHAT_ID_ALERTS

    # construct url using token for a sendMessage POST request
    url = "https://api.telegram.org/bot{}/sendMessage".format(telegram_token)

    # Construct data for the request
    payload = {"chat_id": telegram_chat_id, "text": message_text,
               "disable_web_page_preview": disable_web_page_preview, "parse_mode": "HTML"}

    # send the POST request
    try:
        # If too many requests, wait for Telegram's rate limit
        counter = 1
        while True:
            try:
                post_request = session.post(url=url, data=payload, timeout=timeout)

                if post_request.json()['ok']:
                    return post_request

                sleep(3)

            except ReadTimeout as e:
                log_telegram.warning(f"'telegram_send_message' - {e} - Attempt: {counter}")
                counter += 1

    except ConnectionError or ReadTimeout as e:
        log_telegram.critical(f"'telegram_send_message' - {e} - '{message_text})' was not sent.")
        return None
