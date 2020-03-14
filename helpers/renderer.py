import os
from time import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from databases.database_handler import Database
from helpers.utility import strip_html_tags

options = Options()
options.add_argument("--headless")
options.add_argument('window-size=500x1024')
options.add_argument("load-extension=uBlock")

# Avoid loading images.
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
# HEROKU
"""options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)"""


def render_page(url):
    """
    This method returns the HTML code of a web page. It uses Selenium, thus it supports Javascript.
    :param url: A string containing the URL of the web page to parse.
    :return: The HTML code of the web page.
    """
    start = time()
    try:
        print("Rendering page with Selenium...")
        driver.get(url)
    except Exception:
        print(f"Can't access this website: {url}")
        raise Exception("Error while visiting the page.")

    print(f"Selenium request elapsed time: {(time() - start):.2f} s")

    html_code = driver.find_element_by_tag_name("html").get_attribute("innerHTML")

    return html_code


def crawl_single_page(url):
    """
    Given a URL, it adds in the database all the links contained in that web page.
    :param url: A string containing the URL of the web page to analyse.
    :return: None.
    """
    print(f"Crawling single page [{url}] with Selenium...")
    driver.get(url)
    links = driver.find_elements(By.XPATH, '//a[@href]')
    links_bs4 = BeautifulSoup(driver.page_source, "lxml").find_all("a")
    links_bs4 = list(filter(lambda x: x.get("href") is not None, links_bs4))

    for i, link in enumerate(links):
        try:
            href = link.get_attribute("href")
            text = strip_html_tags(link.get_attribute("innerHTML"))
            x_position = str(link.location.get('x'))
            y_position = str(link.location.get('y'))
            # True if the element is contained in a list container.
            parents = [parent.name for parent in links_bs4[i].parents]
            in_list = int("li" in parents)

            # If the link links to the same page, discard it.
            hash_position = href.find("#")
            if href[:hash_position] == url or text == "" or int(y_position) == 0:
                continue
        except StaleElementReferenceException:
            continue
        # Save link in database.
        Database().insert_crawler_link(
            page_url=url, href=href, text=text, x_position=x_position, y_position=y_position, in_list=in_list)
    print("Crawling of single page terminated.")
    return
