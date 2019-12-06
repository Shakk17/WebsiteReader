import os


class VipsSegmentation:
    def __init__(self, url):
        self.jar_location = r"C:\Users\shakk17\Documents\git-repo\WebsiteReader\vips-java\vips-java.jar"
        self.url = url

    def start(self):
        print("Starting VIPS segmentation of %s ..." % self.url)
        command = "java -cp " + self.jar_location + " org.fit.vips.VipsTester " + self.url
        os.system(command=command)
