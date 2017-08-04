# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    
    product_url = scrapy.Field()
    store_keeping_unit = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    #locale = scrapy.Field()
    currency = scrapy.Field()
    variations = scrapy.Field()


class VariationItem(scrapy.Item):

    display_color_name = scrapy.Field()
    image_urls = scrapy.Field()
