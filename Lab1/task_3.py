#from scrapy import cmdline
#import lxml.etree


import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from lxml import etree

class SecondSpider(CrawlSpider):
    images = []
    num_of_profucts = 0
    name = "first_spider"
    allowed_domains = ["meblium.com.ua"]
    start_urls = (
        'https://www.meblium.com.ua/myagkaya-mebel/divany',
    )
    rules = (Rule(LinkExtractor(allow=()), callback="parse", follow=False), )
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 3,
        'DEPTH_LIMIT':0
    }

    def parse(self, response):
        print('parsibf')
        for title in response.css('.product'):
            if (SecondSpider.num_of_profucts<20):
                yield {
                    'name' : title.xpath('.//span[@class="product-name"]/text()').extract_first(),
                    'url' : title.xpath('.//img[@class="img-responsive"]/@src').extract_first().replace("\n", ""),
                    'price' : title.xpath('.//span[@itemprop="price"]/text()').extract_first(),
                }
                SecondSpider.num_of_profucts += 1
            else:
                raise CloseSpider('nice')
process = CrawlerProcess(settings={
    "FEEDS": {
        "results/meblium.xml": {"format": "xml"},
    },
})

process.crawl(SecondSpider)
process.start()
