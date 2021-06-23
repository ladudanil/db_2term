from scrapy import cmdline
from lxml import etree

cmdline.execute("scrapy crawl xsport".split())
root = None
with open('results/xsport.xml', 'r') as file:
    root = etree.parse(file)
