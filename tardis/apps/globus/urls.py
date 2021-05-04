from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^accessible-hosts/$', views.get_accessible_hosts),
    url(r'^$', views.globus_initiate, name='index'),
]
