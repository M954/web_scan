#encoding=utf8

import os
import json
import random
import requests
import threading
import MySQLdb
import hashlib
from time import ctime,sleep,time

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class DetectDB:

    host = '127.0.0.1'
    port = 3306
    user = 'root'
    passwd = '000000'
    db = 'crawl'

    serverlist = { 'http://127.0.0.1:8775':0 }
    finishtasks = []
    user_agent_file = "user-agent"
    user_agent = []

    def __init__(self):
        self.cur = None
        self.fdir = os.getcwd() + '/tmpfile/'
        self.workserver = len(DetectDB.serverlist)
        for i in open(DetectDB.user_agent_file).readlines():
            DetectDB.user_agent.append(i)
        
    
    # 分布式相关的部分

    def get_server(self):
        #从多个sqlmap服务中选择任务最少的一个，现在只有一个就先用着
        tlist = sorted(DetectDB.serverlist.iteritems(), key=lambda d:d[1], reverse = False)
        DetectDB.serverlist[tlist[0][0]] += 1
        return tlist[0][0]

    def free_server(self, server):
        if DetectDB.serverlist[server] > 0:
            DetectDB.serverlist[server] -= 1

    # 分布式相关部分结束


    # 数据库相关操作

    def connectDB(self):
        self.conn= MySQLdb.connect(
                host=DetectDB.host,
                port=DetectDB.port,
                user=DetectDB.user,
                passwd=DetectDB.passwd,
                db=DetectDB.db,
                )
        self.cur = self.conn.cursor()
        self.taskcur = self.conn.cursor()

    def get_info(self, taskid):
        res = {}
        sqli = "SELECT url, server FROM task_urls where taskid = \"%s\""%taskid
        try:
            print sqli
            self.cur.execute(sqli)
            data = self.cur.fetchone()
            print data
            res["url"] = data[0]
            res["server"] = data[1]
            return res
        except Exception, e:
            print "[error in get_info] " + str(e)
            return False

    def insert_info(self, taskid, url, server):
        sqli = "INSERT INTO task_urls VALUES(\"%s\", \"%s\", \"%s\")"%(taskid, url, server)
        try:
            print sqli 
            self.cur.execute(sqli)
            self.conn.commit()
            return True
        except Exception, e:
            print "[error in set_info] " + str(e)
            return False

    def delete_info(self, taskid):
        sqli = "DELETE FROM task_urls WHERE taskid = \"%s\""%taskid
        try:
            self.cur.execute(sqli)
            return True
        except Exception, e:
            print "[error in delete_info] " + str(e)
            return False
    
    def get_data(self, taskid) :
        
        info = self.get_info(taskid)
        if info == False:
            return False
        server = info['server']
        taskurl = info['url']
        # server = self.get_server() # 改改改
        
        url = server + '/scan/' + taskid + '/data'
        try:
            # print requests.get(url).text
            response = json.loads(requests.get(url).text)
            if response['success'] == True:
                # 向数据库中写入数据
                data = response['data']
                # print json.dumps(data)
                print '[log] ' + taskid + ' data ' + str(data)
                if len(data) != 0:
                    for i in data:
                        if i['type'] == 1:
                            i = i['value'][0]
                            dbms = i['dbms']
                            dbms_version = i['dbms_version']
                            # print self.add_translation(data)
			    data = i['data']['1']['payload']
                            # print json.dumps(data)
			    if self.check_url(taskurl):
                            	#sqli = 'INSERT INTO sql_urls(url, dbms, dbms_version, data) VALUES(\'%s\',\'%s\',\'%s\',\'%s\')'%(
                                #	    taskurl.replace('\'', '\'\''), str(dbms).replace('\'', '\'\''), str(dbms_version).replace('\'', '\'\''), json.dumps(self.add_translation(data)).replace('\'', '\'\''))
                            	sqli = 'INSERT INTO sql_urls(url, dbms, dbms_version, data) VALUES(\'%s\',\'%s\',\'%s\',\'%s\')'%(
                                           taskurl.replace('\'', '\'\''), str(dbms).replace('\'', '\'\''), str(dbms_version).replace('\'', '\'\''), data.replace('\'', '\'\''))
				print sqli
                            	self.cur.execute(sqli)
                            	self.conn.commit()
                            	print '[log] success in insert to database'
            if self.delete_task(taskid) == False:
                print 'delete task failed'
            self.delete_info(taskid)
            self.free_server(server)
        except Exception, e:
            print '[error in get_data]' + str(e)
    
    def check_url(self, url):
	sqli = "select * from sql_urls where url = \'%s\'"%(url)
	self.cur.execute(sqli)
	data = self.cur.fetchone()
	print '[data] ' + str(data)
	if data != None:
	    return False
	else:
	    return True

    # 数据库相关操作结束


    # sqlmap检测任务相关

    def new_task(self):
        server = self.get_server()
        url=server+"/task/new"
        res = {}
        res['server'] = server
        try: 
            response = json.loads(requests.get(url).text)
            if(response['success'] == True):
                taskid = response['taskid']
                res['taskid'] = taskid
                return res
            else:
                return False
	except Exception,e:
	    print "[error in new_task] " + str(e)

    def delete_task(self, taskid):
        
        info = self.get_info(taskid)
        if info == False:
            return False
        server = info['server']
        # server = self.get_server()
        
        url=server+"/task/" + taskid + "/delete"
        try:
            response = json.loads(requests.get(url).text)
            print response
            if(response['success'] == True):
                return True
            else:
                return False
	except Exception, e:
	    print "[error in new_task] " + str(e)

    def set_options(self, taskid, options={}):
        if options is None:
            return False
        
        info = self.get_info(taskid)
        if info == False:
            return False
        server = info['server']
        # server = self.get_server() #从数据库里面读取，先用着，待改
        
        url = server+'/option/'+taskid+'/set'
        #处理一下数据，待加...
        data = json.dumps(options)
        print data
        print url
        response = json.loads(requests.post(url, data=data, headers={'content-Type':'application/json'}).text)
        if(response['success'] == True):
            return True
        else:
            print response
            return False

    def start_scan(self, taskid, options={}):
        
        info = self.get_info(taskid)
        if info == False:
            return False
        server = info['server']
        # server = self.get_server() #从数据库里面读取，先用着，待改
        
        url = server+'/scan/'+taskid+'/start'
        #处理一下数据，待加...
	data = json.dumps(options)
        print url
        print data
        response = json.loads(requests.post(url, data=data, headers={'content-Type':'application/json'}).text)
        if(response['success'] == True):
            return True
        else:
            return False

    # sqlmap检测任务相关结束


    # 从数据库开始的函数
    
    def start_detect(self):
        self.connectDB()
        sql = "select url, port, method, query, data, rawurl from result_urls"
        print sql
        try:
            urls = self.taskcur.execute(sql)
            data = self.taskcur.fetchone()
            while data != None:
                print '[log] task url is ' + str(data[0])
                options = {}
                # if data[1] > 0:
                #     options['url'] = data[0] + ':' + str(data[1])
                # if data[2] != 'GET':
                #    options['method'] = data[2]
                query = json.loads(data[3])
                if len(data[4]) > 0:
                    filedir = './tmpfile/'
                    filename = hashlib.md5(str(time())).hexdigest()
                    f = open(self.fdir + filename, 'w')
                    f.write(data[4])
                    f.close()
                    options['requestFile'] = self.fdir+filename
                elif len(query) > 0:
                    options['url'] = data[5]
                    #options['url'] = options['url'] + '?'
                    #cnt = 0
                    #for q in query:
                    #    options['url'] = options['url'] + q + '=' + str(query[q])
                    #    cnt += 1
                    #    if cnt != len(query):
                    #        options['url'] = options['url'] + '&'
                
                # 测试
                # options['forms'] = True
                # options['user-agent'] = random.choice(DetectDB.user_agent)
                # options['level'] = 2
                # options['risk'] = 2
                 
                print options
              
                res = self.new_task()
                if res == False:
                    print 'create task failed'
                    continue 
                self.insert_info(res['taskid'], data[5], res['server'])
                #if self.set_options(taskid, options) == False:
                #    print 'set options failed'
                #    continue
                if self.start_scan(res['taskid'], options) == False:
                    print 'start scan failed'
                    continue
                print '[log] pull task ' + options['url'] if 'url' in options else data[5]
                data = self.taskcur.fetchone()
                
        except Exception, e:
           print '[error in start_detect]' + str(e)

    # 从数据库开始的函数结束


    # 监控进程相关

    def monitor(self, server):
        url = server + '/admin/' + 'xxxxxx' + '/list'
        while(True):    
            try:
                response = json.loads(requests.get(url).text)
                if response['success'] == True:
                    if response['tasks_num'] == 0:
                        self.workserver -= 1
                        break
                    for i in response['tasks']:
                        print '[log] task ' + i + ' status is ' + response['tasks'][i]
                        if response['tasks'][i] == 'terminated':
                            if i not in DetectDB.finishtasks:
                                DetectDB.finishtasks.append(i)
                else:
                    print 'get list failed'
            except Exception, e:
                print '[error in minitor]' + str(e)
            sleep(5)

    def get_data_loop(self):
        while(True):
            if self.workserver == 0:
                break
            # print DetectDB.finishtasks
            if len(DetectDB.finishtasks) != 0:
                for i in DetectDB.finishtasks:
                    self.get_data(i)
                    DetectDB.finishtasks.remove(i) 

            sleep(5)
    
    # 监控进程结束

    # 处理写入数据库的json字符串

    def add_translation(self, data):
        if type(data) == dict:
            for i in data:
                data[i] = self.add_translation(data[i])
        elif type(data) == list:
            for i in data:
                i = self.add_translation(i)
        else:
            try:
                data = data.replace('\"', '\\\"')
            except:
                pass
        return data

if __name__ =="__main__":
    detect = DetectDB()
    detect.start_detect()  
    threads = []
    for i in DetectDB.serverlist: 
        t = threading.Thread(target=detect.monitor,args=(i,))
        threads.append(t)
    t = threading.Thread(target=detect.get_data_loop)
    threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    
    t.join()
