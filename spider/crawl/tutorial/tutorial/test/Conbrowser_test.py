#encoding=utf8

import scrapy
import spynner

if __name__ == "__main__":
    url = "http://demo.aisec.cn/demo/aisec/"
    browser = spynner.Browser()
    browser.load(url=url)
    html = browser.html
    elements = browser.webframe.findAllElements('a')
    print type(elements)
    print len(elements.toList())
    for e in elements.toList():
        print e.tagName() 
        print e.prefix()
        # QS = e.attribute('href')
        # print type(QS), QS
        browser.wk_click_element(e) 
    hh = scrapy.Selector(text=html)
    for i in hh.xpath('//*[@onclick]'):
        pass
        # print i
        # browser.wk_click_element(i)
    print hh
