from scrapy import cmdline

url = "https://www.polimi.it/"
command = "scrapy crawl urls -s url=" + url

cmdline.execute(command.split())
