from datetime import datetime
from typing import TypeVar

from selenium.webdriver import Chrome

from src.synapse.common.message import telegram_send_message
from src.synapse.common.variables import time_format


# Define a Function type
Function = TypeVar("Function")


def exit_handler(
        program_name: str = "",
        telegram_chat_id: str = "",
        info: str = "",
) -> None:
    """
    Sends a notification message in Telegram to notify of program termination.

    :param program_name: Name of running program
    :param telegram_chat_id: Telegram Chat ID to send message to
    :param info: Additional info to include in debug message
    :returns: None
    """

    timestamp = datetime.now().astimezone().strftime(time_format)

    message = f"<b>⚠️WARNING</b> - {timestamp}\n" \
              f"<b>{program_name}</b> stopped.\n" \
              f"Please contact your administrator.\n" \
              f"{info}"

    # Send debug message in Telegram and print in terminal
    telegram_send_message(message, telegram_chat_id=telegram_chat_id, debug=True)

    print(f"{timestamp}\n{program_name} has stopped. {info}")


def exit_handler_driver(
        driver: Chrome,
        program_name: str = "",
        telegram_chat_id: str = "",
        info: str = "",
) -> None:
    """
    Sends a notification message in Telegram to notify of program termination and quits driver.

    :param driver: Web driver instance
    :param program_name: Name of running program
    :param telegram_chat_id: Telegram Chat ID to send message to
    :param info: Additional info to include in debug message
    :returns: None
    """

    timestamp = datetime.now().astimezone().strftime(time_format)

    message = f"* WARNING *\n" \
              f"{timestamp}: {program_name} has stopped.\n" \
              f"Please contact your administrator.\n" \
              f"{info}"

    # Send debug message in Telegram and print in terminal
    telegram_send_message(message, telegram_chat_id=telegram_chat_id, debug=True)

    print(message)

    # Quit chrome driver
    driver.quit()
