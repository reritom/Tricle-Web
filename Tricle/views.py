from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

def index(request):
    print(request.session)
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    return render(request, "index.html", {"num_vis" : request.session['num_visits']})

def stats(request):
    return render(request, "global.html")

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
