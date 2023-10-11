import scrapy

class PaintSpider(scrapy.Spider):
    name = "paint"
    start_urls = ["https://order-nn.ru/kmo/catalog/"]

    def parse(self, response):
        categories = ["Краски и материалы специального назначения", "Краски для наружных работ", "Лаки"]
        category_name = response.xpath('//h1/text()').get()
        print(category_name)
        
        if category_name in categories:
            category_url = response.url
            yield {
                'category_name': category_name,
                'category_url': category_url
            }

        product_id = response.url.split('/')[-1]
        
        ajax_url = f"https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=489022"
        headers = {'User-Agent': 'Mozilla/5.0'}

        yield scrapy.Request(
            url=ajax_url,
            callback=self.parse_product,
            headers=headers,
            meta={'category_name': category_name}
        )

    def parse_product(self, response):
        category_name = response.meta['category_name']
        product_data = {
            'category_name': category_name,
            'наименование': response.xpath('//div[@class="block-1"]/div/h1/text()').get(),
            'цена': response.xpath('//div[@class="block-2-3"]/div/div/span/text()').get(),
            'описание': self.clean_html(response.xpath("//div[@class='block-4-5']/div[@class='block-4']/div[@class='tab-content']/div[@id='tab-description']/div[@id='block-description']").get())
        }

        characteristics = {}
        json_response = response.json()  # Парсим JSON напрямую из ответа
        for item_data in json_response.get("items", []):
            key = item_data.get("key")
            value = item_data.get("value")
            if key and value:
                characteristics[key] = value

        product_data['characteristics'] = characteristics
        yield product_data

    def clean_html(self, html):
        import re
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', html)
        return cleantext
