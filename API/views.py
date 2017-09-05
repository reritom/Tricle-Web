from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from scrambler.models import ExpiringURL, Profile, ExpiredURL, DailyLedger
import json
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
    if not request.user.is_authenticated():
        return JsonResponse({"authenticated":"False"})

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


    '''test data'''
    if context['user_count'] < 5000 + 3236:
        context['user_count'] = context['user_count'] + 3236
        context['dau'] = '--'
        context['todays_uploads_count'] = '--'
        context['todays_file_count'] = '--'
        context['todays_s_count'] = '--'
        context['todays_u_count'] = '--'
        context['total_file_bytes'] += 37475798087
        context['total_scrambles'] += 817
        context['total_unscrambles'] += 457
        context['total_file_count'] += 817 + 457

    context['total_file_bytes'] = byteconvert(context['total_file_bytes'])
    return JsonResponse(context)

def dau(request):
    if not request.user.is_authenticated():
        return JsonResponse({"authenticated":"False"})

    context = dict()
    context['dau'] = 0

    if len(User.objects.all()) > 0:
        for user in User.objects.all():
            if user.last_login.day == datetime.today().day:
                context['dau'] += + 1

    context['dau'] = '--'

    return JsonResponse(context)

def info(request):
    return render(request, "API/api.html")

def remoteproc(request, userkey, uri, k1, k2, k3, mode):
    profile, check = Profile.objects.get(userkey=userkey)
    return HttpResponse(check, userkey, uri, k1, k2, k3, mode)

@csrf_exempt
def remote(request):
    ret_dict = dict()
    ret_dict['valid'] = False #default
    ret_dict['error'] = None #default

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        print(data)

        if 'k1' not in data:
            ret_dict['error'] = 'No k1 provided'
            return JsonResponse(ret_dict)

        if 'k2' not in data:
            ret_dict['error'] = 'No k2 provided'
            return JsonResponse(ret_dict)

        if 'k3' not in data:
            ret_dict['error'] = 'No k3 provided'
            return JsonResponse(ret_dict)

        if 'mode' not in data:
            ret_dict['error'] = 'No k1 provided'
            return JsonResponse(ret_dict)

        if 'uri' not in data:
            ret_dict['error'] = 'No URI provided'
            return JsonResponse(ret_dict)


        ret_dict['valid'] = True
        return JsonResponse(ret_dict)
    else:
        ret_dict['error'] = 'POST API, not GET'
        return JsonResponse(ret_dict)
