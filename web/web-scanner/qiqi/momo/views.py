# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from momo.models import *
import json
import os

def index(request):
    return render(request, 'index.html')

# def get_elements_from_db(request):
#     runoob=list(RunoobTbl.objects.values('runoob_title', 'runoob_author', 'submission_date'))
#     print(runoob)
#     elements = dict(runoob=runoob)
#     return JsonResponse(elements)

def start_scan(request):
    searchurl = request.GET.get('url');
    print searchurl
    if 'http://' in searchurl or 'https://' in searchurl :
        os.system('sh /home/xuqinqi/web/web-scanner/qiqi/momo/test.sh');
    else:
        os.system('sh /home/xuqinqi/web/web-scanner/qiqi/momo/test2.sh');
    return HttpResponse('finish');

def get_dir(dict_data, path_list):
    if len(path_list) <= 0:
        return dict_data
    tmp = dict_data.get(path_list[0], {})
    # print '[before]\t' + path_list[0] + '\t' + str(tmp)
    dict_data[path_list[0]] = get_dir(tmp, path_list[1:])
    # print '[after  ]\t' + path_list[0] + '\t' + str(dict_data[path_list[0]])
    # print path_list[0] + '[before]\t' + str(tmp) + '[after  ]\t' + str(dict_data[path_list[0]])
    return dict_data

def get_elements_from_db(request):
    curl = list(crawl_urls.objects.values('url'))
    # print curl
    ret_val = {}
    for i in curl:
        # print i
        tmp_url = i['url'].split('/')
        level1 = '/'.join(tmp_url[0:3])
        ret_val[level1] = get_dir(ret_val.get(level1, {}), tmp_url[3:])
    # print(ret_val)
    return JsonResponse(ret_val)

def get_bugs_from_db(request):
    print('start bugs')
    ret_val = []
    cnt = 1
    searchtype = request.GET.get('type')
    if searchtype == 'SQL injection' or searchtype == 'all':
        surl = list(sql_urls.objects.values('url'))
        for url in surl:
            tmp = {}
            tmp['Id'] = cnt
            tmp['Name'] = 'SQL injection'
            tmp['Description'] = url['url']
            cnt += 1
            ret_val.append(tmp)
    if searchtype == 'XSS' or searchtype == 'all':
        xurl = list(xss_urls.objects.values('url'))
        for url in xurl:
            tmp = {}
            tmp['Id'] = cnt
            tmp['Name'] = 'XSS'
            tmp['Description'] = url['url']
            cnt += 1
            ret_val.append(tmp)
    if searchtype == 'Senstive file' or searchtype == 'all':
        furl = list(file_urls.objects.values('url'))
        for url in furl:
            tmp = {}
            tmp['Id'] = cnt
            tmp['Name'] = 'Senstive file'
            tmp['Description'] = url['url']
            cnt += 1
            ret_val.append(tmp)
    if searchtype == 'File inclusion' or searchtype == 'all':
        lurl = list(lfi_urls.objects.values('url'))
        for url in lurl:
            tmp = {}
            tmp['Id'] = cnt
            tmp['Name'] = 'File inclusion'
            tmp['Description'] = url['url']
            cnt += 1
            ret_val.append(tmp)
    # print(ret_val)
    return JsonResponse(ret_val, safe=False)

def get_more_from_db(request):
    # os.system('sh /home/xuqinqi/web/web-scanner/qiqi/momo/test.sh')
    ret_val = {}
    searchtype = request.GET.get('type')
    searchurl = request.GET.get('url')
    print searchtype, searchurl
    if searchtype == 'SQL injection':
        data = list(sql_urls.objects.filter(url=searchurl).values('dbms', 'dbms_version', 'data'))
        # print data[0]['data']
        data[0]['data'] = data[0]['data'].replace('\n', '<br />')
        ret_val = data[0]
    elif searchtype == 'XSS':
        data = list(xss_urls.objects.filter(url=searchurl).values('payload'))
        ret_val = data[0]
    elif searchtype == 'Senstive file':
        data = list(file_urls.objects.filter(url=searchurl).values('domain', 'url', 'status'))
        ret_val = data[0]
    elif searchtype == 'File inclusion':
        data = list(lfi_urls.objects.filter(url=searchurl).values('payload'))
        ret_val = data[0]
    print ret_val
    return JsonResponse(ret_val)
