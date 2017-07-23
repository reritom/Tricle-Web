from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    scramble_count = models.IntegerField(default=0)
    unscramble_count = models.IntegerField(default=0)
    total_size_of_uploaded_images = models.BigIntegerField(default=0)
    total_file_count = models.IntegerField(default=0)
    last_login = models.DateTimeField(default=timezone.now())
    flagged = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class ExpiringURL(models.Model):
    url = models.CharField(default=0, max_length=255, unique=True)
    created = models.DateTimeField(default=timezone.now())
    expired = models.BooleanField(default=False)
    number_of_files = models.IntegerField(default=0)
    user_name = models.CharField(default=0, max_length=255)
    mode = models.CharField(default="Scramble", max_length=255)

    def __str__(self):
        return self.url

class AnalyticsLedger(models.Model):

    def total_scramblers(self):
        pass

    def total_unscrambles(self):
        pass

    def daily_active_users(self):
        pass

    def daily_scrambles(self):
        pass

    def daily_unscrambles(self):
        pass
