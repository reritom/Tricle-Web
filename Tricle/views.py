from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
# Create your views here.

def index(request):
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    return render(request, "index.html", {"num_vis" : request.session['num_visits']})

def stats(request):
    return render(request, "global.html")

def ScramRedirect(request):
    return HttpResponseRedirect("/")

class ContactPage(TemplateView):
    template_name = 'contact.html'

class PrivacyPage(TemplateView):
    template_name = 'privacy.html'

class TestPage(TemplateView):
    template_name = 'test.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'

class AboutPage(TemplateView):
    template_name = 'about.html'
