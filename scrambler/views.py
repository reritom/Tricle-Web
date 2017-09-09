from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Profile, ExpiringURL, ExpiredURL, DailyLedger, RemoteToken
from .forms import ScrambleForm
from .scramble import scrambler

from datetime import datetime, timedelta
from hashlib import sha1
from pathlib import Path
import os
import pickle
import shutil

from PIL import Image
import zipfile

'''
json respond download link which calls view which returns httpresponse.
when json respondes, change download button.
'''

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
    #check if dir is present, delete if it is
    if 'temp' in os.listdir(settings.MEDIA_ROOT):
        if url in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
            url_dir = os.path.join(settings.MEDIA_ROOT, 'temp', url)
            shutil.rmtree(url_dir)
            return
    else:
        return

def expire_url(url):
    delete_dir(url)
    urlobj = ExpiringURL.objects.get(url=url)
    expiredurl, created = ExpiredURL.objects.get_or_create(url=urlobj.url)
    if created == True:
        expiredurl.created = urlobj.created
        expiredurl.number_of_files = urlobj.number_of_files
        expiredurl.mode = urlobj.mode
        expiredurl.user_name = urlobj.user_name
        expiredurl.save()
    urlobj.delete()

def done_url(request, hash):
    url = hash

    if not ExpiringURL.objects.filter(url=url).exists():
        #url doesnt exist, so redirect
        return HttpResponseRedirect('/')

    expire_url(url)
    return HttpResponseRedirect('/')

    pass

def download_url(request, hash):
    ##check if user is correct user for viewing this
    url = hash
    if not ExpiringURL.objects.filter(url=url).exists():
        #url doesnt exist, so redirect
        return HttpResponseRedirect('/')


    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    urlobj = ExpiringURL.objects.get(url=url)

    profile, check = Profile.objects.get_or_create(user=request.user)

    if profile.last_login > urlobj.created:
        #to prevent stolen credentials being used to download data after the legit user
        #has uploaded it
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')

    if urlobj.down_count >= settings.DOWNLOAD_LIMIT:
        #to limit number of download attempts, for security
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')
    else:
        urlobj.down_count += 1
        urlobj.save()


    if urlobj.expired == True:
        #check if it is expired, delete dir, redirect to home
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')

    expiration = urlobj.created + timedelta(minutes=settings.EXPIRATION_TIME_LIMIT)

    if timezone.now() > expiration:
        #url has expired, mark as expired, delete dirs, redirect to homepage
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')


    if urlobj.url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')

    if "marked.txt" not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
        return HttpResponse("Not processed")

    '''
    if "single.txt" in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
        #look for single image in urldir
        for files in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
            if files.lower().endswith(('bmp', 'jpg', 'png', 'jpeg')):
                prezipped = files

    else:
        #look for zip file in urldir
        for files in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
            if files.lower().endswith(('.zip')):
                prezipped = files

    '''

    for files in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
        if files.lower().endswith(('.zip')):
            prezipped = files

    prezipped_address = os.path.join(settings.MEDIA_ROOT, 'temp', url, prezipped)
    response = HttpResponse(open(prezipped_address, 'rb').read(),
                         content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + prezipped

    return response



def load_url(request, hash):

    ##check if user is correct user for viewing this
    url = hash
    if not ExpiringURL.objects.filter(url=url).exists():
        #url doesnt exist, so redirect
        return HttpResponseRedirect('/')


    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    urlobj = ExpiringURL.objects.get(url=url)

    if urlobj.expired == True:
        #check if it is expired, delete dir, redirect to home
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')

    expiration = urlobj.created + timedelta(minutes=settings.EXPIRATION_TIME_LIMIT)

    if timezone.now() > expiration:
        #url has expired, mark as expired, delete dirs, redirect to homepage
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')


    if urlobj.url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
        expire_url(urlobj.url)
        return HttpResponseRedirect('/')

    if "marked.txt" in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
        data = dict()
        data['url'] = url
        data['well'] = 'done'
        data['proc'] = True
        return JsonResponse(data)

    '''If marked.txt isnt in dir, and .zip is, then process broke, abort entire thing
        mark it as expired, mark it as damaged, and delete dir'''

    user = str(request.user)
    userhash = user.encode("UTF-8")
    userhash = sha1(userhash).hexdigest()[:6]

    if url[:6] != userhash:  ##check if user is correct
        return HttpResponseRedirect('/')

    media_path = os.path.join(settings.MEDIA_ROOT, 'temp', url)

    try:
        with open(os.path.join(media_path, 'data'), 'rb') as fp:
            form = pickle.load(fp)
    except:
        return HttpResponseRedirect('/')
        ###change so that it checks if DIR exists, then redirects if it doesnt



    '''

    lone = False
    if "single.txt" in os.listdir(media_path):
        lone = True

    else:
        #create zip file if there is more than one image
        timehash = sha1(str(datetime.now().isoformat()).encode("UTF-8")).hexdigest()[:5]
        zipname = user + "_" + timehash + ".zip"
        zipadr = os.path.join(media_path, zipname)
        zf = zipfile.ZipFile(zipadr, mode='w')

    '''

    timehash = sha1(str(datetime.now().isoformat()).encode("UTF-8")).hexdigest()[:5]
    zipname = user + "_" + timehash + ".zip"
    zipadr = os.path.join(media_path, zipname)
    zf = zipfile.ZipFile(zipadr, mode='w')

    for f in os.listdir(media_path):
        if f.lower().endswith(('bmp', 'jpg', 'png', 'jpeg')):
            image = Image.open(os.path.join(media_path, f))

            final = scrambler(form['mode'], form['k1'], form['k2'], form['k3'], image)

            profile, check = Profile.objects.get_or_create(user=request.user)

            if profile.flagged == True:
                if 'users' not in os.listdir(settings.MEDIA_ROOT):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users'))

                if user not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users')):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user))

                if datetime.now().strftime('%Y-%m-%d') not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users', user)):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d')))

                if urlobj.url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'))):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'), urlobj.url))

                final.save(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'), urlobj.url, f))

                with open(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'), urlobj.url, "data"), 'wb') as fp:
                    pickle.dump(form, fp)





            if form['mode'] == "Scramble":
                name = str(Path(f).with_suffix('')) + ".BMP"
                final.save(os.path.join(media_path, name))
            else:
                try:
                    name = str(Path(f).with_suffix('')) + ".JPG"
                    final.save(os.path.join(media_path, name), format="JPEG", subsampling=0, quality=100)
                except Exception as e:
                    print("Error saving as JPG for user " + request.user + " in interaction " + urlobj.url + " : " + e)
                    try:
                        name = str(Path(f).with_suffix('')) + ".PNG"
                        final.save(os.path.join(media_path, name), format="PNG", subsampling=0, quality=100)
                    except Exception as e:
                        print("Error saving as PNG for user " + request.user + " in interaction " + urlobj.url + " : " + e)
                        try:
                            name = str(Path(f).with_suffix('')) + ".BMP"
                            final.save(os.path.join(media_path, name))
                        except Exception as e:
                            print("Error saving as BMP for user " + request.user + " in interaction " + urlobj.url + " : " + e)
                            print("Unable to save, expiring " + urlobj.url)
                            expire_url(urlobj.url)

            #if not lone:
            if True:
                zf = zipfile.ZipFile(zipadr, mode='a')
                try:
                    zf.write(os.path.join(media_path, name), arcname=name)
                finally:
                    zf.close()


    with open(os.path.join(media_path, "marked.txt"),"w+") as f:
        f.write("")

    data = dict()
    data['url'] = url
    data['well'] = 'done'
    data['proc'] = True
    return JsonResponse(data)


@login_required
def StartPage(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == 'POST':
            daily_ledger, check = DailyLedger.objects.get_or_create(date=timezone.now().date())
            daily_ledger.interaction_count += 1
            daily_ledger.save()

            profile, check = Profile.objects.get_or_create(user=request.user)
            form = ScrambleForm(request.POST, request.FILES)
            if form.is_valid():
                form = form.cleaned_data
                formdat = {'mode' : form['mode'], 'k1' : form['key_one'], 'k2' : form['key_two'], 'k3' : form['key_three']}


                if len(request.FILES.getlist('images')) > 0:

                    user = str(request.user)
                    time = str(datetime.now().isoformat())
                    hashkey = (user + time).encode("UTF-8")

                    userhash = user.encode("UTF-8")
                    userhash = sha1(userhash).hexdigest()[:6]

                    otherhash = sha1(hashkey).hexdigest()[:18]

                    url = str(userhash) + str(otherhash)

                    urlobj = ExpiringURL.objects.create()
                    urlobj.url = url
                    urlobj.user_name = user
                    urlobj.save()

                    if formdat['mode'] == 'Unscramble':
                        urlobj.mode = 'Unscramble'

                    media_path = os.path.join(settings.MEDIA_ROOT, 'temp', url)

                    if 'temp' not in os.listdir(settings.MEDIA_ROOT):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp'))

                    if url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp', url))

                    imcount = 0
                    for f in request.FILES.getlist('images'):
                        if f.name.lower().endswith(('.jpg', '.bmp', '.png', '.jpeg')):
                            imcount += 1

                    if imcount == 1:
                        with open(os.path.join(media_path, "single.txt"),"w+") as f:
                            f.write("")

                    with open(os.path.join(media_path, 'data'), 'wb') as fp:
                        pickle.dump(formdat, fp)

                    for f in request.FILES.getlist('images'):
                        image = Image.open(f)
                        image.save(os.path.join(media_path, f.name), subsampling=0, quality=100)

                        if formdat['mode'] == 'Scramble':
                            profile.scramble_count = profile.scramble_count + 1
                            profile.save()

                            daily_ledger.scram_count += 1
                            daily_ledger.save()
                        else:
                            profile.unscramble_count = profile.unscramble_count + 1
                            profile.save()

                            daily_ledger.unscram_count += 1
                            daily_ledger.save()

                        profile.total_size_of_uploaded_images = profile.total_size_of_uploaded_images + f.size
                        profile.total_file_count = profile.total_file_count + 1
                        profile.save()

                        urlobj.number_of_files = urlobj.number_of_files + 1
                        urlobj.save()

                        daily_ledger.total_files += 1
                        daily_ledger.save()

                    return render(request, "scrambler/download.html", {"dl_url" : url})

                else:
                    return HttpResponse("No files selected")
            return HttpResponse("Aww yeah")

    else:
        form = ScrambleForm

    return render(request, 'scrambler/start.html', {'form': form })

@login_required
def AccountPage(request):
    context = dict()
    context['n_o_b_u'] = byteconvert(request.user.profile.total_size_of_uploaded_images)
    context['userkey'] = request.user.profile.userkey

    if request.user.profile.userkey == '0':
        userprofile = Profile.objects.get(user=request.user)
        context['userkey'] = userprofile.userkey_gen()

    try:
        rmtoken = RemoteToken.objects.get(user_name=str(request.user))
    except:
        rmtoken, check = RemoteToken.objects.get_or_create(user_name=str(request.user))
        rmtoken.create_token()

    if rmtoken.token == '0':
        rmtoken.create_token()

    if rmtoken.uses == settings.API_TOKEN_LIMIT:
        rmtoken.expire()
        rmtoken, check = RemoteToken.objects.get_or_create(user_name=str(request.user))
        rmtoken.create_token()

    context['api_requests'] = request.user.profile.api_requests
    context['api_unscrambles'] = request.user.profile.api_unscrams
    context['api_scrambles'] = request.user.profile.api_scrams

    context['token'] = rmtoken.token
    context['remain'] = settings.API_TOKEN_LIMIT - rmtoken.uses

    return render(request, 'scrambler/account.html', context)
