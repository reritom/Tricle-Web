from django.conf.urls import url
from django.contrib.auth import views as auth_views
from API import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.info, name='info'),
    url(r'^core/$', views.core, name='core'),
    url(r'^core/dau/$', views.dau, name='dau'),
]
