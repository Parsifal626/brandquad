# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import pandas as pd
from scrapy.spiders import CrawlSpider

class PaintSpider(CrawlSpider):
    def __init__(self, *args, **kwargs):
        super(PaintSpider, self).__init__(*args, **kwargs)
        self.data = pd.DataFrame(columns=["category_name", "category_url", "наименование", "цена", "описание", "характеристики"])