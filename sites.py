from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException
import sys
import json


class Site:
    '''Defines a generic interface to hold site details
    '''

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


class Costco(Site):
    '''costco.ca interface
    '''

    _product_urls = ["https://www.costco.ca/playstation-5-console-bundle---ratchet-%2526-clank.product.100780734.html",
                     "https://www.costco.ca/playstation-5-console-bundle.product.100696941.html"
                     ]

    def __init__(self):
        super().__init__()

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''
        pass

        # Login
        self._driver.get("https://www.costco.ca/LogonForm")
        # Email textbox:
        # //*[@id="logonId"]
        # Password textbox:
        # //*[@id="logonPassword"]
        # Submit button:
        # /html/body/div[8]/div[3]/div/div/div/div/form/fieldset/div[6]/input

        # Add to cart - The HTML ID is:
        # "add-to-cart-btn"

        # Once added, navigate to cart (optional? Can you skip directly to checkout?)
        # https://www.costco.ca/CheckoutCartView

        # Click checkout button - HTML ID is:
        # "shopCartCheckoutSubmitButton"

        # Need to fill in CVV if already signed in

        # Shipping

        # Confirmation
