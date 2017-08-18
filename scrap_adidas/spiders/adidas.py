import scrapy
import logging
import re
import json
from scrapy.utils.log import configure_logging
from scrap_adidas.items import ProductItem, VariationItem, SizeItem
from copy import deepcopy

class AdidasSpider(scrapy.Spider):
    
    name= "adidas"
    start_urls = [ 
        'https://shop.adidas.co.id', 
    ]
    
    custom_settings = {
        'LOG_STDOUT': True,
    }
    configure_logging(settings=None, install_root_handler=True)
    
    def parse(self, response):
        url= response.xpath("//li[@class='level0 nav-5 last parent']/a/@href").extract_first()
        yield scrapy.Request(url, callback= self.parse_product_pages)
            
    def parse_product_pages(self, response):
        product_urls = response.xpath('//h2[@class="product-name"]/a/@href').extract()
        for url in product_urls:
            yield scrapy.Request(url, callback= self.parse_product_info)
            
        next_page_url = response.xpath('//li[@class="next-page"]/a/@href').extract_first()
        if next_page_url is not None:
            yield response.follow(next_page_url, callback= self.parse_product_pages)
            
    def parse_product_info(self,response):
        prod_item = ProductItem()
        prod_item['product_url'] = response.url
        prod_item['store_keeping_unit'] = response.xpath('//span[@class="article-number"]/text()').extract_first().strip(')').strip('(')
        prod_item['title'] = response.xpath('//div[@class="product-name hidden-sm hidden-xs"]/span/text()').extract_first()
        prod_item['brand'] = response.xpath('//div[@class="product-brand hidden-sm hidden-xs"]/p/text()').extract_first().strip()
        prod_item['description'] = response.xpath('//div[@class="product-description"]/ul/li/text()').extract()
        prod_item['price'] = response.xpath("//div[@class='sibling-product']//li/a/@data-priceformatted").extract_first()
        prod_item['currency'] = re.search(r'^[a-zA-z]{2}', prod_item['price']).group(0)
        colors = response.xpath("//div[@class='sibling-product']//li/a/@data-coloroption").extract()
        colors_dup = set(colors)
        prod_item['variations'] = dict.fromkeys(colors_dup, None)
        color = response.xpath("//div[@class='sibling-product']//li[@class='active']/a/@data-coloroption").extract_first()
        var_item = VariationItem()
        var_item['display_color_name'] = color
        var_item['image_urls']= response.xpath("//div[@class='more-views vertical-slider']//img/@src").extract()
        var_item['size'] = list()
        sizes = response.xpath("//div[@class='sibling-product']//li[@class='active']/a/@data-size").extract_first()
        sizes = json.loads(sizes)
        if sizes:
            for size in sizes:
                size_item = SizeItem()
                size_item['size_name']=size['option_value']
                size_item['size_quantity']=size['qty']
                var_item['size'].append(size_item)
        prod_item['variations'][color]= list()
        prod_item['variations'][color].append(var_item)
        data_list= response.xpath("//div[@class='sibling-product']//li/a/@data-config").extract()
        data_config= response.xpath("//div[@class='sibling-product']//li/a[@data-coloroption='{}']/@data-config".format(color)).extract_first()
        data_processed_list= list()
        data_processed_list.append(data_config)
        url= response.xpath("//div[@class='sibling-product']//li/a[@data-config!='{}']/@data-url".format(data_config)).extract_first()
        if url is None or data_processed_list == data_list:
            yield prod_item
        else:
            data_config= response.xpath("//div[@class='sibling-product']//li/a[@data-url='{}']/@data-config".format(url)).extract_first()
            data_processed_list.append(data_config)
            yield scrapy.Request(url, callback=self.parse_variation_info, meta={'item': prod_item, 'data_processed_list': data_processed_list,'data_list':data_list })
       
    def parse_variation_info(self, response):
        meta = deepcopy(response.meta)
        prod_item = ProductItem()
        prod_item= deepcopy(response.meta['item'])
        data_processed_list= response.meta['data_processed_list']
        data_list= response.meta['data_list']
        color= response.xpath("//div[@class='sibling-product']//li[@class='active']/a/@data-coloroption").extract_first() 
        var_item = VariationItem()
        var_item['display_color_name'] = color
        var_item['image_urls']= response.xpath("//div[@class='more-views vertical-slider']//img/@src").extract()
        var_item['size']=list()
        sizes = response.xpath("//div[@class='sibling-product']//li[@class='active']/a/@data-size").extract_first()
        sizes = json.loads(sizes)
        if sizes:
            for size in sizes:
                size_item = SizeItem()
                size_item['size_name'] = size['option_value']
                size_item['size_quantity'] = size['qty']
                var_item['size'].append(size_item)
        if prod_item['variations'][color] == None:
            prod_item['variations'][color]=list()
        prod_item['variations'][color].append(var_item)
        cond= True
        for x in data_list:
            if data_processed_list.count(x) != 1:
                cond= False
                break
        
        if cond == True:
            yield prod_item        
        else:
            for data_config in data_list:
                if data_config not in data_processed_list:
                    url = response.xpath("//div[@class='sibling-product']//li/a[@data-config='{}']/@data-url".format(data_config)).extract_first()
                    data_processed_list.append(data_config)      
                    request = scrapy.Request(url, callback= self.parse_variation_info, meta={'item':prod_item, 'data_processed_list':data_processed_list, 'data_list':data_list})
                    yield request
        
