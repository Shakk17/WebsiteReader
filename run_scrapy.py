from scrapy import cmdline

url = "https://www.polimi.it/"
command = "scrapy crawl urls --nolog -s url=" + url

cmdline.execute(command.split())
