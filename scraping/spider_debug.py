from scrapy import cmdline

url = "https://floriandaniel.it/"
command = f"scrapy crawl links -s url={url}"

cmdline.execute(command.split())