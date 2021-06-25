# ps5-bot
A bot to buy a PS5.

This is not designed to be a scalper's best friend, but rather a way for individuals to acquire a single system in these hard times. 

Almost all web stores feature a very similar purrchasing system:
- Login page (with email, password and "submit" button)
- Product page (with an "Add to cart" button)
- View cart/checkout page (with a "place order" button)

Because of this, the design is a generic class interface for a web store, and can probably be made even more generic to the point where the only requirements in adding a new site are to fill in the XPATH's for the components.

## Current Status

Currently works for `costco.ca` as long as you have an account with your information on file. A test implementation of `bestbuy.ca` and `walmart.ca` are incorporated as well, but they have bot protections and so they don't work at the moment.

## Requirements

1. Python 3 with pip
2. Libraries (can be installed by running `python3 -m pip install -r requirements.py` in this repo, preferrably in a virtual environment)
3. Google Chrome and the [Google Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) that matches the version of Chrome you have installed (this requirement can be fixed to allow any web driver, but the code requires some changes)

## How to use

1. Clone this repo
2. Ensure the above requirements are met
3. Fill in `credentials.json` file with the corresponding credentials for the site you are trying to run
4. (Optional) Modify the `site` class attributes with custom values. The defaults are (time variables are in seconds):

```python
    _retry_stock = 1
    _retry_action_delay = 0.2
    _retry_attempts = 100
    _wait_timeout = 3
```
5. There is currently a list of product page URLs in each class as an attribute, where I chose one to run. If you would like a particular bundle/edition, add your own product page URL and make sure the code is choosing it.
6. Inside of the repo, run the Python interpreter
7. Import the `sites.py` module:

```python
import sites
```
8. Instantiate whichever site's class you want to run, passing the path to the chrome driver and the credentials file:

```python
site = sites.Costco('./chromedriver', './credentials.json')
```
9. A browser window should open up, and the bot will attempt to buy a PS5. Upon success, the bot will exit.
