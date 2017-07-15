from django import forms
from django.contrib.auth.models import User
from scrambler.models import UserScrambleInfo

class ScrambleForm(forms.Form):
    key_one = forms.CharField(max_length=256)
    key_two = forms.CharField(label='Key Two', max_length=256)
    key_three = forms.CharField(label='Key Three', max_length=256)

    CHOICES=[('Scramble','scramble'), ('Unscramble','unscramble')]
    Choice = forms.ChoiceField(choices=CHOICES)
