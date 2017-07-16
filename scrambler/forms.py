from django import forms
from django.contrib.auth.models import User
from scrambler.models import UserScrambleInfo

class ScrambleForm(forms.Form):
    key_one = forms.CharField(max_length=256)
    key_two = forms.CharField(label='', max_length=256)
    key_three = forms.CharField(label='Key Three', max_length=256)

    CHOICES=[('Scramble','scramble'), ('Unscramble','unscramble')]
    mode = forms.ChoiceField(choices=CHOICES)

    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
