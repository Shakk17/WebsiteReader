import time
from selenium import webdriver


def save_screenshot(url):
    start = time.time()
    options = webdriver.ChromeOptions()
    options.headless = True

    with webdriver.Chrome(options=options)as driver:
        driver.get(url)

        S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
        driver.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
        driver.find_element_by_tag_name('body').screenshot('web_screenshot.png')

    print("Time elapsed: %.2f" % (time.time() - start))


save_screenshot("https://www.open.online")
