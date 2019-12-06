import time
from selenium import webdriver

from PIL import Image, ImageDraw, ImageFont

from lxml import etree

from vips_segmentation import VipsSegmentation


def draw_rectangle(element):
    id_box = element.get("ID")
    print("Drawing box %s" % id_box)

    # Get level of box to be drawn.
    level = id_box.count('-')

    if level < 1:
        return

    # Get shape of box to draw.
    x = int(element.get("ObjectRectLeft"))
    y = int(element.get("ObjectRectTop"))
    width = int(element.get("ObjectRectWidth"))
    height = int(element.get("ObjectRectHeight"))

    im = Image.open("web_screenshot.png")

    final_x = x + width
    final_y = y + height

    draw = ImageDraw.Draw(im)
    draw.rectangle([(x, y), (final_x, final_y)], outline=(255, (level - 1) * 100, 0), width=6 - level)
    draw.text([(x + width / 2), (y + height / 2)], id_box, fill=(0, 0, 255), font=ImageFont.truetype("arial.ttf", 24))

    content = element.get("Content")
    if content is not None:
        draw.text([(x + width / 2), (y + height / 2 + 30)], element.get("Content"), fill=(0, 0, 255), font=ImageFont.truetype("arial.ttf", 24))
    del draw

    im.save("web_screenshot.png", "PNG")


def draw_boxes():
    tree = etree.parse('VIPSResult.xml')

    for child in tree.getroot()[0].iter("*"):
        draw_rectangle(child)


class PageRenderer:
    def __init__(self, url):
        self.url = url

    def save_screenshot(self):
        print('*' * 40)
        print("Saving screenshot ...")
        start = time.time()
        options = webdriver.ChromeOptions()
        options.headless = True

        with webdriver.Chrome(options=options)as driver:
            driver.get(self.url)

            S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
            driver.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
            driver.find_element_by_tag_name('body').screenshot('web_screenshot.png')

        print("Time elapsed: %.2f sec" % (time.time() - start))

    def start(self):
        # Start VIPS segmentation on web page.
        vips_segmentation = VipsSegmentation(self.url)
        vips_segmentation.start()

        # Save screenshot of the web page.
        self.save_screenshot()

        # Draw boxes on screenshot.
        draw_boxes()


page_renderer = PageRenderer("https://www.google.com")
page_renderer.start()
