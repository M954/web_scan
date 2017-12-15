#encoding=utf8
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
 
from spiders.UrlSpider import UrlSpider

import datetime
import MySQLdb
import optparse
import sys
from optparse import OptionParser  
import get_domain
import usersetting

# 获取settings.py模块的设置
settings = get_project_settings()
process = CrawlerProcess(settings=settings)

# def get_domain(url):
#     return url.strip().split('/')[2]

def start_spider(url) :
    UrlSpider.start_urls = [url]
    UrlSpider.unvalidurl = [url]
    UrlSpider.allowed_domains = [get_domain.get_domain(url)]
    # print UrlSpider.allowed_domains
    
    # 可以添加多个spider
    # process.crawl(Spider1)
    # process.crawl(Spider2)
    process.crawl(UrlSpider)

    # 启动爬虫，会阻塞，直到爬取完成
    process.start()

def start_from_database(database):
    db = MySQLdb.connect(usersetting.SQLip, 
                         usersetting.SQLuser, 
                         usersetting.SQLpasswd,
                         database )
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM start_urls"
    try:
       # 执行SQL语句
       cursor.execute(sql)
       # 获取所有记录列表
       results = cursor.fetchall()
       for row in results:
           url = row[0]
           # print url
           start_spider(url)

    except Exception,e:
        print >> sys.stderr, e

    # 关闭数据库连接
    db.close()

def start_from_url(url):
    start_spider(url)
    
    db = MySQLdb.connect(usersetting.SQLip, 
                         usersetting.SQLuser, 
                         usersetting.SQLpasswd, 
                         usersetting.SQLdatabase)
    cursor = db.cursor()

    # SQL 查询语句
    sqli = 'SELECT url FROM result_urls WHERE domain like \'%%%s%%\''%get_domain.get_domain(url)
    print str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + ' ' + sqli
    cursor.execute(sqli)
    data = cursor.fetchone()
    while data != None:
        print data[0]
        data = cursor.fetchone()
    db.close()

def start_from_file(filename):
    for line in open(filename).readlines():
        start_from_url(line)
    close(filename)

if __name__ == "__main__":
    
    parser = OptionParser()  
    parser.add_option("-d", "--database", dest="database",  
                  help="read start_urls from database", type="string")  
    parser.add_option("-u", "--url", dest="url", 
                  help="start crawling from the appointed url", type="string")
    parser.add_option("-f", "--file", dest="filename",     
                  help="read start_urls from the appointed file", type="string") 
    parser.add_option("-c", "--concurrent", dest="concurrent",
                  help="the max concurrent requests", type="int")
    parser.add_option("-t", "--downloadtime", dest="downloadtime",
                  help="the max time for downloading", type="int")
    parser.add_option("-C", "--maxclick", dest="maxclick",
                  help="the max num to click", type="int")
    parser.add_option("-w", "--splashwait", dest="splashwait",
                  help="the max time for the splash to wait", type="int")    
 
    (options, args) = parser.parse_args()  

    print options
 
    custom_settings = {}    

    if options.concurrent != None:
        custom_settings["CONCURRENT_REQUESTS"] = options.concurrent
    
    if options.downloadtime != None:
        custom_settings["DOWMLOAD_DELY"] = options.downloadtime

    if options.maxclick != None:
        usersetting.Maxclick = options.maxclick
    
    if len(custom_settings) != 0:
        UrlSpider.custom_settings = custom_settings

    if options.database != None:
        start_from_database(options.database)
    elif options.url != None:
        start_from_url(options.url)
    elif options.filename != None:
        start_from_file(options.filename)
    else:
        parser.print_help()
