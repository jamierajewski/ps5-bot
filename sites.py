from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException
import sys
import json
import time


class Site:
    '''Defines a generic interface to hold site details
    '''

    _retry_stock = 2
    _retry_action_delay = 0.2
    _retry_attempts = 100

    def __init__(self, driver_path, credentials):

        try:
            with open(credentials, "r") as json_file:
                self._credentials = json.load(json_file)
        except FileNotFoundError:
            sys.exit("Invalid credentials file at: {}".format(credentials))
        except json.decoder.JSONDecodeError:
            sys.exit("Unable to load {} as JSON".format(credentials))

        try:
            self._driver = Chrome(executable_path=driver_path)
        except WebDriverException:
            sys.exit("Invalid path to Chrome driver: {}".format(driver_path))

    def try_action(func):
        '''Wrapper to attempt a given action the predefined number of times
        '''

        def retry(self, *args, **kwargs):

            for attempt in range(1, self._retry_attempts+1):
                print("Attempt {}".format(attempt))
                if func(self, *args, **kwargs):
                    break
                time.sleep(self._retry_action_delay)

            if attempt > self._retry_attempts:
                print("{} attempts reached, giving up".format(
                    self._retry_attempts))
                return False

            return True

        return retry

    @try_action
    def clickButton(self, button_xpath):
        try:
            self._driver.find_element_by_xpath(button_xpath).click()
            return True
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not click element {}".format(button_xpath))
            return False

    @try_action
    def inputText(self, textbox_xpath, text):
        try:
            self._driver.find_element_by_xpath(textbox_xpath).send_keys(text)
            return True
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not send keys to element {}".format(textbox_xpath))
            return False

    def findText(self, text_xpath, text):
        '''Don't decorate this, as we want to react differently to the
        text being there or not
        '''
        try:
            element_text = self._driver.find_element_by_xpath(text_xpath).text
            print("element text: [{}]".format(element_text))
            if element_text == text:
                print("Text: {}, element_text: {}, returning true".format(
                    text, element_text))
                return True
            return False
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not find text at element {}".format(text_xpath))
            return False


class Costco(Site):
    '''costco.ca interface
    '''

    _product_urls = ["https://www.costco.ca/playstation-5-console-bundle---ratchet-%2526-clank.product.100780734.html",
                     "https://www.costco.ca/playstation-5-console-bundle.product.100696941.html"
                     ]

    # HTML xpaths for elements

    # Language/territory modal
    _modal_submit = '//*[@id="language-region-set"]'

    # Login form
    _login_url = 'https://www.costco.ca/LogonForm'
    _login_email = '//*[@id="logonId"]'
    _login_password = '//*[@id="logonPassword"]'
    _login_submit = '/html/body/div[8]/div[3]/div/div/div/div/form/fieldset/div[6]/input'

    # Product page
    _product_add_to_cart = '//*[@id="add-to-cart-btn"]'

    def __init__(self, driver_path, credentials):
        super().__init__(driver_path, credentials)
        self._credentials = self._credentials["costco"]
        self.login()
        self.monitor_stock(self._product_urls[0])

    def login(self):
        '''Self-explanatory
        '''
        self._driver.get(self._login_url)

        self.clickButton(self._modal_submit)

        # Delete the language/territory modal to speed up
        # self._driver.execute_script("""
        # var modal = document.evaluate('/html/body/div[10]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        # modal.parentNode.removeChild(modal);
        # modal = document.evaluate('/html/body/div[10]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        # modal.parentNode.removeChild(modal);
        # """)

        self.inputText(self._login_email,
                       self._credentials["email"])

        self.inputText(self._login_password,
                       self._credentials["password"])

        self.clickButton(self._login_submit)

    def monitor_stock(self, product_url):
        '''Continually monitor page until product is in stock
        '''
        self._driver.get(product_url)

        while True:
            # If out of stock, wait _retry_stock-seconds and reload page, try again
            if self.findText(self._product_add_to_cart, "Add to Cart"):
                print("In stock!")
                break
            else:
                print("OOS - Retrying in {}s".format(self._retry_stock))
                time.sleep(self._retry_stock)
                self._driver.refresh()

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''
        pass

        # Once added, navigate to cart (optional? Can you skip directly to checkout?)
        # https://www.costco.ca/CheckoutCartView

        # Click checkout button - HTML ID is:
        # "shopCartCheckoutSubmitButton"

        # Need to fill in CVV if already signed in

        # Shipping

        # Confirmation
