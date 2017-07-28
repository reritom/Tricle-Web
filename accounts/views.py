from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect

from accounts import forms
# Create your views here.

class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

def ThanksPage(request):
    #if not request.user.is_authenticated():
    #    return HttpResponseRedirect('/')
    template_name = 'accounts/thanks.html'
    return render(request, template_name)

def validate_username(request):
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse("Sneaky")
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)

def validate_email(request):
    email = request.GET.get('email', None)
    if email == None:
        return HttpResponse("Sneaky")
    data = {
        'is_taken': User.objects.filter(email__iexact=email).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this email already exists.'
    return JsonResponse(data)
