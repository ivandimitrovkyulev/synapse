from datetime import datetime
from typing import TypeVar

from selenium.webdriver import Chrome

from src.common.message import telegram_send_msg
from src.variables import time_format


# Define a Function type
Function = TypeVar("Function")


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
    telegram_send_msg(message, telegram_chat_id=telegram_chat_id, debug=True)

    print(message)

    # Quit chrome driver
    driver.quit()
