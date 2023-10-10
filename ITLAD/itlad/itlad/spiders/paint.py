import scrapy
import time  # Импортируйте модуль time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json

class PaintSpider(CrawlSpider):
    name = "paint"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36" 

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="sections-block-level-2-item"]/a'), callback="parse_category", follow=True),
        Rule(LinkExtractor(restrict_xpaths='//div[@class="horizontal-product-item"]/div/div/a'), callback="parse_item", follow=True),
    )

    def parse_category(self, response):
        category_name = response.xpath('//h1/text()').get()
        category_url = response.url

        desired_categories = ["Краски и материалы специального назначения", "Краски для наружных работ", "Лаки"]
        if category_name in desired_categories:
            yield {
                'category_name': category_name,
                'category_url': category_url
            }

    def parse_item(self, response):
        # Извлекаем данные о товаре с основной страницы
        item = {}
        item["наименование"] = response.xpath('//div[@class="block-1"]/div/h1/text()').get()
        item["цена"] = response.xpath('//div[@class="block-2-3"]/div/div/span/text()').get()
        description = response.xpath("//div[@class='block-4-5']/div[@class='block-4']/div[@class='tab-content']/div[@id='tab-description']/div[@id='block-description']").get()
        item["описание"] = self.clean_html(description).strip()

        # Извлекаем последний элемент из URL
        last_element = response.url.split('/')[-1]

        # Создаем полный URL с параметрами для AJAX-запроса
        ajax_url = f"https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items={last_element}"

        # Отправляем GET-запрос к серверу, чтобы получить характеристики товара
        yield scrapy.Request(
            url=ajax_url,
            callback=self.parse_characteristics,
            meta={'item': item},
            headers={'User-Agent': self.user_agent}
        )

        # Добавляем задержку в 2 секунды перед следующим запросом
        time.sleep(2)

    def parse_characteristics(self, response):
        item = response.meta['item']

        # Парсим JSON-ответ и извлекаем характеристики товара
        json_response = json.loads(response.text)
        characteristics = {}
        for item_data in json_response.get("items", []):
            key = item_data.get("key")
            value = item_data.get("value")
            if key and value:
                characteristics[key] = value

        item['characteristics'] = characteristics

        yield item

    def clean_html(self, html):
        import re
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', html)
        return cleantext
