import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pandas as pd
import pdb

class PaintSpider(CrawlSpider):
    name = "paint"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    desired_categories = ["Краски и материалы специального назначения", "Краски для наружных работ", "Лаки"]
    visited_links = set()

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        
    }

    data = []
    rules = (
        Rule(
            LinkExtractor(
            restrict_xpaths='//div[@class="sections-block-level-2"]'),
             callback="parse_category",
             
             follow=False),
             LinkExtractor(restrict_xpaths='//div/div[@class="horizontal-product-item-block_3_2"]/a/@href'), callback ="parse_item_links",
    )
    
    category_dict = {}

    def parse_category(self, response):
        
        for category in self.desired_categories:
            elements = response.xpath(f'//a[contains(text(), "{category}")]')
            
            
            if category not in self.category_dict:
                self.category_dict[category] = [] 
            
            
            for element in elements:
                print(len(elements))
                link = element.xpath('@href').extract_first()

            if link not in self.category_dict[category]:
                self.visited_links.add(link)
                self.log(f"Найдена ссылка на категорию '{category}': {link}")
                self.category_dict[category].append(link)
            else:
                self.log(f"Ссылка на категорию '{category}' уже существует: {link}")
                 

                print(self.category_dict)

            
                        
        for category, links in self.category_dict.items():
            for link in links:
                if link not in self.visited_links:
                    yield response.follow(link, callback=self.parse_item_links)
                    self.visited_links.add(link)

    def parse_item_links(self, response):
        item_links = response.xpath('//div/div[@class="horizontal-product-item-block_3_2"]/a/@href').extract()
        print(item_links)
        for item_link in item_links:
            yield response.follow(item_link, callback=self.parse_item)




    def parse_item(self, response):
        item = {}
       
        item["наименование"] = response.xpath('//div[@class="block-1"]/div/h1/text()').get()
        item["цена"] = response.xpath('//div[@class="block-2-3"]/div/div/span/text()').get()
        description = response.xpath("//div[@class='block-4-5']/div[@class='block-4']/div[@class='tab-content']/div[@id='tab-description']/div[@id='block-description']").get()
        item["описание"] = self.clean_html(description).strip()
        

        ajax_url = "https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=" + response.url.split('/')[-1]

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
                item[text] = value

        self.data.append(item)

    def clean_html(self, html):
        import re
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', html)
        return cleantext

    def closed(self, reason):
        df = pd.DataFrame(self.data)
        df.to_csv('paint_data.csv', index=False)
