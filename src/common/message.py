import requests

from time import sleep

from requests.exceptions import ConnectionError

from src.common.logger import (
    log_error,
    log_telegram,
)
from src.variables import (
    TOKEN,
    CHAT_ID_ALERTS,
    CHAT_ID_DEBUG,
)


def telegram_send_msg(
        message_text: str,
        disable_web_page_preview: bool = True,
        telegram_token: str = TOKEN,
        telegram_chat_id: str = CHAT_ID_ALERTS,
        debug: bool = False,
        timeout: float = 10,
        sleep_time: int = 3,
) -> requests.Response or None:
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
    :param sleep_time: Time to sleep if Telegram bot clutters
    :return: requests.Response
    """
    telegram_token = str(telegram_token)
    telegram_chat_id = str(telegram_chat_id)
    message_text = str(message_text)

    # if Chat ID not provided - try CHAT_ID_ALERTS or CHAT_ID_DEBUG variable from the .env file
    if debug:
        telegram_chat_id = CHAT_ID_DEBUG

    # construct url using token for a sendMessage POST request
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    # Construct data for the request
    payload = {
        "chat_id": telegram_chat_id,
        "text": message_text,
        "disable_web_page_preview": disable_web_page_preview,
        "parse_mode": "HTML"
    }

    # send the POST request
    log_telegram.info(f"Telegram Sending: {message_text}")
    try:
        counter = 1
        # If too many requests, wait for Telegram's rate limit
        while True:
            post_request = requests.post(url=url, data=payload, timeout=timeout)

            if post_request.json()['ok']:
                return post_request

            log_error.warning(f"'Telegram Message not sent, attempt {counter}. "
                              f"Sleeping {sleep_time} secs...")
            counter += 1
            sleep(sleep_time)

    except ConnectionError as ex:
        log_error.warning(f"'Telegram Message not sent: {message_text}. {ex}")
        return None
