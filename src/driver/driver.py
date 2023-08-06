"""
Configure Chrome settings and initiate it.
"""
from atexit import register

from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager

from src.driver.options import driver_options


# Open Chromium web driver
# chrome_driver = Chrome(ChromeDriverManager().install(), options=driver_options)
chrome_driver = Chrome(options=driver_options)

# Quit chrome driver after whole script has finished execution
register(chrome_driver.quit)
