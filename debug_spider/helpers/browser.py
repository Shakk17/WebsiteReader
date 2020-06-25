import requests
from seleniumwire import webdriver

from helpers.utility import get_time


def get_firefox_profile():
    profile = webdriver.FirefoxProfile()
    # AdBlockPlus extension.
    profile.add_extension("firefox_extensions/d10d0bf8-f5b5-c8b4-a8b2-2b9879e08c5d.xpi")
    profile.set_preference("extensions.adblockplus.currentVersion", "3.8")
    # uBlock Origin extension.
    profile.add_extension("firefox_extensions/uBlock0@raymondhill.net.xpi")
    profile.set_preference("extensions.ublock0.currentVersion", "1.25.2")
    # I don't care about cookies extension.
    profile.add_extension("firefox_extensions/jid1-KKzOGWgsW3Ao4Q@jetpack.xpi")
    profile.set_preference("extensions.idontcareaboutcookies.currentVersion", "3.1.3")
    return profile


def get_firefox_options(heroku=False):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("window-size=500x1024")
    options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0")

    if heroku:
        # HEROKU
        """options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)"""
        pass
    return options


def add_headers_to_driver(driver):
    header_overrides = {
        "Accept": """text/html,application/xhtml+xml,application/xml;
                    q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9""",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7,es;q=0.6,fr;q=0.5,nl;q=0.4,sv;q=0.3",
        "Dnt": "1",
        "Referer": "https://www.google.com/",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    driver.header_overrides = header_overrides

    return driver


def get_quick_html(url):
    html = requests.get(url=url).text
    return html


def render_page(url):
    """
    This method returns the HTML code of a web page. It uses Selenium, thus it supports Javascript.
    :param url: A string containing the URL of the web page to parse.
    :return: The HTML code of the web page.
    """
    try:
        print(f"{get_time()} [SELENIUM] Page rendering started.")
        browser = webdriver.Firefox(options=get_firefox_options(), firefox_profile=get_firefox_profile())
        browser.get(url)
    except Exception:
        print(f"[SELENIUM] Can't access this website: {url}")
        raise Exception("Error while visiting the page.")

    print(f"{get_time()} [SELENIUM] Page rendering finished.")

    html_code = browser.find_element_by_tag_name("html").get_attribute("innerHTML")

    browser.close()

    return html_code
