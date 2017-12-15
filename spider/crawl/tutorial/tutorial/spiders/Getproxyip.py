#encoding=utf8
import scrapy

class ProxySpider(scrapy.Spider):
    name = "proxy"

    start_urls = ["http://www.xicidaili.com/nn"]
