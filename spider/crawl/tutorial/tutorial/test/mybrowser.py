#encoding=utf8

from PyQt4.QtWebKit import QWebView, QWebPage, QWebFrame
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl

import sys
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == "__main__":
    url = "http://blog.csdn.net/fron_csl/article/details/46400023"
   
    app = QApplication([]) 
    webview = QWebView()
    webpage = QWebPage()
    webview.setPage(webpage)
    wf = webpage.currentFrame()
    webview.load(QUrl(url))
    print wf.toHtml()
