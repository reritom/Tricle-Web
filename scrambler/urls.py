from django.conf.urls import url
from django.contrib.auth import views as auth_views
from scrambler import views

app_name = 'scrambler'

urlpatterns = [
    url(r'^start/$', views.StartPage, name='start'),
    url(r'^account/$', views.AccountPage.as_view(), name='account'),
]
