import scrapy
import json
import re
import pandas as pd

class CharacterSpider(scrapy.Spider):
    name = 'char'

    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    desired_categories = ["Краски и материалы специального назначения", "Краски для наружных работ", "Лаки"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 2,
    }

    def remove_special_characters(self, text):
        return re.sub(r'[^\w\sа-яА-Я]+', '', text)

    def parse(self, response):
        find_categories_links = response.xpath("//div[@class='sections-block-level-2']")
        category_dict = {}

        for category in self.desired_categories:
            elements = response.xpath(f'//a[contains(text(), "{category}")]')
            link = elements.xpath('@href').extract_first()

            if category not in category_dict:
                category_dict[category] = []  # Initialize an empty list

            if link and link not in category_dict[category]:
                self.log(f"Найдена ссылка на категорию '{category}': {link}")
                category_dict[category].append(link)  # Append the link to the list
            else:
                self.log(f"Ссылка на категорию '{category}' уже существует: {link}")

        for category, links in category_dict.items():
            for link in links:
                yield response.follow(link, self.parse_item_links)

    def parse_item_links(self, response):
        item_links = response.xpath('//div/div[@class="horizontal-product-item-block_3_2"]/a/@href').extract()
        for link in item_links:
            yield response.follow(link, self.parse_item)

    def parse_item(self, response):
        item = {}

        item["наименование"] = response.xpath('//div[@class="block-1"]/div/h1/text()').get()
        item["цена"] = response.xpath('//div[@class="block-2-3"]/div/div/span/text()').get()
        description = response.xpath('//div[@id="block-description"]//text()').extract()

        item["описание"] = self.remove_special_characters(''.join(description)).strip()

        ajax_url = f"https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items={response.url.split('/')[-1]}"
        yield scrapy.Request(ajax_url, callback=self.parse_ajax_data, meta={'item': item})

    def parse_ajax_data(self, response):
        item = response.meta['item']
        item["характеристики"] = {}
        data = response.xpath('//table[@class="table table-striped table-character"]/tr')

        for row in data:
            text = row.xpath('td[@class="table-character-text"]/text()').get()
            value = row.xpath('td[@class="table-character-value"]/text()').get()

            if text and value:
                item["характеристики"][text] = value

        yield item

        # Collect the items in a list
        self.items.append(item)

    def __init__(self, *args, **kwargs):
        super(CharacterSpider, self).__init__(*args, **kwargs)
        self.items = []

    def closed(self, reason):
        # Convert the list of items to a Pandas DataFrame
        df = pd.DataFrame(self.items)

        # Save the DataFrame to a CSV file
        df.to_csv("scraped_data.csv", index=False)