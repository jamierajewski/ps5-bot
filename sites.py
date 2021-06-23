from selenium.webdriver import Chrome

# TODO
# - Use cookie of logged in session to skip logging in?


class Site:
    '''Defines a generic interface to hold site details
    '''

    self._driver = None

    def __init__(self, chrome_driver_path):
        self._driver = Chrome(executable_path=chrome_driver_path)


class Costco(Site):
    '''costco.ca interface
    '''

    self._urls = ["https://www.costco.ca/playstation-5-console-bundle---ratchet-%2526-clank.product.100780734.html",
                  "https://www.costco.ca/playstation-5-console-bundle.product.100696941.html"
                  ]

    def __init__(self):
        super().__init__()

    def buy(self):
        '''Once on a product page, this function will attempt to purchase it
        '''
        pass

        # Add to cart - The HTML ID is:
        # "add-to-cart-btn"

        # Once added, navigate to cart (optional? Can you skip directly to checkout?)
        # https://www.costco.ca/CheckoutCartView

        # Click checkout button - HTML ID is:
        # "shopCartCheckoutSubmitButton"

        # Need to fill in CVV if already signed in

        # Shipping

        # Confirmation
