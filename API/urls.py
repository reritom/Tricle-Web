from django.conf.urls import url
from django.contrib.auth import views as auth_views
from API import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.info, name='info'),
    url(r'^core/$', views.core, name='core'),
    url(r'^core/dau/$', views.dau, name='dau'),
    url(r'^remote/$', views.remote, name='rm'),    
    url(r'^remote/(?P<userkey>\w+)/(?P<uri>\w+)/k1=(?P<k1>\w+)&k2=(?P<k2>\w+)&k3=(?P<k3>\w+)&mode=(?P<mode>\w+)/$', views.remoteproc, name='remote'),
]
