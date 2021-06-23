# Scrapy settings for lab1 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'lab1'

SPIDER_MODULES = ['lab1.spiders']
NEWSPIDER_MODULE = 'lab1.spiders'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 16
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.closespider.CloseSpider': 100,
    "scrapy.extensions.logstats.LogStats": None,
    "scrapy.extensions.memusage.MemoryUsage": None,
    "scrapy.extensions.corestats.CoreStats": None
}

CLOSESPIDER_PAGECOUNT = 20
ROBOTSTXT_OBEY = False
