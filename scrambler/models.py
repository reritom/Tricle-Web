from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    scramble_count = models.IntegerField(default=0)
    unscramble_count = models.IntegerField(default=0)
    total_size_of_uploaded_images = models.BigIntegerField(default=0)
    total_file_count = models.IntegerField(default=0)
    last_login = models.DateTimeField(default=timezone.now(), null=True)
    flagged = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class ExpiringURL(models.Model):
    url = models.CharField(default=0, max_length=255, unique=True)
    created = models.DateTimeField(default=timezone.now(), null=True)
    expired = models.BooleanField(default=False)
    number_of_files = models.IntegerField(default=0)
    user_name = models.CharField(default=0, max_length=255)
    mode = models.CharField(default="Scramble", max_length=255)

    def __str__(self):
        return self.url

class ExpiredURL(models.Model):
    url = models.CharField(default=0, max_length=255, unique=True)
    created = models.DateTimeField(default=timezone.now(), null=True)
    number_of_files = models.IntegerField(default=0)
    user_name = models.CharField(default=0, max_length=255)
    mode = models.CharField(default="Scramble", max_length=255)

    def __str__(self):
        return self.url



'''
create expiredurl model

populate daily ledger

make notification model

'''

class DailyLedger(models.Model):
    date = models.DateTimeField(default=timezone.now().date())
    dau = models.IntegerField(default=0)
    interaction_count = models.IntegerField(default=0)
    scram_count = models.IntegerField(default=0)
    unscram_count = models.IntegerField(default=0)
    total_files = models.IntegerField(default=0)
    login_count = models.IntegerField(default=0)

    def __str__(self):
        return self.date
