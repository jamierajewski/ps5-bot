from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException
import sys
import json
import time


class Site:
    '''Defines a generic interface to hold site details
    '''

    _retry_delay = 0.2
    _retry_attempts = 100

    def __init__(self, chrome_driver_path, credentials):

        try:
            with open(credentials, "r") as json_file:
                self._credentials = json.load(json_file)
        except FileNotFoundError:
            sys.exit("Invalid credentials file at: {}".format(credentials))
        except json.decoder.JSONDecodeError:
            sys.exit("Unable to load {} as JSON".format(credentials))

        try:
            self._driver = Chrome(executable_path=chrome_driver_path)
        except WebDriverException:
            sys.exit("Invalid path to Chrome driver: {}".format(
                chrome_driver_path))

    def clickButton(self, button_xpath, attempt):
        try:
            self._driver.find_element_by_xpath(button_xpath).click()
            return True
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not click element {} - Attempt {}".format(button_xpath, attempt))
            return False

    def inputText(self, textbox_xpath, text, attempt):
        try:
            self._driver.find_element_by_xpath(textbox_xpath).send_keys(text)
            return True
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print(
                "Could not send keys to element {} - Attempt {}".format(textbox_xpath, attempt))
            return False


class Costco(Site):
    '''costco.ca interface
    '''

    _product_urls = ["https://www.costco.ca/playstation-5-console-bundle---ratchet-%2526-clank.product.100780734.html",
                     "https://www.costco.ca/playstation-5-console-bundle.product.100696941.html"
                     ]

    # HTML xpaths for elements

    # Login form
    _login_email = '//*[@id="logonId"]'
    _login_password = '//*[@id="logonPassword"]'
    _login_submit = '/html/body/div[8]/div[3]/div/div/div/div/form/fieldset/div[6]/input'

    # Product page

    def __init__(self):
        super().__init__()
        self._credentials = self._credentials["costco"]

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''

        # Login
        self._driver.get("https://www.costco.ca/LogonForm")

        # Add to cart - The HTML ID is:
        # "add-to-cart-btn"

        # Once added, navigate to cart (optional? Can you skip directly to checkout?)
        # https://www.costco.ca/CheckoutCartView

        # Click checkout button - HTML ID is:
        # "shopCartCheckoutSubmitButton"

        # Need to fill in CVV if already signed in

        # Shipping

        # Confirmation
