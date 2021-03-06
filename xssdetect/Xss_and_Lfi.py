#!/usr/bin/env python
# encoding=utf-8

import os
import sys
import copy
import json
import urlparse
import urllib2
import MySQLdb
from time import time
from optparse import OptionError
from optparse import OptionGroup
from optparse import OptionParser
from browser import MyBrowser
import sys
import logging
import logging.config
import csv
import traceback

specil_list=['referer','user_agent','cookie']
mypath = os.path.join(os.path.dirname(os.path.realpath(__file__)),'tmp_file')
xsstypes = ['alert', 'prompt', 'confirm', 'throw']
lfitypes = ['windows', 'linux']
eventtypes = ['auto', 'event']
lfi_feature_windows = []


#Method of Url
def Method_Of_Url(url,method, headers, targetParam = None, queryDict = {}, \
							postDict = {}, payloadsDict = {}):

	retVal = False, '', '','',''
        totalcnt = len(eventtypes) * len(xsstypes)
	cnt = 0.0
	for eventtype in eventtypes:
		for xsstype in xsstypes:
			# print xsstype
			cnt += 1
			print str(cnt/totalcnt * 100) + '%'
			payloads = payloadsDict[eventtype][xsstype]
			if method.upper() == 'GET':
				if queryDict:
					print '.................It is GET'
					print 'queryDict are:',queryDict
					for param in queryDict:
						# print param
                                                # print targetParam
						if param != targetParam:
							# print 'got ycha..'
							continue
						# print 'ok. do it...'
						browser = MyBrowser(download_directory = mypath) 
						flag = False
						# print 'payloads..... ', payloads
						for payload in payloads:
							# print "payload: ", payload
							payloadDict = copy.deepcopy(queryDict)
							payloadDict[param] = "%s%s" % (payloadDict[param], payload)
							queryStr = toParamStr(payloadDict)
							#print 'payloadDict[param] is:',payloadDict[param]
							#print 'payloadDict is:',payloadDict
							#拼接了payload的url
							reqUrl = '%s?%s' % (url, queryStr)
							#print 'reqUrl is:',reqUrl
							#通过webkit模拟浏览器对该url执行，如果执行时弹框则会被捕获到，触发调用alert函数
                                                        # print reqUrl	
							browser.attack(reqUrl, 'GET', '', headers)
							#print browser.html
							if eventtype == 'event':
								# print "make an event..."
								browser.self_event_attack()
							if browser.ret:
								flag = True
								#payload 在 URL中 
								retVal = True, 'URL', reqUrl, xsstype, eventtype   
								print "xss found in %s" %reqUrl
								return retVal
							if flag:
								print 'break 1...'
								break
				else:
					print '......queryDict is null'
					break
			elif method.upper() == 'POST':
				print 'it is POST'
				if postDict:
					queryStr = toParamStr(queryDict) if queryDict else ''
					reqUrl = '%s?%s' % (url, queryStr) if queryStr else url
					for param in postDict:
						if param != targetParam: #如果param与目标参数不匹配，则继续遍历直到匹配后可执行continue后的语句
							continue
						browser = MyBrowser(download_directory = mypath)
						flag = False
						for payload in payloads:
							print "[payload]: ", payload					
							payloadDict = copy.deepcopy(postDict)
							payloadDict[param] = "%s%s" % (payloadDict[param], payload)
							browser.attack(reqUrl, 'POST', payloadDict, headers)
							print eventtype
							print xsstype
							if eventtype == 'event':
								browser.self_event_attack()
							print '.................:',browser.ret 
							if browser.ret:
								flag = True
								payload_data = toParamStr(payloadDict)
								#payload 在data里 
								retVal = True, 'data', payload_data, xsstype, eventtype
								print "[*] xss found in %s" %reqUrl
								return retVal
							if flag:
								print 'break 3...'
								break
				else:
					print '......postDict is null'
					break
	return retVal	
	
	

#Method of Referer and User_agent
def Method_Of_referer_user_agent(url,method, headers, targetType=None,targetParam = None, queryDict = {}, \
							postDict = {}, payloadsDict = {}, referer = '', \
							user_agent = '',cookie=''):
	retVal = False, '', '','','' #函数返回值定义
	headers={'Cookie':'','Host':'','Referer':'','User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
	RequestRefer=''
	RequestUser_agent=''
	payloadDict={}
	try:
		for eventtype in eventtypes:
			for xsstype in xsstypes:
				payloads = payloadsDict[eventtype][xsstype]
				flag=False
				for payload in payloads:
					if postDict:
						payloadDict = copy.deepcopy(postDict)
					print "[payload]: ", payload
					if targetType == 'referer':
					#这里有两种形式referer 一种为replace,一种为append,append往深研究会有很多种形式，比如referer形式是get或post，具体是否要继续拆分切割还要进行进一步分析，由于目前replace场景常见，所以目前只考虑简单的referer
						print "......referer"
						RequestRefer = '%s%s' % (referer,payload)
						print 'RequestRefer is:',RequestRefer
					headers['Referer']=RequestRefer
					if targetType == 'user_agent':
					#同上，User_agent也有两种显示方式
						print "......user_agent"
						RequestUser_agent = '%s%s' % (user_agent, payload)#若user_agent为空，则将payload与''做拼接，若不为空,与user_agent拼接
					headers['User-Agent']=RequestUser_agent
					browser=MyBrowser(referer=RequestRefer,user_agent=RequestUser_agent,download_directory = mypath,headers=headers)
					if method =='GET':
						print '.................It is GET'
						print eventtype
						print xsstype
						browser.attack(url,'GET','',headers)
					else:
						print '.................It is POST'
						print eventtype
						print xsstype
						browser.attack(url,'POST',payloadDict,headers)
					if eventtype =='envent':
						browser.self_event_attack()
					print '.................:',browser.ret 
					if browser.ret:
						flag = True
						if targetType == 'referer':
							retVal = True, 'referer', RequestRefer, xsstype, eventtype
							print "xss found in %s" %RequestRefer
							return retVal
						if flag:
							print 'break......'
							break
						if targetType == 'user_agent':
							retVal = True, 'user_agent', RequestUser_agent, xsstype, eventtype
							print "xss found in %s" %RequestUser_agent
							return retVal
						if flag:
							print 'break......'
							break
	except Exception, e:
		print str(e)
		print traceback.format_exc()


#Method of Cookie
def Method_Of_cookie(url,method, headers, targetParam = None, queryDict = {}, \
							postDict = {}, payloadsDict = {},referer='',user_agent='',cookie=''):
	print "......cookie"
	ReqCookieString=""
	retVal = False, '', '','','' #函数返回值定义
	headers={'Cookie':'','Host':'','Referer':'','User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
	try:
		CookieStr = cookie if cookie else ''
		CookieDict=toParamDictCookie(CookieStr) if CookieStr else {}
		for eventtype in eventtypes:
			for xsstype in xsstypes:
				payloads = payloadsDict[eventtype][xsstype]
				flag = False
				print '.....CookieDict:',CookieDict
				for payload in payloads:
					#replace的情况，直接变为恶意脚本处理
					if CookieDict is None:
						ReqCookieString='%s%s' % (CookieStr,payload)
						headers['Cookie']=ReqCookieString
					#append的情况，将抽取的cookie与.txt文档里的脚本拼接
					else:	
						for param in CookieDict:
							if param!=targetParam:
								# print '......param is:',param
								# print '......targetParam is:',targetParam
								#print 'got ycha..'
								continue
							#将传进来的cookie字符串进行变形
							print 'ok. do it...'
							CookieDictionary=copy.deepcopy(CookieDict)
							CookieDictionary[param]="%s%s" % (CookieDictionary[param], payload)
							#print '......CookieDictionary[param] is:',CookieDictionary[param]
							ReqCookieString = toParamStr(CookieDictionary)
							headers['Cookie']=ReqCookieString
							#print '......ReqCookieString is:',ReqCookieString
							print 'headers are.....:',headers
					browser = MyBrowser(cookie = ReqCookieString, download_directory = mypath,headers=headers)
					if method=='GET':
						browser.attack(url,'GET','',headers)
					else:
						if postDict:
							payloadDict = copy.deepcopy(postDict)
						browser.attack(url,'POST',payloadDict,headers)
					if eventtype =='envent':
						browser.self_event_attack()
						print '---------------------------------------------:',browser.ret 
					if browser.ret:
						flag = True
						retVal =True,'cookie',ReqCookieString, xsstype, eventtype
						print "[*] xss found in %s" %ReqCookieString
						return retVal
					if flag:
						print 'break......'
						break
	except Exception, e:
		print str(e)
		print traceback.format_exc()

#检测本地文件读取是否成功
def check_windows_lfi(html):
	cnt = 0
	html = html.lower()
	for fea in lfi_feature_windows:
		if fea in html:
			cnt += 1
	if cnt >= 2:
		return True
	else:
		return False

def check_linux_lfi(html):
	#for i in html.split('\n'):
	#	fea = i.split(':')
	#	if len(fea) != 7:
	#		return False
	#return True
	#print html
	if 'root:/root:/bin/bash' in html:
		print 'GET'
		return True
	else:
		return False

def load_feature_windows():
	for line in open('lfi-feature-windows.txt').readlines():
		lfi_feature_windows.append(line.strip().lower())

#检测主函数
def check_xss(url, method, headers, targetType=None,targetParam = None, queryDict = {}, \
							postDict = {},payloadsDict = {}, referer = '', \
							user_agent = '', cookie = ''):
	"""xss check """
#判断targetType是否在Referer user_angent cookie之间
#Referer user_agent Cookie
        print 'targetParam : %s' %targetParam
	if targetType in specil_list:
		try:
			if targetType=='cookie':
				return Method_Of_cookie(url,method, headers,targetParam, queryDict = {}, \
								postDict = postDict, payloadsDict=payloadsDict, referer=referer, \
								user_agent=user_agent,cookie=cookie\
								)
			else:
				return Method_Of_referer_user_agent(url,method, headers,targetType,targetParam, queryDict = {}, \
								postDict = postDict, payloadsDict=payloadsDict, referer=referer, \
								user_agent=user_agent,cookie=cookie\
								)
		except Exception,e:
			print str(e)
			print traceback.format_exc() 
#Url
	else:
		try:
			return Method_Of_Url(url,method, headers, targetParam, queryDict =queryDict, \
								postDict = postDict, payloadsDict=payloadsDict)
		except Exception,e:
			print str(e)
			print traceback,format_exc()

def check_lfi(url, method, headers, targetType=None,targetParam = None, queryDict = {}, \
                                                        postDict = {},payloadsDict = {}, referer = '', \
                                                        user_agent = '', cookie = ''):
	retVal = False, '', ''
	cnt = 0
	totalcnt = len(payloadsDict)
	for lfitype in lfitypes:
		# print xsstype
                cnt += 1
                print str(cnt/totalcnt * 100) + '%'
		payloads = payloadsDict[lfitype]
                if method.upper() == 'GET':
                        if queryDict:
                                print '.................It is GET'
                                print 'queryDict are:',queryDict
                                for param in queryDict:
	                        	# print param
                                	# print targetParam
                                	if param != targetParam:
                                		# print 'got ycha..'
                                        	continue
                                	# print 'ok. do it...'
                                	browser = MyBrowser(download_directory = mypath)
                                	flag = False
                                	# print 'payloads..... ', payloads
                                	for payload in payloads:
                                                # print "payload: ", payload
                                                payloadDict = copy.deepcopy(queryDict)
                                                payloadDict[param] = "%s" % (payload)
                                                queryStr = toParamStr(payloadDict)
                                                #print 'payloadDict[param] is:',payloadDict[param]
                                                #print 'payloadDict is:',payloadDict
                                                #拼接了payload的url
                                                reqUrl = '%s?%s' % (url, queryStr)
                                                print 'reqUrl is:',reqUrl
                                                #通过webkit模拟浏览器对该url执行，如果执行时弹框则会被捕获到，触发调用alert函数
                                                # print reqUrl  
                                                browser.attack(reqUrl, 'GET', '', headers)
                                                #print browser.html
						if lfitype == 'windows':
							if check_windows_lfi(browser.html):
								return True, reqUrl, lfitype
						elif lfitype == 'linux':
							if check_linux_lfi(browser.html):
								return True, reqUrl, lfitype
								
                        else:
                                print '......queryDict is null'
                                break
		elif method.upper() == 'POST':
                        print 'it is POST'
                        if postDict:
                        	queryStr = toParamStr(queryDict) if queryDict else ''
                                reqUrl = '%s?%s' % (url, queryStr) if queryStr else url
                                for param in postDict:
                                	if param != targetParam: #如果param与目标参数不匹配，则继续遍历直到匹配后可执行continue后的语句
                                                continue
                                        browser = MyBrowser(download_directory = mypath)
                                        flag = False
                                        for payload in payloads:
                                                print "[payload]: ", payload
                                                payloadDict = copy.deepcopy(postDict)
                                                payloadDict[param] = "%s%s" % (payloadDict[param], payload)
                                                browser.attack(reqUrl, 'POST', payloadDict, headers)
                                                if lfitype == 'windows':
                                                        if check_windows_lfi(browser.html):
                                                                return True, reqUrl, lfitype
                                                elif lfitype == 'linux':
                                                        if check_linux_lfi(browser.html):
                                                                return True, reqUrl, lfitype
                                                if flag:
                                                        print 'break 3...'
                                                        break
			else:
                                print '......postDict is null'
                                break
        return retVal
		

def audit(url, targetType,targetParam, method = 'GET', data = None,\
					referer = '', user_agent = '', cookie = '', headers = {}):
	retVal = False, '', '','',''
	#加载payloadsDict
	payloadsDict = getPayloadsDict()
	payloadsDict_LFI = getPayloadsDict_LFI()
	#解析url参数
	__urlSplit = urlparse.urlsplit(url) 
	__hostnamePort = __urlSplit[1].split(":")
	scheme = __urlSplit[0].strip()
	path = __urlSplit[2].strip()
	hostname = __hostnamePort[0].strip()
	if 2 == len(__hostnamePort):
		try:
			port = int(__hostnamePort[1])
		except Exception, e:
			return retVal
	elif "https" == scheme:
		port = 443
	else:
		port = 80
	reqUrl = "%s://%s%s" % (scheme, hostname, path) \
		if port==80 else "%s://%s:%d%s" % (scheme, hostname, port, path)
	queryDict = toParamDict(__urlSplit[3]) if __urlSplit[3] else {}
	postDict = toParamDict(data) if data else {}
	#print '......................................................................cookie',cookie
	try:
		#进入主函数check_xss检测
		ret, position ,url_payload, xsstype, eventtype = check_xss(reqUrl,method,headers,targetType,targetParam, \
									queryDict, postDict,payloadsDict, \
									referer,user_agent,cookie)
		#进入主函数check_lfi检测
		ret_lfi, url_payload_lfi, lfitype = check_lfi(reqUrl,method,headers,targetType,targetParam, \
                                                                        queryDict, postDict,payloadsDict_LFI, \
                                                                        referer,user_agent,cookie)

	except Exception, e:
		print e
		ret = False
		url_payload = ''
		position = ''
		xsstype = ''   
		eventtype = ''
		ret_lfi = False
		url_payload_lfi = ''
		lfitype = ''
	
	return ret, position, url_payload, xsstype, eventtype, ret_lfi, url_payload_lfi, lfitype


def run(url, method, data = None, targetType=None,targetParam = None, \
				referer = '', user_agent = '', cookie = '',headers={}):
	if targetType!= None and targetType!='':
                print 'run targetParam : %s' %targetParam
		print '[*] Checking %s ...' %url
		print "targetType:",targetType
	else:
		print '[*] Checking %s ...' %url
	ret, position, payload, xsstype, eventtype, ret_lfi, url_payload_lfi, lfitype = audit(url, targetType,targetParam, method,data,referer,user_agent, cookie,headers)
	retVal = []
	if ret:
		ret_targetParam = targetParam if targetParam != None else ''
		print '[+] Found xss! payload: %s' % payload
		if position == 'URL':
			retVal.append([True, method, payload, ret_targetParam, data, referer, xsstype, eventtype])
		elif position == 'data':
			retVal.append([True, method, url, ret_targetParam, payload, referer, xsstype, eventtype])
		elif position == 'referer':
			retVal.append([True, method, url, ret_targetParam, payload, referer, xsstype, eventtype])
		elif position == 'user_agent':
			retVal.append([True, method, url, ret_targetParam, payload, user_agent, xsstype, eventtype])
		elif position == 'cookie':
			retVal.append([True, method, url, ret_targetParam, payload, cookie, xsstype, eventtype])
	else:
		print '[*] XSS not found'
		retVal.append([False])

	if ret_lfi:
		ret_targetParam = targetParam if targetParam != None else ''
		print '[+] Found lfi! payload: %s' %url_payload_lfi
		retVal.append([ret_lfi, method, url_payload_lfi, lfitype])
	else:
		print '[*] LFI not found'
		retVal.append([False])
	
	return retVal

def getPayloadsDict():
	#需要对pay进行编码，用于绕过waf等防护
	#retVal = {xsstype:[]}, i.e., {'alert' : ['alert(1)', 't="ale"+"rt"+']}
	xssposition = 'on'
	thehtml = ''
	jpayload = ''
	xsstypes = ['alert','prompt', 'confirm', 'throw'] 
	eventtypes = ['auto', 'event']
	retVal = {'auto':{}, 'event':{}}
	payloadFileHtml = os.path.join(os.path.dirname(__file__), 'xss-payloads-html-%s.txt')
	
	#print payloadsHtml
	for eventtype in eventtypes:
		payloadsHtml = getFileItems(payloadFileHtml % eventtype)
		for item in xsstypes:
			retVal[eventtype][item] = []
			payloadFilefortype = os.path.join(os.path.dirname(__file__), 'xss-payloads-%s.txt' % item)
			payloadsfortype = getFileItems(payloadFilefortype)
			for i in payloadsfortype:
				for j in payloadsHtml:
					if j.find('*noton') <> -1:
						xssposition = 'other'
						thehtml = j.rstrip('*noton')	
					else:
						xssposition = 'on'
						thehtml = j
					#print j, xssposition
					#jpayload = xss_encode(i, xssposition)
                                        jpayload = i # 测试用的 XQQ
					#print jpayload
					retVal[eventtype][item].append(thehtml % jpayload)
	#print retVal
	return retVal

def getPayloadsDict_LFI():
        #需要对pay进行编码，用于绕过waf等防护
        #retVal = {xsstype:[]}, i.e., {'alert' : ['alert(1)', 't="ale"+"rt"+']}
        thehtml = ''
        jpayload = ''
        lfitypes = ['windows','linux']
        retVal = {'windows':[], 'linux':[]}
        payloadFile = os.path.join(os.path.dirname(__file__), 'lfi-payloads-%s.txt')

        #print payloadsHtml
        for lfitype in lfitypes:
                payloadsHtml = getFileItems(payloadFile % lfitype)
                retVal[lfitype] = []
                for j in payloadsHtml:
                       	#print j, xssposition
                        #jpayload = xss_encode(j, "on")
                        jpayload = j # 测试用的 XQQ
                        #print jpayload
                        retVal[lfitype].append(jpayload)
        # print retVal
        return retVal


def xss_encode(payload, xssposition):
	#xssposition： 
	#javascript 在事件里的如：onclick=%s, 可以进行html编码先，否则只走下一步
	#默认urlencode: + to %2b, ' '(blank) to %20
	if xssposition == 'on':
		payload = to_html(payload)
		payload = payload.replace('&', '%26')
		payload = payload.replace('#', '%23')

	payload = payload.replace('+','%2b')
	return payload

def to_html(payload):
	retVal = ''
	for letter in payload:
		retVal += '&#%d;' % ord(letter)
	return retVal
#检查文件正确性
def checkFile(filename):
	"""
	@param filename: filename to check if it exists.
	@type filename: C{str}
	"""

def getFileItems(filename, commentPrefix = '#'):
	retVal = []
	checkFile(filename)
	ifile = open(filename, 'r')
	for line in ifile.readlines():
		if commentPrefix:
			if line.find(commentPrefix) != -1:
				line = line[:line.find(commentPrefix)]
		line = line.strip()
		if line:
			retVal.append(line)
	#print retVal
	return retVal

def toParamStr(param_dict):
	params = '&'.join([k + '=' + v for k, v in param_dict.items()])
	return params

def toParamDict(params):
	param_dict = {}
	if not params:
		return param_dict
	try:
		split_params = params.split('&')
		for element in split_params:
			elem = element.split("=")
			if len(elem) >= 2:
				parameter = elem[0].replace(" ", "")
				value = "=".join(elem[1:]) #a.php?id=1&id=2&id=3
				param_dict[parameter] = value
	except Exception,e:
		pass
	return param_dict

def run_from_file(input_file, out_file, debug= 'False'):
	if not debug or debug == 'False':
		sys.stdout = NullStdOut()
	progress = 0
	scaned_num = 0
	total_num = stat_line_number(input_file)
	progress_file = os.path.join(os.path.split(out_file)[0], 'progress.log')
	file_reader = csv.reader(file(input_file, 'rb'))
	for line in file_reader:
		try:
			url = line[0]
			param = line[1]
			method = line[2].upper()
			url_split = urlparse.urlsplit(url)
			query = url_split[2]
			data = query
			result = run(url, method, data= data, targetParam = param)
			out_put_result(out_file, result)
		except Exception,e:
			print str(e)
			print traceback.format_exc()
		scaned_num += 1
		write_progress(progress_file, int(100*(float(scaned_num)/total_num)))
	write_progress(progress_file, 100)

def run_from_sql():
        getPayloadsDict()
	conn= MySQLdb.connect(
        	host='127.0.0.1',
        	port = 3306,
        	user='root',
        	passwd='000000',
        	db ='crawl',
        )
	cur = conn.cursor()
	sqli = "select rawurl, query, method from result_urls"
	cur.execute(sqli)
	data = cur.fetchone()
	while data != None:
		# print data
		query = json.loads(data[1])
		for i in query:
			url = data[0]
			method = data[2]
			targetParam = i
			referer = ''
			user_agent = ''
			cookie = ''
			result = run(url=url, method=method, targetParam=targetParam, referer=referer, user_agent=user_agent, cookie=cookie)
			print result
			if result[0][0]:
				sqli = "insert into xss_urls(url, payload) values('%s', '%s')"%(url, result[0][2])
				cur.execute(sqli)
				conn.commit()
			if result[1][0]:
				sqli = "insert into lfi_urls(method, url, payload, type ) values('%s', '%s', '%s', '%s')"%(method, url, result[1][2], result[1][3])
				cur.execute(sqli)
				conn.commit()
		#print data
		data = cur.fetchone()	

def test(test):
	if test == 'test':
		getPayloadsDict()
	else:
		url="http://demo.aisec.cn/demo/aisec/js_link.php?id=1&msg=abc"
		targetParam = 'msg'
		method = 'GET'
		data = None
		refer = ''
		user_agent = ''
		cookie = ''
                print 'test targetParam : %s' %targetParam
		result = run(url=url, method=method, data=data, targetParam=targetParam, referer=refer, user_agent=user_agent, cookie=cookie)
		print result	
	
def toParamDictCookie(params):
	param_dict = {}
	if not params:
		return param_dict
	try:
		split_params = params.split(';')
		for element in split_params:
			elem = element.split("=")
			if len(elem) >= 2:
				parameter = elem[0].replace(" ", "")
				value = "=".join(elem[1:]) #a.php?id=1&id=2&id=3
				param_dict[parameter] = value
	except Exception,e:
		pass
	return param_dict

if __name__ == '__main__':
		
	usage = "python %prog [options]"
	parser = OptionParser(usage, version = "%prog 1.0") #内建的模块用于处理命令行参数;
	parser.add_option("-v", action = "store_true", dest = "verbose", default = False,
					  help = u"在屏幕上打印详细信息")
	parser.add_option("-t", action = "store_true", dest = "test", default = False,
					  help = u"执行test自测试") 
	target = OptionGroup(parser, "Target", u"检测目标")
	target.add_option("-u", "--url", dest = "url",
					  help = u"target url to be checked")
	target.add_option("-d", "--data", dest = "data",
					  help = u"http post data")
	target.add_option("-p", "--param", dest = "param",
					  help = u"指定检测的参数")
	target.add_option("-y", "--type", dest = "type",
					  help = u"指定检测的类型")
	target.add_option("-i", "--input", dest = "input_file",
					  help = u"url从文件批量输入")
	target.add_option("-o", "--output", dest = "output_file",
					  help = u"结果输出到文件")
	target.add_option("-g", "--debug", dest = "debug",
					  help = u"是否输出调试信息 True/False")
        target.add_option("-s", "--sql", action = "store_true", dest = "sql", default = False,
                                          help = u"从数据库中读取并检测")

	request = OptionGroup(parser, "Request", u"需要预处理的参数")
	request.add_option("--referer", dest = "referer",default = "",
					  help = u"HTTP Referer header")
	request.add_option("--user_agent", dest = "agent", default = "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)",
					  help = u"HTTP User_Agent header")
	request.add_option("--cookie", dest="cookie",default = "",
					  help = u"HTTP Cookie header")

	parser.add_option_group(target)
	parser.add_option_group(request)
	print '======parser========', parser.values
	(options, args) = parser.parse_args()   #解析命令行的参数, 并将结果传给options
	print '..........options~~~:',options
	print '..........args~~~:',args
	#1. options , 这是一个对象(optpars.Values)，保存命令行参数值。只要知道命令行参数名,如file，就可以访问其对应的值：options.file。 
	#2. args , 一个由 positional arguments 组成的列表
	try:
	#while True:

		load_feature_windows()	

		if options.test:
			test(options.test)
                elif options.sql:
                        run_from_sql()
		else:
			if options.input_file and options.output_file:
				run_from_file(options.input_file, options.output_file, options.debug)
			else:
				url = options.url
				data = options.data
				targetType =options.type
				# print 'targetType is:',targetType
				print 'options.param:',options.param
				method = 'POST' if data else 'GET'
				if not url:
					parser.print_help()
				else:
					print '......:',data
					print '...................`````````:',options.param
					if data!='' and data!=None:
						try:
							if not options.param:
								print u'\n请指定检测URL的参数 eg: -p id. -h 查看帮助'
							else:
								result = run(url, method, data,targetType,targetParam = options.param, referer = options.referer, user_agent = options.agent, cookie = options.cookie)
								print result
						except Exception,e:
							print str(e)
							print traceback.format_exc()
					else:
						result = run(url, method, data,targetType,targetParam = options.param, referer = options.referer, user_agent = options.agent, cookie = options.cookie)
						print result
		#break
	except Exception, e:
		print e
		pass
