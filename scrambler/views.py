from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ScrambleForm
from django.http import HttpResponse, HttpResponseRedirect
import time
from .scramble import scrambler
# Create your views here.

def StartPage(request):
    print(request.user)

    if request.method == 'POST':
            form = ScrambleForm(request.POST, request.FILES)
            if form.is_valid():
                form = form.cleaned_data
                print(form.get('key_one'))
                print(form.get('mode'))
                print(request.FILES['images'])
                return HttpResponse("Well done")

    else:
        form = ScrambleForm

    return render(request, 'scrambler/start.html', {'form': form })


class AccountPage(TemplateView):
    template_name = 'scrambler/account.html'
