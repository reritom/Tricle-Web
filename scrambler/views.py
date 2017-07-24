from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.contrib.auth.models import User
from .models import Profile, ExpiringURL, ExpiredURL, DailyLedger
from .forms import ScrambleForm
from .scramble import scrambler

from datetime import datetime, timedelta
from hashlib import sha1
import os
import pickle
import shutil

from PIL import Image
import zipfile

'''
json respond download link which calls view which returns httpresponse.
when json respondes, change download button.
'''

def delete_dir(url):
    #check if dir is present, delete if it is
    if 'temp' in os.listdir(settings.MEDIA_ROOT):
        if url in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
            url_dir = os.path.join(settings.MEDIA_ROOT, 'temp', url)
            shutil.rmtree(url_dir)
            return
    else:
        return

def load_url(request, hash):
    #url = get_object_or_404(TempUrl, url_hash=hash, expires__gte=datetime.now())

    ##check if user is correct user for viewing this
    url = hash
    if not ExpiringURL.objects.filter(url=url).exists():
        #url doesnt exist, so redirect
        return HttpResponseRedirect('/')

    urlobj = ExpiringURL.objects.get(url=url)

    if urlobj.expired == True:
        #check if it is expired, delete dir, redirect to home
        delete_dir(url)
        expiredurl, created = ExpiredURL.objects.get_or_create(url=urlobj.url)
        if created == True:
            expiredurl.created = urlobj.created
            expiredurl.number_of_files = urlobj.number_of_files
            expiredurl.mode = urlobj.mode
            expiredurl.user_name = urlobj.user_name
            expiredurl.save()
        urlobj.delete()
        return HttpResponseRedirect('/')

    expiration = urlobj.created + timedelta(minutes=10)

    if timezone.now() > expiration:
        #url has expired, mark as expired, delete dirs, redirect to homepage
        urlobj.expired = True
        urlobj.save()

        delete_dir(url)
        expiredurl, created = ExpiredURL.objects.get_or_create(url=urlobj.url)
        if created == True:
            expiredurl.created = urlobj.created
            expiredurl.number_of_files = urlobj.number_of_files
            expiredurl.mode = urlobj.mode
            expiredurl.user_name = urlobj.user_name
            expiredurl.save()
        urlobj.delete()
        return HttpResponseRedirect('/')


    if urlobj.url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
        urlobj.expired = True
        urlobj.save()
        expiredurl, created = ExpiredURL.objects.get_or_create(url=urlobj.url)
        if created == True:
            expiredurl.created = urlobj.created
            expiredurl.number_of_files = urlobj.number_of_files
            expiredurl.mode = urlobj.mode
            expiredurl.user_name = urlobj.user_name
            expiredurl.save()
        urlobj.delete()
        return HttpResponseRedirect('/')

    if "marked.txt" in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
        for files in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
            if files.lower().endswith(('.zip')):
                prezipped = files

        prezipped_address = os.path.join(settings.MEDIA_ROOT, 'temp', url, prezipped)
        response = HttpResponse(open(prezipped_address, 'rb').read(),
                             content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=' + prezipped

        for users in User.objects.all():
            Profile.objects.get_or_create(user=users)

        return response

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

    timehash = sha1(str(datetime.now().isoformat()).encode("UTF-8")).hexdigest()[:5]
    zipname = user + "_" + timehash + ".zip"
    zipadr = os.path.join(media_path, zipname)

    zf = zipfile.ZipFile(zipadr, mode='w')

    for f in os.listdir(media_path):
        if f.lower().endswith(('bmp', 'jpg', 'png')):
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

            final.save(os.path.join(media_path, f))

            zf = zipfile.ZipFile(zipadr, mode='a')
            try:
                zf.write(os.path.join(media_path, f), arcname=f)
            finally:
                zf.close()

    with open(os.path.join(media_path, "marked.txt"),"w+") as f:
        f.write("")

    response = HttpResponse(open(zipadr, 'rb').read(),
                         content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + zipname

    return response

    #return HttpResponse(url)
    #return JsonResponse(data)


def StartPage(request):
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


                    if 'temp' not in os.listdir(settings.MEDIA_ROOT):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp'))

                    if url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp', url))

                    media_path = os.path.join(settings.MEDIA_ROOT, 'temp', url)

                    with open(os.path.join(media_path, 'data'), 'wb') as fp:
                        pickle.dump(formdat, fp)

                    for f in request.FILES.getlist('images'):
                        image = Image.open(f)
                        image.save(os.path.join(media_path, f.name), format="BMP", subsampling=0, quality=100)

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


class AccountPage(LoginRequiredMixin, TemplateView):
    template_name = 'scrambler/account.html'
