#encoding=utf8
import spynner
import urllib2
from bs4 import BeautifulSoup
import sys
import urllib
import MySQLdb
reload(sys)
sys.setdefaultencoding('utf8')

def get_search_result(word):
	conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='000000',db='crawl',port=3306)
    	cur=conn.cursor()
	url="http://cn.bing.com/search?q=" + urllib.quote(word)
	content=urllib2.urlopen(url).read()
	soup = BeautifulSoup(content, "lxml")
	for link in soup.find_all('li', "b_algo"):
    		tmp = link.h2.a.get('href')
    		if tmp != None:
			if 'http' in tmp or 'https' in tmp:
				sqli = "insert into start_urls values('%s')"%(tmp)
				cur.execute(sqli)
				print tmp
	url="http://cn.bing.com/search?q=" + urllib.quote(word) + "&first=11"
	content=urllib2.urlopen(url).read()
	soup2 = BeautifulSoup(content, "lxml")
	for link in soup2.find_all('li', "b_algo"):
    		tmp = link.h2.a.get('href')
    		if tmp != None:
        		if 'http' in tmp or 'https' in tmp:
				sqli = "insert into start_urls values('%s')"%(tmp)
                                cur.execute(sqli)
				print tmp
	cur.close()
	conn.commit()
	conn.close()

if __name__ == "__main__":
	get_search_result("demo.aisec")
