import time
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
)

from src.synapse.common.message import telegram_send_message
from src.synapse.common.logger import (
    log_arbitrage,
    log_error,
)
from src.synapse.common.variables import (
    time_format,
    network_names,
    CHAT_ID_ALERTS,
    CHAT_ID_SPECIAL,
)


def query_synapse(
        driver: Chrome,
        amounts: list,
        min_arbitrage: float,
        src_network_name: str = "Ethereum",
        dest_network_name: str = "Optimism",
        token_name: str = "USDC",
        special_chat: dict = {},
        max_wait_time: int = 15,
) -> None:
    """
    Queries Hop Bridge and checks for arbitrage opportunity.

    :param driver: Chrome webdriver instance
    :param amounts: List of amounts to swap
    :param min_arbitrage: Minimum arbitrage to alert for
    :param src_network_name: Chain ID source
    :param dest_network_name: Chain ID destination
    :param token_name: Token code, eg. USDC
    :param max_wait_time: Maximum number of seconds to wait for driver element
    :param special_chat: Send specific info, if empty ignore
    """
    dest_network_id = network_names[dest_network_name]

    url = f"https://synapseprotocol.com/?inputCurrency={token_name}&outputCurrency={token_name}" \
          f"&outputChain={dest_network_id}"

    try:
        driver.get(url)

    except WebDriverException:
        log_error.warning(f"Error querying {url}")
        return None

    all_arbs = {}
    for amount in amounts:
        amount = float(amount)

        in_xpath = "//*[@id='root']/div[1]/div[2]/main/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[1]/div/div[2]/div/input"
        try:
            in_field = WebDriverWait(driver, max_wait_time).until(ec.element_to_be_clickable(
                (By.XPATH, in_xpath)))

        except TimeoutException:
            log_error.warning(f"ElementError {src_network_name} -> {dest_network_name}, {token_name}. "
                              f"{in_xpath} not located. ")
            return None

        # Clear the entire field
        in_field.send_keys(Keys.CONTROL + "a")
        in_field.send_keys(Keys.DELETE)
        in_field.send_keys(Keys.COMMAND + "a")
        in_field.send_keys(Keys.DELETE)
        # Fill in swap amount
        in_field.send_keys(amount)

        timeout = time.time() + 20
        out_xpath = "//*[@id='root']/div[1]/div[2]/main/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/input"
        out_xpath = "//*[@id='root']/div[1]/div[2]/main/div/div[2]/div/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/input"
        while True:
            out_field = driver.find_element(By.XPATH, out_xpath)
            received = out_field.get_attribute("value")

            if received != "" or time.time() > timeout:
                break

        try:
            received = float(received.replace(",", ""))
        except ValueError as e:
            log_error.warning(f"ReceivedError - {token_name}, {src_network_name} -> {dest_network_name} - {e}")
            return None

        # Calculate arbitrage
        arbitrage = received - amount

        timestamp = datetime.now().astimezone().strftime(time_format)
        message = f"{timestamp} - Synapse Web\n" \
                  f"Sell {amount:,} {token_name} for {received:,.2f}; {src_network_name} -> {dest_network_name}\n" \
                  f"\t-->Arbitrage: <a href='{url}'>{arbitrage:,.2f} {token_name}</a>\n"

        ter_msg = f"Sell {amount:,} {token_name} for {received:,.2f}; {src_network_name} -> {dest_network_name}\n" \
                  f"\t-->Arbitrage: {arbitrage:,.2f} {token_name}\n"

        # Record all arbs to select the highest later
        if arbitrage >= min_arbitrage:
            all_arbs[arbitrage] = [message, ter_msg, amount]

    if len(all_arbs) > 0:
        highest_arb = max(all_arbs)

        message = all_arbs[highest_arb][0]
        ter_msg = all_arbs[highest_arb][1]
        amount_in = all_arbs[highest_arb][2]

        telegram_send_message(message, telegram_chat_id=CHAT_ID_ALERTS)

        # If special chat required, send telegram msg to it
        if special_chat:
            if float(special_chat['max_swap_amount']) >= float(amount_in) and token_name.upper() in special_chat['coins']:
                telegram_send_message(message, telegram_chat_id=CHAT_ID_SPECIAL)

        log_arbitrage.info(ter_msg)
        timestamp = datetime.now().astimezone().strftime(time_format)
        print(f"{timestamp} - {ter_msg}")

    else:
        return None
