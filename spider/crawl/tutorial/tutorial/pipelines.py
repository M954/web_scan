# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import json
import urlparse
import MySQLdb
import MySQLdb.cursors
from scrapy.crawler import Settings as settings
import usersetting

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class TutorialPipeline(object):

    def __init__(self):

        dbargs = dict(
            host = usersetting.SQLip ,
            db = usersetting.SQLdatabase,
            user = usersetting.SQLuser, #replace with you user name
            passwd = usersetting.SQLpasswd, # replace with you password
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
            )    
        self.dbpool = adbapi.ConnectionPool('MySQLdb',**dbargs)

    def process_item(self, item, spider):
        res = self.dbpool.runInteraction(self.insert_into_table,item)
        return item
 
    def insert_into_table(self,conn,item):
        if len(item) < 6:
            return
        print item['url']
        if len(item['query']) == 0 and len(item['data']) == 0:
            return
        try:
            res = self.check_update(conn, item)
            print 'res : ' + str(res)
            if res['update'] == False:
                return 
            else:
                if 'query' in res:
                    # print 'update result_urls set query=\'%s\' where url=\'%s\''%(str(json.dumps(res['query'])), str(item['url']))
                    conn.execute('update result_urls set query=\'%s\' where url=\'%s\''%(
                                str(json.dumps(res['query'])).replace("'", "''"), str(item['url']).replace("'", "''")))
                else:
                    # print 'insert into result_urls(domain, url, port, method, query, data) values(\'%s\', \'%s\', %s, \'%s\', \'%s\', \'%s\')'%(str(item['domain']), str(item['url']), str(item['port']), str(item['method']), str(json.dumps(item['query'])), str(item['data']))
                    sqli = "select count(*) from result_urls"
		    conn.execute(sqli)
		    id_data = conn.fetchone()
		    sqli = "insert into result_urls(id, domain, url, port, method, query, data, rawurl) values(%s, \'%s\', \'%s\', %s, \'%s\', \'%s\', \'%s\', \'%s\')"% \
                         (str(id_data["count(*)"]), str(item['domain']).replace("'", "''"), str(item['url']).replace("'", "''"), str(item['port']).replace("'", "''"), 
                          str(item['method']).replace("'", "''"), str(json.dumps(item['query'])).replace("'", "''"), str(item['data']).replace("'", "''"), 
                          str(item['rawurl']).replace("'", "''"))
		    print sqli
		    conn.execute(sqli)
        except Exception, e:
            print '[pip insert error] ' + str(e)

    def check_update_old(self, cnn, item):
        try:
            result = {}
            result['update'] = False
            sqli = "select port, method, query, data from result_urls where url = \'%s\' and method = \'%s\' and port = %s and data = \'%s\'" % (str(item['url']).replace("'", "''"), str(item['method']).replace("'", "''"), str(item['port']).replace("'", "''"), str(item['data']).replace("'", "''"))
            cnn.execute(sqli)
            data = cnn.fetchone()
            if data == None:
                result['update'] = True
                return result
            print data['query']
            jquery = json.loads(data['query'])
            for i in item['query']:
                if i not in jquery:
                    result['update'] = True
                    result['query'] = jquery
                    result['query'][i] = item['query'][i]
            return result
        except Exception, e:
            print '[database error] ' + str(e)

    def check_update(self, cnn, item):
        try:
            result = {}
            result['update'] = False
            sqli = "select port, method, query, data from result_urls where rawurl = \'%s\' and method = \'%s\' and port = %s and data = \'%s\'" % (str(item['rawurl']).replace("'", "''"), str(item['method']).replace("'", "''"), str(item['port']).replace("'", "''"), str(item['data']).replace("'", "''"))
            cnn.execute(sqli)
            data = cnn.fetchone()
            if data == None:
                result['update'] = True
                return result
            result['update'] = False
            return result
        except Exception, e:
            print '[database error] ' + str(e)

