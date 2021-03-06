from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent, FakeUserAgentError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import json
import time


class Site:
    '''Defines a generic interface to hold site details
    '''

    _retry_stock = 1
    _wait_timeout = 3

    def __init__(self, driver_path, credentials):
        self._driver_path = driver_path

        try:
            with open(credentials, "r") as json_file:
                self._credentials = json.load(json_file)
        except FileNotFoundError:
            sys.exit("Invalid credentials file at: {}".format(credentials))
        except json.decoder.JSONDecodeError:
            sys.exit("Unable to load {} as JSON".format(credentials))

        # Pick a random UserAgent
        # Source: https://stackoverflow.com/a/49565254
        self._options = Options()
        # Contacting the primary server seems to continually fail, so catch the exception
        # and move on
        try:
            ua = UserAgent()
        except FakeUserAgentError:
            pass
        userAgent = ua.random
        
        self._options.add_argument("user-agent={}".format(userAgent))

    def launch(self, product_url: str):
        if product_url is not None:
            self._product_urls.insert(0, product_url)

        try:
            self._driver = Chrome(executable_path=self._driver_path,
                                  options=self._options)
        except WebDriverException:
            sys.exit("Invalid path to Chrome driver: {}".format(self._driver_path))

        if type(self) == Site:
            raise Exception("Cannot execute using Site baseclass")

        self.execute()


    def clickButton(self, button_xpath):
        try:
            # Wait for element to show up before retrieving text
            # Source: https://stackoverflow.com/a/65861880
            WebDriverWait(self._driver, self._wait_timeout).until(
                EC.visibility_of_element_located((By.XPATH, button_xpath))).click()
            return True
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not click element {}".format(button_xpath))
            return False

    def inputText(self, textbox_xpath, text):
        try:
            WebDriverWait(self._driver, self._wait_timeout).until(
                EC.visibility_of_element_located((By.XPATH, textbox_xpath))).send_keys(text)
            return True
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not send keys to element {}".format(textbox_xpath))
            return False

    def findText(self, text_xpath, text):
        try:
            element_text = WebDriverWait(self._driver, self._wait_timeout).until(
                EC.visibility_of_element_located((By.XPATH, text_xpath))).get_attribute("value")
            if element_text == text:
                return True
            return False
        # Numerous exceptions could occur here so catch, print and move on
        except:
            print("Could not find text at element {}".format(text_xpath))
            return False

    def send_email(self, body):
        '''Source:
        https://www.tutorialspoint.com/send-mail-from-your-gmail-account-using-python
        '''

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = self._credentials["notifications"]["sender_email"]
        message['To'] = self._credentials["notifications"]["recipient_email"]
        message['Subject'] = "PS5 Bot - Order Confirmation"
        message.attach(MIMEText(body, 'plain'))
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(self._credentials["notifications"]["sender_email"],
                      self._credentials["notifications"]["sender_password"])
        text = message.as_string()
        try:
            session.sendmail(self._credentials["notifications"]["sender_email"],
                             self._credentials["notifications"]["recipient_email"],
                             text)
            print("Email confirmation sent")
        except smtplib.SMTPException:
            # No point in exiting the program here since it ends after this anyways
            print("Failed to send email confirmation")
        finally:
            session.quit()

    def enter_credentials(self):
        '''
        Enter login credentials
        '''

        if not self.inputText(self._login_email, self._site_credentials["email"]):
            self.send_email("Failed to enter email at login")

        if not self.inputText(self._login_password, self._site_credentials["password"]):
            self.send_email("Failed to enter password at login")

    def login(self):

        self._driver.get(self._login_url)

        self.enter_credentials()

        if not self.clickButton(self._login_submit):
            self.send_email("Failed to click login button")

    def monitor_stock(self, product_url):
        '''Continually monitor page until product is in stock
        '''
        self._driver.get(product_url)

        while True:
            # If out of stock, wait _retry_stock-seconds and reload page, try again
            if self.findText(self._product_add_to_cart, "Add to cart"):
                # DEBUG
                self.send_email(
                    "Product actually in stock, attempting to buy!")
                print("In stock!")
                break
            else:
                print("OOS - Retrying in {}s".format(self._retry_stock))
                time.sleep(self._retry_stock)
                self._driver.refresh()

    def execute(self):
        self._site_credentials = self._credentials[self._site_name]
        self.login()
        self.monitor_stock(self._product_urls[0])
        # Implemented in each child class
        self.buy()
        self._driver.quit()


class Costco(Site):
    '''costco.ca interface
    '''

    _product_urls = ["https://www.costco.ca/playstation-5-console-bundle---ratchet-%2526-clank.product.100780734.html",
                     "https://www.costco.ca/playstation-5-console-bundle.product.100696941.html"
                     ]

    # Language/territory modal
    _modal_submit = '//*[@id="language-region-set"]'

    # Login form
    _login_url = 'https://www.costco.ca/LogonForm'
    _login_email = '//*[@id="logonId"]'
    _login_password = '//*[@id="logonPassword"]'
    _login_submit = '/html/body/div[8]/div[3]/div/div/div/div/form/fieldset/div[6]/input'

    # Product page
    _product_add_to_cart = '//*[@id="add-to-cart-btn"]'

    # Shopping cart
    _shopping_cart_url = 'https://www.costco.ca/CheckoutCartView'

    # Checkout page
    _checkout_cvv = '//*[@id="securityCode"]'

    _site_name = "costco"

    def __init__(self, driver_path, credentials):
        super().__init__(driver_path, credentials)

    def login(self):
        '''
        Self-explanatory

        Override base method because of the extra button click
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

        self.enter_credentials()

        self.clickButton(self._login_submit)

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''
        self.clickButton(self._product_add_to_cart)

        # Once added, navigate to cart
        self._driver.get(self._shopping_cart_url)

        # Skip waiting for the button to appear and just trigger the onClick function directly
        self._driver.execute_script(
            "COSTCO.OrderSummaryCart.submitCart('https://www.costco.ca/ManageShoppingCartCmd?actionType=checkout');")

        # Need to fill in CVV since everything else is filled in
        self.inputText(self._checkout_cvv, self._site_credentials["cvv"])

        # Continue to shipping options
        self._driver.execute_script(
            "COSTCO.OrderSummary.checkoutSteps.submitCheckoutStep(2);")

        # Place order
        self._driver.execute_script(
            "COSTCO.OrderSummary.checkoutSteps.submitCheckoutStep(3);")

        self.send_email("""This is an automated confirmation that the product at {} was purchased successfully.
        
        Please verify that the product was indeed purchased successfully; if not, please submit an issue on the repo.
        """)


class Walmart(Site):
    '''walmart.ca interface
    '''

    _product_urls = ["https://www.walmart.ca/en/ip/playstation-5-console-plus-extra-dualsense-wireless-controller-midnight-black-ratchet-clank-rift-apart-playstation-5/6000194255691",
                     "https://www.walmart.ca/en/ip/playstation5-console-plus-playstation5-dualsense-wireless-controller-and-ratchet-clank-rift-apart-playstation-5/6000195165106",
                     "https://www.walmart.ca/en/ip/playstation5-console/6000202198562",
                     "https://www.walmart.ca/en/ip/playstation-5-console-plus-extra-dualsense-wireless-controller/6000201790922"]

    # Login form
    _login_url = 'https://www.walmart.ca/sign-in?from=%2Fen'
    _login_email = '//*[@id="username"]'
    _login_password = '//*[@id="password"]'
    _login_submit = '//*[@id="login-form"]/div/div[7]/button'

    # Product page
    _product_add_to_cart = '/html/body/div[1]/div/div[4]/div/div/div[1]/div[3]/div[2]/div/div[2]/div[2]/div/button[1]'

    # Age confirmation modal
    _age_modal_submit = '//*[@id="modal-root"]/div/div/div[1]/div/div[1]/div/button[2]'

    # Checkout confirmation
    _checkout_submit = '//*[@id="atc-root"]/div[3]/div[2]/button[1]'

    _site_name = "walmart"

    # Checkout... second confirmation
    #_proceed_to_checkout = '/html/body/div/div/div/div[3]/div[4]/div[3]/div/div[1]/div[11]/div/a/button'

    # Confirm shipping
    #_confirm_shipping = '//*[@id="step2"]/div[2]/div[2]/div/div/div[2]/div[3]/div/div[2]/button'

    # Place order
    #_place_order = '/html/body/div[1]/div/div/div[1]/div[1]/div[4]/div/div/div/button'

    def __init__(self, driver_path, credentials):
        super().__init__(driver_path, credentials)

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''
        self.clickButton(self._product_add_to_cart)

        # Pass the age confirmation
        self.clickButton(self._age_modal_submit)

        # Submit to checkout
        self.clickButton(self._checkout_submit)

        # Place order
        # self.clickButton(self._place_order)

        # Confirmation


class Bestbuy(Site):
    '''bestbuy.ca interface
    '''

    _product_urls = []

    # Login form
    _login_url = 'https://www.bestbuy.ca/identity/en-ca/signin?tid=j0Q%252F5pUU%252BafVGaOL0JNn47xtEAhyHADGHetaxhNp1%252BXXl0GUAOGx%252B1USSVgW1yQx1DRPTyRyRD2SbR%252FxOfUQhueRHVoB2QN%252B6XO1E%252BHmd7vKxDjD0E%252F03jrsoEVUZZu%252BO7RVx5AYAVnTNxTDBFdeE7kIp307q4UY1qRvW3uHHo6IJImQxQujXQrIuwYmQL0w%252BavDkSLCoEbHfuUhoGlwTZqs8e7WcxvFDZ%252BXqn5jUCEka0Av8lfyWKvqWJmWq8zlWVcmuA1lYkhacwfn0iRGfv%252B6msL7Myryxr05S7ysTZx3Dd1tioK0ZVNI6HASVAei'
    _login_email = '//*[@id="username"]'
    _login_password = '//*[@id="password"]'
    _login_submit = '//*[@id="signIn"]/div/button'

    _site_name = "bestbuy"

    # Product page
    #_product_add_to_cart = '/html/body/div[1]/div/div[4]/div/div/div[1]/div[3]/div[2]/div/div[2]/div[2]/div/button[1]'

    # Age confirmation modal
    #_age_modal_submit = '//*[@id="modal-root"]/div/div/div[1]/div/div[1]/div/button[2]'

    # Checkout confirmation
    #_checkout_submit = '//*[@id="atc-root"]/div[3]/div[2]/button[1]'

    # Checkout... second confirmation
    #_proceed_to_checkout = '/html/body/div/div/div/div[3]/div[4]/div[3]/div/div[1]/div[11]/div/a/button'

    # Confirm shipping
    #_confirm_shipping = '//*[@id="step2"]/div[2]/div[2]/div/div/div[2]/div[3]/div/div[2]/button'

    # Place order
    #_place_order = '/html/body/div[1]/div/div/div[1]/div[1]/div[4]/div/div/div/button'

    def __init__(self, driver_path, credentials):
        super().__init__(driver_path, credentials)

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''
        self.clickButton(self._product_add_to_cart)

        # Submit to checkout
        self.clickButton(self._checkout_submit)

        # Place order
        # self.clickButton(self._place_order)

        # Confirmation
