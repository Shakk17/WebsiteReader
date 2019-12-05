import os

jar_location = r"C:\Users\shakk17\Documents\git-repo\WebsiteReader\vips-java\vips-java.jar"
url = "https://www.open.online"

command = "java -cp " + jar_location + " org.fit.vips.VipsTester " + url

os.system(command=command)
