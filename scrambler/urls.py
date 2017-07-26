from django.conf.urls import url
from django.contrib.auth import views as auth_views
from scrambler import views

app_name = 'scrambler'

urlpatterns = [
    url(r'^start/$', views.StartPage, name='start'),
    url(r'^account/$', views.AccountPage, name='account'),
    url(r'^(?P<hash>\w+)/$', views.load_url, name="url"),
    url(r'^down/(?P<hash>\w+)/$', views.download_url, name="down"),
]
