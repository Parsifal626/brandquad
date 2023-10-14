import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pandas as pd 

class PaintSpider(CrawlSpider):
    name = "paint"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    desired_categories = ["Краски и материалы специального назначения", "Краски для наружных работ", "Лаки"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False  # Disable robots.txt check
    }

    data = []

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="sections-block-level-2-item"]/a'), callback="parse_category", follow=True),
    )


    def parse_category(self, response):
        category_name = response.xpath('//h1/text()').get()
        category_url = response.url

        if category_name in self.desired_categories:
            category_dict = {
                'category_name': category_name,
                'category_url': category_url
            }
            #yield category_dict

            for product_url in response.xpath('//div[@class="horizontal-product-item"]/div/div/a/@href').extract():
                yield response.follow(product_url, callback=self.parse_item)

    def parse_item(self, response):
        item = {}
        item["наименование"] = response.xpath('//div[@class="block-1"]/div/h1/text()').get()
        item["цена"] = response.xpath('//div[@class="block-2-3"]/div/div/span/text()').get()
        description = response.xpath("//div[@class='block-4-5']/div[@class='block-4']/div[@class='tab-content']/div[@id='tab-description']/div[@id='block-description']").get()
        item["описание"] = self.clean_html(description).strip()
        item['характеристики'] = {}

        # Define the AJAX URL here or pass it as an argument
        ajax_url = "https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=" + response.url.split('/')[-1]

        # Extract characteristics using a Scrapy request
        yield scrapy.Request(
            ajax_url,
            callback=self.parse_characteristics,
            meta={'item': item}
        )

    def parse_characteristics(self, response):
        item = response.meta['item']
        data = response.xpath('//table[@class="table table-striped table-character"]/tr')

        for row in data:
            text = row.xpath('td[@class="table-character-text"]/text()').get()
            value = row.xpath('td[@class="table-character-value"]/text()').get()


            if text and value:
                item['характеристики'][text] = value
                

        self.data.append(item)


    def clean_html(self, html):
        import re
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', html)
        return cleantext
    
    def closed(self, reason):
        df = pd.DataFrame(self.data)

        df.to_csv('paint_data.csv', index=False)