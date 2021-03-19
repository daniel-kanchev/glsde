import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from glsde.items import Article


class GlsdeSpider(scrapy.Spider):
    name = 'glsde'
    start_urls = ['https://www.gls.de/privatkunden/gls-bank/aktuelles/neuigkeiten/']

    def parse(self, response):
        links = response.xpath('//a[@class="link link--default link--right"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="text__inner"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
