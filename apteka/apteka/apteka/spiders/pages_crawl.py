import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import re



t = time.time()
local = time.localtime(t)


class PagesCrawlSpider(CrawlSpider):
    name = "pages_crawl"
    allowed_domains = ["maksavit.ru"]
    start_urls = ["https://maksavit.ru/novosibirsk/catalog/materinstvo_i_detstvo/detskaya_gigiena/"]



    # download_delay = 2

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="product-card-block"]/div[@class="product-top"]/a'), callback="parse_item"),
        Rule(LinkExtractor(restrict_xpaths=("//ul[@class='ui-pagination']/li/a")), callback='parse_next_page', follow=True)
    )


    def parse_item(self, response):
        current_url = response.url
        item = {}
        item['timestamp'] = time.asctime(local)
        item['RPC'] = current_url.split('/')[-2]

        item['url'] = []
        item['url'].append(current_url)

        item['title'] = response.xpath("//h1[contains(@class, 'product-top__title')]/text()").get()
        item['marketing_tags'] = response.xpath("//div[contains(@class, 'badge-discount badge-discount_price-reduced')]/text()").get()
        item['brand'] = response.xpath("//div[@class='product-info__brand']/div/a[contains(@class, 'product-info__brand-value')]/text()").get()
        
        
        breadcrumbs = response.xpath('//ul[@class="breadcrumbs"]//span/text()').getall()
        cleaned_breadcrumbs = [breadcrumb.strip() for breadcrumb in breadcrumbs if breadcrumb.strip()]
        item['section'] = {}
        item['section'] = cleaned_breadcrumbs[2:-1]

        
        item["price_data"] = {}

        original_price_element = response.xpath('//div[@class="price-box__old-price"]/text()').get()
        current_price_element = response.xpath('//span[@class="price-value"]/text()').get()

        original_price_numbers = re.findall(r'\d+\.\d+|\d+', original_price_element) if original_price_element else []
        current_price_numbers = re.findall(r'\d+\.\d+|\d+', current_price_element) if current_price_element else []

        item["price_data"]["original"] = float(original_price_numbers[0]) if original_price_numbers else None
        item["price_data"]["current"] = float(current_price_numbers[0]) if current_price_numbers else None

        item["price_data"]["sale_tag"] = None

        if item["price_data"]["original"] is not None and item["price_data"]["current"] is not None:
            discount = f'Скидка {round((item["price_data"]["original"] - item["price_data"]["current"]) / item["price_data"]["original"] * 100, 2)}%'
            item["price_data"]["sale_tag"] = discount
        
        item["stock"] = {}

        available = response.xpath('//a[@class="offers-table__drugstore-link"]/text()').get()
        if available:
            item["stock"]['in_stock'] = True
            item["stock"]['count'] = len(available)
        else:
            item["stock"]['in_stock'] = False
            item["stock"]['count'] = 0

        item['assets'] = {}

        item['assets']["main_image"] = response.xpath("//div[@class='product-picture']/img/@src").get()
        item['assets']["set_image"] = response.xpath("//div[@class='product-picture']/img/@src").getall()

        item['metadata'] = {}
        meta = response.xpath("//div[@class='product-instruction']//text()").extract()
        search = "Описание" 
        if search in meta:
            index = meta.index(search)
            description = meta[index+1]
                       
            item['metadata']['__description'] = description

        
        fields = response.xpath("//h3[@class='desc']")

        for field in fields:
            header = field.xpath("text()").get()

            text_element = field.xpath("following-sibling::text()").extract()
            text_element = [text.strip() for text in text_element if text.strip()]
            if header and text_element:
                item['metadata'][header] = text_element

        item['variants'] = 1

        yield item

    def parse_next_page(self, response):
        page_links = response.xpath('//ul[@class="ui-pagination"]/li/a/@href').extract()

        for page_link in page_links:
            yield scrapy.Request(response.urljoin(page_link), callback=self.parse_item)




