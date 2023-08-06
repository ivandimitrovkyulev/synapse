"""
Configure Chrome settings and initiate it.
"""
import os
from dotenv import load_dotenv

from selenium.webdriver.chrome.options import Options


load_dotenv()
# Get env variables
CHROME_LOCATION = os.getenv('CHROME_LOCATION')

# Chrome driver options
driver_options = Options()
driver_options.add_argument("--window-size=1920,1080")
driver_options.add_argument("--start-maximized")
driver_options.add_argument('--headless')
driver_options.add_argument('--no-sandbox')
driver_options.add_argument('--disable-gpu')
driver_options.add_argument('--disable-dev-shm-usage')
