# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = "tardis.apps.globus"
urlpatterns = [
    url(r'^accessible-hosts/$', views.get_accessible_hosts),
    url(r'^$', views.globus_initiate, name='index'),
]
