import scrapy


class XSportSpider(scrapy.Spider):
    name = "xsport"
    custom_settings = {
        'ITEM_PIPELINES': {
            'lab1.pipelines.XSportPipeline': 300,
        }
    }
    fields = {
        'img': '//img/@src',
        'text': '//*[not(self::script)]/text()',
        'link': '//a/@href'
    }
    start_urls = [
        'https://xsport.ua'
    ]
    allowed_domains = [
        'xsport.ua'
    ]

    def parse(self, response):
        text = filter(isNotEmptyString,
                      map(lambda str: str.strip(),
                          [text.extract() for text in response.xpath(self.fields["text"])]))
        images = map(lambda url: ((response.url + url) if url.startswith('/') else url),
                     [img_url.extract() for img_url in response.xpath(self.fields["img"])])
        yield {
            'text': text,
            'images': images,
            'url': response.url
        }
        for link_url in response.xpath(self.fields['link']):
            yield response.follow(link_url.extract(), callback=self.parse)


def isNotEmptyString(str):
    return len(str) > 0

