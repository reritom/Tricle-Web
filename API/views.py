from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from scrambler.models import ExpiringURL, Profile, ExpiredURL, DailyLedger, RemoteToken, ExpiredToken, RemoteInteraction
from scrambler.scramble import scrambler
import json, io
from PIL import Image
from hashlib import sha1
from base64 import decodestring
import base64
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


@csrf_exempt
def remote(request):
    ret_dict = dict()
    ret_dict['valid'] = False #default
    ret_dict['error'] = None #default

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            ret_dict['error'] = 'Error trying to decode posted data. Make sure it is in JSON format'
            return JsonResponse(ret_dict)


        if 'userkey' not in data:
            ret_dict['error'] = 'No userkey provided'
            return JsonResponse(ret_dict)

        try:
            profile = Profile.objects.get(userkey=data['userkey'])
        except Profile.DoesNotExist:
            ret_dict['error'] = 'Unrecognised userkey'
            return JsonResponse(ret_dict)

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
            ret_dict['error'] = 'No mode provided'
            return JsonResponse(ret_dict)

        if 'uri' not in data:
            ret_dict['error'] = 'No uri provided'
            return JsonResponse(ret_dict)

        if 'token' not in data:
            ret_dict['error'] = 'No token provided'
            return JsonResponse(ret_dict)

        try:
            rmtoken = RemoteToken.objects.get(token=data['token'])
        except:
            try:
                exptoken = ExpiredToken.objects.get(token=data['token'])
            except:
                ret_dict['error'] = 'Expired token - visit your account page for a new one'
                return JsonResponse(ret_dict)

            ret_dict['error'] = 'Invalid token - visit your account page for a new one'
            return JsonResponse(ret_dict)

        if rmtoken.uses >= settings.API_TOKEN_LIMIT:
            rmtoken.expire()
            ret_dict['error'] = 'Expired token - visit your account page for a new one'
            return JsonResponse(ret_dict)

        if rmtoken.user_name != profile.user.username:
            ret_dict['error'] = 'Token user and userkey user do not match'
            return JsonResponse(ret_dict)


        '''Check the mode'''

        if data['mode'].lower() == "scramble" or data['mode'].lower() == "scram" or data['mode'].lower() == "s":
            data['mode'] = 'Scramble'

        elif data['mode'].lower() == "unscramble" or data['mode'].lower() == "unscram" or data['mode'].lower() == "u":
            data['mode'] = 'Unscramble'

        else:
            ret_dict['error'] = 'mode needs to be scramble or unscramble'
            return JsonResponse(ret_dict)


        '''create token interaction model: user, mode, day'''

        rmid = create_api_id(profile.user.username)
        token_interaction, token_check = RemoteInteraction.objects.get_or_create(rm_id=rmid, user_name=profile.user.username, mode=data['mode'])
        daily_ledger, check = DailyLedger.objects.get_or_create(date=timezone.now().date())

        profile.api_requests += 1
        daily_ledger.api_requests +=1

        if data['mode'] == 'Scramble':
            profile.api_scrams += 1
            daily_ledger.api_scrams += 1
        else:
            profile.api_unscrams += 1
            daily_ledger.api_unscrams += 1

        rmtoken.uses += 1

        rmtoken.save()
        profile.save()
        daily_ledger.save()



        try:
            image = io.BytesIO(base64.b64decode(data['uri']))
            image = Image.open(image)
            #image.show()
        except:
            ret_dict['error'] = 'Error converting b64 string to PIL image'
            return JsonResponse(ret_dict)


        try:
            final = scrambler(data['mode'], data['k1'], data['k2'], data['k3'], image)
        except:
            ret_dict['error'] = 'Scrambling error'
            return JsonResponse(ret_dict)

        #final.show()

        try:
            buffer = io.BytesIO()
            final.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue())
        except:
            ret_dict['error'] = 'URI return buffer error'
            return JsonResponse(ret_dict)

        ret_dict['uri'] = img_str.decode('utf-8')

        ret_dict['valid'] = True
        return JsonResponse(ret_dict)
    else:
        ret_dict['error'] = 'POST API, not GET'
        return JsonResponse(ret_dict)


def create_api_id(user):
    time = str(datetime.now().isoformat())
    hashkey = (user + time).encode("UTF-8")

    userhash = user.encode("UTF-8")
    userhash = sha1(userhash).hexdigest()[:10]

    otherhash = sha1(hashkey).hexdigest()[:20]

    rmid = str(otherhash) + str(userhash)[::-1]

    try:
        interaction = RemoteInteraction.objects.get(rm_id=rmid)
        return create_api_id(user)
    except:
        return rmid #remote id
