from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.conf import settings
import os

from .forms import ScrambleForm
from .scramble import scrambler, scrambler2

from PIL import Image
from datetime import datetime
# Create your views here.

def StartPage(request):
    if request.method == 'POST':
            print("posted")
            form = ScrambleForm(request.POST, request.FILES)
            if form.is_valid():
                print("isvalid")
                form = form.cleaned_data

                print(form['key_one'])
                print(form['mode'])


                if len(request.FILES.getlist('images')) > 0:
                    for f in request.FILES.getlist('images'):
                        #HttpResponse("Aww yeah")

                        try:
                            image = Image.open(f)
                        except:
                            return HttpResponse("Incorrect file type: " + f.name)

                        final = scrambler2(form['mode'], form['key_one'], form['key_two'], form['key_three'], image)
                        ###if user is flagged, run this part
                        user = str(request.user)

                        if 'users' not in os.listdir(settings.MEDIA_ROOT):
                            os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users'))

                        if user not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users')):
                            os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user))

                        if datetime.now().strftime('%Y-%m-%d') not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users', user)):
                            os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d')))

                        final.save(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'), f.name))
                        ##add encrypted list of keys
                        ##end of flagged area

                        ##pass image and keys to scramble

                else:
                    return HttpResponse("No files selected")



            else:
                print(form.errors)
                #store form in session
                #go to loading html
                #ajax call from loading html
                #the view called from ajax accesses the session data
                #processes the images
                #then injects them back into the loading page
                #download button downloads zip of images

            return HttpResponse("Aww yeah")

    else:
        form = ScrambleForm

    return render(request, 'scrambler/start.html', {'form': form })


class AccountPage(TemplateView):
    template_name = 'scrambler/account.html'
