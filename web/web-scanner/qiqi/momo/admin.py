# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from momo import models

# Register your models here.


# admin.site.register(models.RunoobTbl)
# admin.site.register(models.MomoTest)

admin.site.register(models.result_urls)
admin.site.register(models.sql_urls)
admin.site.register(models.xss_urls)
admin.site.register(models.file_urls)
admin.site.register(models.lfi_urls)
admin.site.register(models.crawl_urls)
