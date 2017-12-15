#encoding=utf8

import usersetting
import Nspynner
import urlparse
import datetime
import threading
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class Conbrowser(object):

    # 黑名单筛选
    black_list = ['.cpp', '.pdf', '.gif', '.jpg', '.jpeg', '.txt', '.zip', '.png', '.css']

    def __init__(self, url):
        self.url = url
        self.Uurl = []
        self.Iurl = []
	self.click_point = []
	self.cnt = 0
        
        try:
            self.browser = Nspynner.Browser()
            self.browser.load(url=url)
        except Exception, e:
            print >> sys.stderr

    def analyse_page(self):
        elements = self.browser.webframe.findAllElements('a')
        for ele in elements.toList():
            # 获取url
            link = ele.attribute('href')
            link = str(link).strip()
            if self.checkurl(link):
                continue
            link = self.fixurl(link, self.url)
            if link not in self.Uurl :
                self.Uurl.append(link)

    # 检查获取到的url
    def checkurl(self, url):
        if len(url) == 0:
            return True
        if url == '#':
            return True
        for i in Conbrowser.black_list:
            if i in url:
                return True
        return False

    def get_fdir(self, furl):
        tmp = furl.strip().split('/')
        tmp.pop()
        return '/'.join(tmp)

    # 补全相对url
    def fixurl(self, url, furl):
        res = urlparse.urljoin(furl, url)
        return res

    def get_click_point(self):
        res = []
        elements = self.browser.webframe.findAllElements('*[onclick]')
        res = elements.toList()
        #elements = self.browser.webframe.findAllElements('input')
        #res = res + elements.toList()
        #elements = self.browser.webframe.findAllElements('a')
        #res = res + elements.toList()
        felements = self.browser.webframe.findAllElements('form')
        for fele in felements.toList():
            fchildele = fele.findAll('*')
            res = res + fchildele.toList()
        return res

    def click(self):
	while( len(self.click_point) > 0):
	    e = self.click_point[0]
	    self.click_point.remove(e)
            if usersetting.Maxclick >= 0 and cnt >= usersetting.Maxclick:
                print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [click] stop because reach max click number'
                break
            # print e.tagName()
            try:
                self.browser.wk_click_element(e, wait_load=True, timeout=0.5)
            except:
                self.browser.wk_click_element(e)
            self.analyse_page()
            self.cnt += 1.0
            print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [click] ' + "%.2f"%(self.cnt/len(self.click_point) * 100) + '%'


    def run(self):
        # 分析原始网页
        self.analyse_page()
 
        # 进行自动交互
        print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [Conbrowser] start click ' + self.url
        self.click_point = self.get_click_point()
        self.cnt = 0.0
	self.total = len(self.click_point)

	#threads = []
	#for i in range(5):
	#    t = threading.Thread(target=self.click)
	#    threads.append(t)
	
	#for t in threads:
        #    t.setDaemon(True)
        #    t.start()
	
	#for t in threads:
	#    t.join()

	while( len(self.click_point) > 0):
            e = self.click_point[0]
            self.click_point.remove(e)
            if usersetting.Maxclick >= 0 and cnt >= usersetting.Maxclick:
                print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [click] stop because reach max click number'
                break
            # print e.tagName()
            try:
                self.browser.wk_click_element(e, wait_load=True, timeout=0.5)
            except:
                self.browser.wk_click_element(e)
            self.analyse_page()
            self.cnt += 1.0
            print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [click] ' + "%.2f"%(self.cnt/self.total * 100) + '%'


        # self.browser.wk_click('input[name=\"B1\"]', wait_load=True, timeout=1)
        print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [Conbrowser] finish click'
        
        # 获取浏览器自动请求的信息
        requests = self.browser.get_request_urls()
        for re in requests:
            print datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' [Conbrowser] ' + str(re['rawurl'])
            for i in usersetting.Blacklist:
                if i in re['url']:
                    continue
            if len(re['query']) != 0 or len(re['data']) != 0:
                tmp = {}
                tmp['domain'] = re['domain']
                tmp['url'] = re['url']
                tmp['method'] = re['method']
                tmp['port'] = re['port']
                tmp['query'] = re['query']
                tmp['data'] = re['data']
                tmp['rawurl'] = re['rawurl']
                self.Iurl.append(tmp)
            if re['rawurl'] not in self.Uurl:
                self.Uurl.append(re['rawurl'])
        
        return [self.Uurl, self.Iurl]

    def close(self):
        self.browser.close()
            

if __name__ == "__main__":
    print("test")
    url = "http://demo.aisec.cn/demo/aisec/"
    browser = Conbrowser(url)
    print browser.run()
    browser.close()
    # browser = Nspynner.Browser()
    # browser.load(url=url)
    # browser.wk_click('input[name=\"B1\"]', wait_load=True)
    browser.close()
