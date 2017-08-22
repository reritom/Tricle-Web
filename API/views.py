from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from scrambler.models import ExpiringURL, Profile, ExpiredURL, DailyLedger

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


def core(request):
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
    return JsonResponse(context)

def dau(request):
    context = dict()
    context['dau'] = 0

    if len(User.objects.all()) > 0:
        for user in User.objects.all():
            if user.last_login.day == datetime.today().day:
                context['dau'] += + 1
                
    return JsonResponse(context)

def info(request):
    return HttpResponse("Dis is info page")
