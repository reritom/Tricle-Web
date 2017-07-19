from django import forms
from django.contrib.auth.models import User
from scrambler.models import UserScrambleInfo

class ScrambleForm(forms.Form):
    key_one = forms.CharField(label='', max_length=256, widget=forms.TextInput(attrs={'placeholder': 'Enter your first key'}))
    key_two = forms.CharField(label='', max_length=256, widget=forms.TextInput(attrs={'placeholder': 'Enter your second key'}))
    key_three = forms.CharField(label='', max_length=256, widget=forms.TextInput(attrs={'placeholder': 'Enter your third key'}))

    CHOICES=[('Scramble','Scramble'), ('Unscramble','Unscramble')]
    mode = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={'class':'regDropDown'}))

    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,}))
