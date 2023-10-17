import scrapy
import json
import re

class CharacterSpider(scrapy.Spider):
    name = 'char'

    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    # start_urls = ["https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=489022"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    desired_categories = ["Краски и материалы специального назначения", "Краски для наружных работ", "Лаки"]    

    custom_settings = {
        'ROBOTSTXT_OBEY': False  
    }
    
    def remove_special_characters(self, text):
        return re.sub(r'[^\w\sа-яА-Я]+', '', text)

    def parse(self, response):
        find_categories_links = response.xpath("//div[@class='sections-block-level-2']")
        category_dict = {}

        for category in self.desired_categories:
            elements = find_categories_links(f'//a[contains(text(), "{category}")]')

            if category not in category_dict:
                category_dict[category] = []

            for element in elements:
                print(len(elements))
                link = element.xpath('@href').extract_first()

            if link not in category_dict[category]:
                self.log(f"Найдена ссылка на категорию '{category}': {link}")
                category_dict[category].append(link)
            else:
                self.log(f"Ссылка на категорию '{category}' уже существует: {link}")

                print(self.category_dict)

        for category, links in category_dict.items():
            for link in links:
                yield response.follow(link, self.parse_item_links)

    def parse_item_links(self, response):
        item_links = response.xpath('//div/div[@class="horizontal-product-item-block_3_2"]/a/@href').extract()
        print(item_links)
        for link in item_links:
            yield response.follow(link, self.parse_item)
        

    def parse_item(self, response):
        item = {}
        
        item["наименование"] = response.xpath('//div[@class="block-1"]/div/h1/text()').get()
        item["цена"] = response.xpath('//div[@class="block-2-3"]/div/div/span/text()').get()
        description = response.xpath("//div[@class='block-4-5']/div[@class='block-4']/div[@class='tab-content']/div[@id='tab-description']/div[@id='block-description']").get()
        item["описание"] = self.clean_html(description).strip()
        
        ajax_url = ("https://order-nn.ru/local/ajax/kmo/getCharacterItems.php?type=character&style=element&items=" + response.url.split('/')[-1]).extract()
        data = ajax_url.xpath('//table[@class="table table-striped table-character"]/tr')

        for row in data:
            
            text = row.xpath('td[@class="table-character-text"]/text()').get()
            value = row.xpath('td[@class="table-character-value"]/text()').get()

            if text and value:
                item[text] = value

        yield item



        # yield response.follow()

        # data = []


        # table_rows = response.xpath('//table[@class="table table-striped table-character"]/tr')

        # for row in table_rows:
        #     text = row.xpath('td[@class="table-character-text"]/text()').get()
        #     value = row.xpath('td[@class="table-character-value"]/text()').get()

        #     if text and value:
        #         text = text.replace("\u00a0", " ")
        #         value = self.remove_special_characters(value)  # Apply the function to the value
        #         data[text] = value.strip()
        
        # with open('data.json', 'w', encoding='utf-8') as json_file:
        #     json.dump(data, json_file, ensure_ascii=False, indent=4, separators=(',', ':'))
        
        # json_data = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ':'))
        # print(json_data)
        # yield {'character_data': json_data}
