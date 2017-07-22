from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Profile

from datetime import datetime
from hashlib import sha1

import os
import pickle

from .forms import ScrambleForm
from .scramble import scrambler

from PIL import Image
# Create your views here.


def load_url(request, hash):
    #url = get_object_or_404(TempUrl, url_hash=hash, expires__gte=datetime.now())

    ##check if user is correct user for viewing this
    url = hash

    if url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
        return HttpResponse("url does not exist")
    '''
    if "marked.txt" in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp', url)):
        return HttpResponse("Already processed")
    '''
    print("a")

    user = str(request.user)
    userhash = user.encode("UTF-8")
    userhash = sha1(userhash).hexdigest()[:6]

    print("user: ", userhash)
    print("url: ", url[:6])

    if url[:6] != userhash:  ##check if user is correct
        return HttpResponseRedirect('/')

    print("b")

    media_path = os.path.join(settings.MEDIA_ROOT, 'temp', url)

    try:
        with open(os.path.join(media_path, 'data'), 'rb') as fp:
            form = pickle.load(fp)
            print(form)
    except:
        return HttpResponseRedirect('/')
        ###change so that it checks if DIR exists, then redirects if it doesnt

    print("c")

    print(os.listdir(media_path))

    for f in os.listdir(media_path):
        #HttpResponse("Aww yeah")
        if f == "data" or f == "marked.txt":
            print(f)

        else:
            image = Image.open(os.path.join(media_path, f))

            final = scrambler(form['mode'], form['k1'], form['k2'], form['k3'], image)
            ###if user is flagged, run this part
            user = str(request.user)

            if 'users' not in os.listdir(settings.MEDIA_ROOT):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users'))

            if user not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users')):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user))

            if datetime.now().strftime('%Y-%m-%d') not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users', user)):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d')))

            final.save(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'), f))
            ##add encrypted list of keys
            ##end of flagged area

            ##pass image and keys to scramble

    with open(os.path.join(media_path, "marked.txt"),"w+") as f:
        f.write("")

    ##if user.marked, copy temp url dir to user/data/url

    return HttpResponse(url)


    #return JsonResponse(data)


def StartPage(request):
    if request.method == 'POST':
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

                    print("s_user:", userhash)
                    print("s_url: ", url)

                    if 'temp' not in os.listdir(settings.MEDIA_ROOT):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp'))

                    if url not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'temp')):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'temp', url))

                    media_path = os.path.join(settings.MEDIA_ROOT, 'temp', url)

                    with open(os.path.join(media_path, 'data'), 'wb') as fp:
                        pickle.dump(formdat, fp)

                    ##add data to session, create url, return page which does ajax call to temp url
                    for f in request.FILES.getlist('images'):
                        image = Image.open(f)
                        image.save(os.path.join(media_path, f.name), format="BMP", subsampling=0, quality=100)

                        if formdat['mode'] == 'Scramble':
                            profile.scramble_count = profile.scramble_count + 1
                            profile.save()
                        else:
                            profile.unscramble_count = profile.unscramble_count + 1
                            profile.save()

                    return render(request, "scrambler/download.html", {"dl_url" : url})

                else:
                    return HttpResponse("No files selected")
            return HttpResponse("Aww yeah")

    else:
        form = ScrambleForm

    return render(request, 'scrambler/start.html', {'form': form })


class AccountPage(LoginRequiredMixin, TemplateView):
    template_name = 'scrambler/account.html'
