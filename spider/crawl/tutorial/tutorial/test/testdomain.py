#encoding=utf8

import spynner
import urllib2

domain_suffix = []

for i in open('domain_filter').readlines():
    domain_suffix.append(i.strip())

def get_domain(url):
    tmp = url.split('/')
    tmp = tmp[2].split('.')
    cnt = 1
    for t in tmp:
        if t in domain_suffix:
            cnt += 1
    return '.'.join(tmp[-cnt:])

if __name__ == "__main__":
    url = 'http://www.linyi.gov.cn/'
    print domain_suffix
    print get_domain(url)
    # browser = spynner.Browser()
    # browser.load(url)
    # print browser.html

    # response = urllib2.urlopen(url)
    # print response.read()
