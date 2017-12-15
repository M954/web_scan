#encoding=utf8

import MySQLdb
from optparse import OptionParser 
from urlparse import urljoin
from urlparse import urlparse
import requests
import threading
import MySQLdb

config = "config2.txt"
Testurls = []

conn= MySQLdb.connect(
        host='127.0.0.1',
        port = 3306,
        user='root',
        passwd='000000',
        db ='crawl',
        )
cur = conn.cursor()

def test_url(url, method, timeout):
	if method == 'GET':
		return requests.get(url, timeout=timeout).status_code
	else:
		return requests.head(url, timeout=timeout).status_code

def test_url_thread(method, timeout):
	while (len(Testurls) > 0):
		try:
			tmp = Testurls[0]
			Testurls.remove(tmp)
			result = test_url(tmp, method, timeout)
			if result != None and str(result) != '404':
				# print urlparse(tmp).netloc
				sqli = 'insert into file_urls (domain, url, status) values(\'%s\', \'%s\', \'%s\')'%(urlparse(tmp).netloc, tmp, result)
				# print sqli
				cur.execute(sqli)
				conn.commit()
				print '%s\t%s'%(tmp, result)
		except Exception, e:
			# print e
			# print 'there is something wrong here'
			pass

def start_thread(method, concurrent, timeout):
	
	thread_list = []
	
	for i in xrange(concurrent):
    		t =threading.Thread(target=test_url_thread,args=(method, timeout,))
    		t.setDaemon(True)
		thread_list.append(t)
	
	for t in thread_list:
		t.start()

	for t in thread_list:
		t.join()
	
		
def run_from_database(database, method, concurrent, timeout):
	conn= MySQLdb.connect(
        	host='127.0.0.1',
        	port = 3306,
        	user='root',
        	passwd='000000',
        	db ='crawl',
        	)
	cur = conn.cursor()

	sqli = 'select url from crawl_urls'
	cur.execute(sqli)
	data = cur.fetchone()
	while data != None:
		load_testurls(data[0])
		start_thread(method, concurrent, timeout)

def run_from_file(filename, method, concurrent, timeout):
	for i in open(filename).readlines():
		load_testurls(i)
		start_thread(method, concurrent, timeout)

def run(url, method, concurrent, timeout):
	load_testurls(url)
	start_thread(method, concurrent, timeout)

def load_testurls(url):
	for i in open(config).readlines():
		Testurls.append(urljoin(url, i.strip()))

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
	parser.add_option("-t", "--timeout", dest="timeout",
                  help="the max timeout for loading url", type="float")
	parser.add_option("-m", "--method", dest="method",
                  help="method for scanning(GET, HEAD)", type="string")
	parser.add_option("--delay", dest="delay", 
		  help="delay between two requests", type="float")

	(options, args) = parser.parse_args()
	print options

	concurrent = 5
	timeout = 3.0
	delay = 0.0
	method = 'HEAD'	
	
	if options.concurrent != None:
		concurrent = options.concurrent
	if options.timeout != None:
		timeout = options.timeout
	if options.delay != None:
		delay = options.delay
	if options.method != None:
		method = options.method.upper()
		if method != 'GET' and method != 'HEAD':
			print 'method only supports GET or HEAD'
			exit(1)

	if options.url != None:
		run(options.url, method, concurrent, timeout)
	elif options.filename != None:
		run_from_file(options.filename, method, concurrent, timeout)
	elif options.database != None:
		run_from_database(options.database, method, concurrent, timeout)
	else:
		parser.print_help()
	
	conn.close()	
