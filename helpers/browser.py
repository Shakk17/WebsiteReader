import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

from databases.handlers.crawler_links_handler import db_insert_crawler_link, db_delete_all_url_crawler_links
from helpers.printer import magenta, red
from helpers.utility import strip_html_tags, get_time, add_scheme


def get_firefox_profile():
    profile = webdriver.FirefoxProfile()
    # AdBlockPlus extension.
    profile.add_extension("firefox_extensions/{d10d0bf8-f5b5-c8b4-a8b2-2b9879e08c5d}.xpi")
    profile.set_preference("extensions.adblockplus.currentVersion", "3.8")
    # uBlock Origin extension.
    # profile.add_extension("firefox_extensions/uBlock0@raymondhill.net.xpi")
    # profile.set_preference("extensions.ublock0.currentVersion", "1.25.2")
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
    try:
        html = requests.get(url=url).text
    except Exception:
        print(red("Exception while getting SIMPLE HTML."))
        html = ""
    return html


def scrape_page(url):
    """
    Given a URL, it adds in the database all the links contained in that web page.
    :param url: A string containing the URL of the web page to analyse.
    :return: None.
    """
    print(f"{get_time()} [SELENIUM] Page rendering started.")
    browser = webdriver.Firefox(options=get_firefox_options(), firefox_profile=get_firefox_profile())
    try:
        browser.get(url)
        body = browser.page_source

        links = browser.find_elements(By.XPATH, '//a[@href]')

        links_bs4 = BeautifulSoup(body, "lxml").find_all("a")
        links_bs4 = list(filter(lambda x: x.get("href") is not None, links_bs4))

        # Delete all the old crawler links of the page.
        db_delete_all_url_crawler_links(url=url)

        for i, link in enumerate(links):
            try:
                href = add_scheme(link.get_attribute("href"))
                text = strip_html_tags(link.get_attribute("innerHTML"))
                x_position = str(link.location.get('x'))
                y_position = str(link.location.get('y'))
                # True if the element is contained in a list container.
                parents = [parent.name for parent in links_bs4[i].parents]
                in_list = int("li" in parents)

                # Skip PDF files.
                if href[-3:] in ["pdf", "jpg", "png"]:
                    continue

                # If the link links to the same page, discard it.
                hash_position = href.find("/#")
                if href[:hash_position] == url or len(text) == 0:
                    continue

            except StaleElementReferenceException:
                continue
            # Update link in database.
            db_insert_crawler_link(
                page_url=url, link_url=href, link_text=text,
                x_position=x_position, y_position=y_position, in_list=in_list)

    except Exception as e:
        print(magenta(f"[SELENIUM] Can't access this website: {url}"))
        body = ""

    print(f"{get_time()} [SELENIUM] Page rendering finished.")
    browser.close()
    return body
