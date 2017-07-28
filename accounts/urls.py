from django.conf.urls import url
from django.contrib.auth import views as auth_views
from accounts import views

app_name = 'accounts'

urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^signup/$', views.SignUp.as_view(), name='signup'),
    url(r'^thanks/$', views.ThanksPage, name='thanks'),
    url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    url(r'^ajax/validate_email/$', views.validate_email, name='validate_email'),
]
