from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserScrambleInfo(models.Model):
    user = models.OneToOneField(User)
    scramble_count = models.IntegerField(default=0)
    unscramble_count = models.IntegerField(default=0)
