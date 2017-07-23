from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.utils import timezone
from scrambler.models import ExpiringURL, Profile

from datetime import datetime
# Create your views here.

def index(request):
    if request.user.is_authenticated():
        profile, check = Profile.objects.get_or_create(user=request.user)
        profile.save()

    return render(request, "index.html")

def updateLastLogin(sender, user, request, **kwargs):
     profile, check = Profile.objects.get_or_create(user=request.user)
     profile.last_login = timezone.now()
     profile.save()

user_logged_in.connect(updateLastLogin)

def stats(request):

    context = dict()

    context['user_count'] = len(User.objects.all())
    context['todays_uploads_count'] = 0
    context['todays_file_count'] = 0
    context['todays_s_count'] = 0
    context['todays_u_count'] = 0
    context['dau'] = 0
    context['total_file_bytes'] = 0
    context['total_scrambles'] = 0
    context['total_unscrambles'] = 0
    context['total_file_count'] = 0

    for expurl in ExpiringURL.objects.all():
        if expurl.created.day == datetime.today().day:
            context['todays_uploads_count'] = context['todays_uploads_count'] + 1
            context['todays_file_count'] = context['todays_file_count'] + expurl.number_of_files

            if expurl.mode == 'Scramble':
                context['todays_s_count'] = context['todays_s_count'] + expurl.number_of_files
            else:
                context['todays_u_count'] = context['todays_u_count'] + expurl.number_of_files

    if len(User.objects.all()) > 0:
        for user in User.objects.all():
            print(user)
            if user.last_login.day == datetime.today().day:
                context['dau'] = context['dau'] + 1

            profile, check = Profile.objects.get_or_create(user=user)
            context['total_file_bytes'] = context['total_file_bytes'] + profile.total_size_of_uploaded_images
            context['total_scrambles'] = context['total_scrambles'] + profile.scramble_count
            context['total_unscrambles'] = context['total_unscrambles'] + profile.unscramble_count
            context['total_file_count'] = context['total_file_count'] + profile.total_file_count



    return render(request, "global.html", context)

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
