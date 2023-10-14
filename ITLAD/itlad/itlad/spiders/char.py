import scrapy
import json
import re

class CharacterSpider(scrapy.Spider):
    name = 'char'
    start_urls = ["https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=489022"]
    headers = {'User-Agent': 'Mozilla/5.0'}

    custom_settings = {
        'ROBOTSTXT_OBEY': False  # Disable robots.txt check
    }
    
    def remove_special_characters(self, text):
        return re.sub(r'[^\w\sа-яА-Я]+', '', text)

    def parse(self, response):
        data = {}

        table_rows = response.xpath('//table[@class="table table-striped table-character"]/tr')

        for row in table_rows:
            text = row.xpath('td[@class="table-character-text"]/text()').get()
            value = row.xpath('td[@class="table-character-value"]/text()').get()

            if text and value:
                text = text.replace("\u00a0", " ")
                value = self.remove_special_characters(value)  # Apply the function to the value
                data[text] = value.strip()
        
        with open('data.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4, separators=(',', ':'))
        
        json_data = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ':'))
        print(json_data)
        yield {'character_data': json_data}
