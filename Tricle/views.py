from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings
from scrambler.models import ExpiringURL, Profile, ExpiredURL, DailyLedger

from datetime import datetime, timedelta

import os
import shutil
# Create your views here.

def byteconvert(val):
    '''Converts bytes into a readable format'''

    if val > 1000000000000:
        return str(val/1000000000000) + " TB"
    elif val > 1000000000:
        return str(val/1000000000) + " GB"
    elif val > 1000000:
        return str(val/1000000) + " MB"
    elif val > 1000:
        return str(val/1000) + " KB"
    else:
        return str(val) + " Bytes"

def delete_dir(url):
    '''
    If a tempurl directory is exists, delete it and its contents.
    '''

    if 'temp' in os.listdir(settings.MEDIA_ROOT):
        if url in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
            url_dir = os.path.join(settings.MEDIA_ROOT, 'temp', url)
            shutil.rmtree(url_dir)
            return
    else:
        return

def index(request):
    '''
    User login redirects to index, on redirect,
    create a profile object for the user.
    '''

    if request.user.is_authenticated():
        profile, check = Profile.objects.get_or_create(user=request.user)
        profile.save()

    return render(request, "index.html")

def updateLastLogin(sender, user, request, **kwargs):
    '''
    When a user logs in, the profile is collected, last login is updated.
    Daily ledger is created or collected, login count is incremented.
    If it is the users first login of the day, DAU is incremented.
    '''

    profile, check = Profile.objects.get_or_create(user=request.user)
    daily_ledger, check = DailyLedger.objects.get_or_create(date=timezone.now().date())
    daily_ledger.login_count += 1
    daily_ledger.save()

    if profile.last_login.date() != timezone.now().date():
        #first login of the day
        daily_ledger.dau += 1

    profile.last_login = timezone.now()
    profile.save()

user_logged_in.connect(updateLastLogin)

def stats(request):
    '''
    This view extracts all the app data for viewing.
    '''

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
            context['todays_uploads_count'] += 1
            context['todays_file_count'] += expurl.number_of_files

            if expurl.mode == 'Scramble':
                context['todays_s_count'] += expurl.number_of_files
            else:
                context['todays_u_count'] += expurl.number_of_files

    for expurl in ExpiredURL.objects.all():
        if expurl.created.day == datetime.today().day:
            context['todays_uploads_count'] += 1
            context['todays_file_count'] += expurl.number_of_files

            if expurl.mode == 'Scramble':
                context['todays_s_count'] += expurl.number_of_files
            else:
                context['todays_u_count'] += expurl.number_of_files


    if len(User.objects.all()) > 0:
        for user in User.objects.all():
            if user.last_login.day == datetime.today().day:
                context['dau'] += + 1

            profile, check = Profile.objects.get_or_create(user=user)
            context['total_file_bytes'] += profile.total_size_of_uploaded_images
            context['total_scrambles'] += profile.scramble_count
            context['total_unscrambles'] += profile.unscramble_count
            context['total_file_count'] += profile.total_file_count

    context['total_file_bytes'] = byteconvert(context['total_file_bytes'])

    return render(request, "global.html", context)

def cleanup(request):
    '''
    Go through expiring, convert to expired, remove from expiring, make sure dir is deleted
    This needs to be performed at least daily. /iaw
    '''

    expiring_list = ExpiringURL.objects.all()

    for expiring in expiring_list:
        if expiring.expired == True:
            #move from expiringurls to expiredurls
            #delete dir if its still there
            delete_dir(expiring.url)
            expiredurl, created = ExpiredURL.objects.get_or_create(url=expiring.url)
            if created == True:
                expiredurl.created = expiring.created
                expiredurl.number_of_files = expiring.number_of_files
                expiredurl.mode = expiring.mode
                expiredurl.user_name = expiring.user_name
                expiredurl.save()
            expiring.delete()
            pass

        expiration = expiring.created + timedelta(minutes=settings.EXPIRATION_TIME_LIMIT)

        if timezone.now() > expiration:
            #url has expired, mark as expired, delete dirs, redirect to homepage
            expiring.expired = True
            expiring.save()

            delete_dir(expiring.url)

            expiredurl, created = ExpiredURL.objects.get_or_create(url=expiring.url)
            if created == True:
                expiredurl.created = expiring.created
                expiredurl.number_of_files = expiring.number_of_files
                expiredurl.mode = expiring.mode
                expiredurl.user_name = expiring.user_name
                expiredurl.save()
            expiring.delete()
            #move to expiredurls

    '''
    go through dir, if not in expiring or expired, delete dir
    '''

    for tempurl in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
        if not ExpiringURL.objects.filter(url=tempurl).exists():
            delete_dir(tempurl)

    '''
    create daily ledger if needed
    '''

    daily_ledger, check = DailyLedger.objects.get_or_create(date=timezone.now().date())

    return HttpResponseRedirect("/")

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
