# from django.urls import url
from django.conf.urls import  url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_elements_from_db$', views.get_elements_from_db, name='get_elements_from_db'),
    url(r'^get_bugs_from_db$', views.get_bugs_from_db, name='get_bugs_from_db'),
    url(r'^get_more_from_db$', views.get_more_from_db, name='get_more_from_db'),
    url(r'^start_scan$', views.start_scan, name='start_scan'),
]
