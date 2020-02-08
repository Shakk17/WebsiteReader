from scrapy import cmdline

url = "https://www.open.online/"
command = "scrapy crawl urls -s url=" + url

cmdline.execute(command.split())
