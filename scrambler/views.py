from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ScrambleForm
from django.http import HttpResponse
# Create your views here.

def StartPage(request):
    if request.method == 'POST':
            form = ScrambleForm(request.POST)
            if form.is_valid():
                form = form.cleaned_data
                print(form.get('key_one'))
                return HttpResponse("Well done")

    else:
        form = ScrambleForm

    return render(request, 'scrambler/start.html', {'form': form })



class AccountPage(TemplateView):
    template_name = 'scrambler/account.html'
