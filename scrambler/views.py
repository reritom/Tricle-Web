from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.conf import settings
import os

from .forms import ScrambleForm
from .scramble import scrambler

from PIL import Image
from datetime import datetime
# Create your views here.

def StartPage(request):
    if request.method == 'POST':
            form = ScrambleForm(request.POST, request.FILES)
            if form.is_valid():
                form = form.cleaned_data
                for f in request.FILES.getlist('images'):
                    image = Image.open(f)
                    user = str(request.user)

                    #create dir
                    if 'users' not in os.listdir(settings.MEDIA_ROOT):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users'))

                    if user not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users')):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user))

                    if datetime.now().strftime('%Y-%m-%d') not in os.listdir(os.path.join(settings.MEDIA_ROOT, 'users', user)):
                        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d')))

                    image.save(os.path.join(settings.MEDIA_ROOT, 'users', user, datetime.now().strftime('%Y-%m-%d'), f.name))

                return HttpResponse("Aww yeah")

                #store form in session
                #go to loading html
                #ajax call from loading html
                #the view called from ajax accesses the session data
                #processes the images
                #then injects them back into the loading page
                #download button downloads zip of images

    else:
        form = ScrambleForm

    return render(request, 'scrambler/start.html', {'form': form })


class AccountPage(TemplateView):
    template_name = 'scrambler/account.html'
