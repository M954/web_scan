# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import MySQLdb
import qiqi.settings

# class MomoTest(models.Model):
#     runoob_title = models.CharField(max_length=20)
#     runoob_author = models.CharField(max_length=20)
#     submission_date = models.CharField(max_length=20)
#     runoob_id = models.CharField(max_length=100, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'momo_test'
#
#
# class RunoobTbl(models.Model):
#     runoob_id = models.AutoField(primary_key=True)
#     runoob_title = models.CharField(max_length=100)
#     runoob_author = models.CharField(max_length=40)
#     submission_date = models.DateField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'runoob_tbl'
#
#     def __str__(self):
#         return self.runoob_title

class result_urls(models.Model):
    domain = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    port = models.IntegerField()
    method = models.CharField(max_length=10)
    query = models.CharField(max_length=500)
    data = models.CharField(max_length=5000)
    rawurl = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'result_urls'

    def __str__(self):
        return self.rawurl

class sql_urls(models.Model):
    url = models.CharField(max_length=1000)
    dbms = models.CharField(max_length=100)
    dbms_version = models.CharField(max_length=100)
    data = models.CharField(max_length=10000)

    class Meta:
        managed = False
        db_table = 'sql_urls'

    def __str__(self):
        return self.url

class xss_urls(models.Model):
    url = models.CharField(max_length=500)
    payload = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'xss_urls'

    def __str__(self):
        return self.url

class file_urls(models.Model):
    domain = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'file_urls'

    def __str__(self):
        return self.url

class lfi_urls(models.Model):
    method = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    payload = models.CharField(max_length=1000)
    type = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'lfi_urls'

    def __str__(self):
        return self.url

class crawl_urls(models.Model):
    url = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'crawl_urls'

    def __str__(self):
        return self.url
