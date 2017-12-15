#encoding=utf8
import Nspynner
import Conbrowser
import scrapy
import random
import sys
import re
import urlparse
import datetime
import MySQLdb
import usersetting
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy_splash import SplashRequest
from items import TutorialItem 

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
 
# 一个服务器启动一个spider
class UrlSpider(scrapy.Spider):
    # 必须定义
    name = "url"
    
    # 已经爬过的url，用于去重
    unvalidurl = ["https://opencv.org/"] 

    # 当前爬的域名，非该域名不会爬取
    allowed_domains = ["opencv.org"]

    # 初始urls
    start_urls = [
       "https://opencv.org/",
    ]
   
    # 用户设置
    custom_settings = {}
 
    # 黑名单筛选
    black_list = ['.cpp', '.pdf', '.gif', '.jpg', '.jpeg', '.txt', '.zip', '.png', '.css']

    # 用于构造header的UA
    user_agent = usersetting.Useragent

    def init_mysql(self):
        self.db = MySQLdb.connect(usersetting.SQLip, 
                                  usersetting.SQLuser, 
                                  usersetting.SQLpasswd,
                                  usersetting.SQLdatabase)
        self.cursor = self.db.cursor() 

    def start_requests(self):
        self.init_mysql()
        self.sql_clear_url()
        for url in UrlSpider.start_urls:
            myheader = {
                'referer': url,
                'user-agent': random.choice(UrlSpider.user_agent),
            }
            yield scrapy.Request(url, self.parse, headers=myheader)

    # 默认response处理函数
    def parse(self, response):

        print datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ' [spider] ' + response.url

        result = set() 
        
        hxs = scrapy.Selector(response)

        # 解析页面方法1
        sites = hxs.xpath('//a')
        for site in sites:
            # 获取方法1
            link = site.xpath('@href').extract()
	    for i in link:
                i = i.strip()
                if self.checkurl(i):
                    continue
                i = self.fixurl(i, response.url)
                if i not in result :
                    result.add(i)
            # 获取方法2
            #match = re.findall(r'(http[^"]+)', str(site)) 
            #for i in match:
            #    i = i.strip()
            #    if self.checkurl(i):
            #        continue
            #    i = self.fixurl(i, response.url)
            #    if i not in result :
            #        result.add(i)
         
        # 解析页面方法2
        try: 
            if len(response.url) < 500 :
                browser = Conbrowser.Conbrowser(response.url)
                res = browser.run()
                for i in res[0]:
                    if self.checkurl(i):
                        continue
                    if i not in result :
                        result.add(i)
                for i in res[1]:
                    if self.checkurl(i["url"]):
                        continue
                    item = TutorialItem()
                    item["domain"] = i["domain"]
                    item["url"] = i["url"]
                    item["method"] = i["method"]
                    item["port"] = i["port"]
                    item["query"] = i["query"]
                    item["data"] = i["data"]
                    item["rawurl"] = i["rawurl"]
                    # print '[spider] ' + str(item)
                    yield item

                browser.close()
        except Exception, e:
            print >> sys.stderr, response.url, e
         

        # 构造header
        myheader = {
            'referer': response.url,
            'user-agent': random.choice(UrlSpider.user_agent),
        }

        for url in result:
            if self.sql_exist_url(url) == False:
                continue
            self.sql_insert_url(url)
            yield scrapy.Request(url, self.parse, headers=myheader)

    # 检查获取到的url
    def checkurl(self, url):
        if len(url) == 0:
            return True
        if url == '#':
            return True
        for i in usersetting.Blacklist:
            if i in url:
                return True
        return False

    def get_fdir(self, furl):
        tmp = furl.strip().split('/')
        tmp.pop()
        return '/'.join(tmp)

    # 补全相对url
    def fixurl(self, url, furl):
        res = url
        if 'http' in url:
            res = url
        elif UrlSpider.allowed_domains[0] in url:
            res = 'http://' + url
        elif url[0] != '/':
            res = self.get_fdir(furl) + '/' + url
        else:
            res = 'http://' + UrlSpider.allowed_domains[0] + '/' + url
        
        res = urlparse.urljoin(furl, url)
        # print '[current url]' + str(url)
        # print '[current dir]' + str(self.get_fdir(furl))
        # print '[result url]' + str(res)
        return res

    def sql_clear_url(self):
        try:
            sqli = "delete from crawl_urls"
            self.cursor.execute(sqli)
            self.db.commit()
        except Exception, e:
            print >> sys.stderr, '[clear error] ' + str(e)

    def sql_insert_url(self, url):
        try:
            path = url.split('?')[0]
            sqli = "insert into crawl_urls(url) values(\'%s\')"%(str(path).replace("'", "''"))
            # print 'insert : ' + str(sqli)
            self.cursor.execute(sqli)
            self.db.commit()
        except Exception, e:
            print >> sys.stderr, '[insert error] ' + str(e)

    def sql_exist_url(self, url):
        try:
            path = url.split('?')[0]
            sqli = "select url from crawl_urls where url = \'%s\'"%(str(path).replace("'", "''"))
            self.cursor.execute(sqli)
            data = self.cursor.fetchone()
            if data:
                return False
            else:
                return True
        except Exception, e:
            print >> sys.stderr, '[search error] ' + str(e)
            return False
    
    def sql_filter_url(self, url):
        def get_domain(url):
            return url.strip().split('/')[2]
        
        def get_path(url):
            return '/'.join(url.strip().split('/')[3:-1])

        try:
            
            # sqli = 
            pass
        except Exception, e:
            pass
          
