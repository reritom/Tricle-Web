from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

from datetime import datetime
from hashlib import sha1
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    scramble_count = models.IntegerField(default=0)
    unscramble_count = models.IntegerField(default=0)
    total_size_of_uploaded_images = models.BigIntegerField(default=0)
    total_file_count = models.IntegerField(default=0)
    last_login = models.DateTimeField(default=timezone.now, null=True)
    flagged = models.BooleanField(default=False)
    test_user = models.BooleanField(default=False)
    userkey = models.CharField(default=0, max_length=255)

    api_scrams = models.IntegerField(default=0)
    api_unscrams = models.IntegerField(default=0)
    api_requests = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def userkey_gen(self):
        username = self.user.username

        user_hash = username.encode("UTF-8")
        user_hash = sha1(user_hash).hexdigest()[:20]

        self.userkey = user_hash
        self.save()
        return self.userkey

class ExpiringURL(models.Model):
    url = models.CharField(default=0, max_length=255, unique=True)
    created = models.DateTimeField(default=timezone.now, null=True)
    expired = models.BooleanField(default=False)
    number_of_files = models.IntegerField(default=0)
    user_name = models.CharField(default=0, max_length=255)
    mode = models.CharField(default="Scramble", max_length=255)
    down_count = models.IntegerField(default=0)

    def __str__(self):
        return self.url

class ExpiredURL(models.Model):
    url = models.CharField(default=0, max_length=255, unique=True)
    created = models.DateTimeField(default=timezone.now, null=True)
    number_of_files = models.IntegerField(default=0)
    user_name = models.CharField(default=0, max_length=255)
    mode = models.CharField(default="Scramble", max_length=255)

    def __str__(self):
        return self.url



'''
make notification model
'''

'''
class Notification(models.Model):
    message = models.CharField(default=0, max_length=255)
    start date = datetime models
    duration = timedelta
'''

class DailyLedger(models.Model):
    date = models.DateTimeField(default=0, unique=True)
    dau = models.IntegerField(default=0)
    interaction_count = models.IntegerField(default=0)
    scram_count = models.IntegerField(default=0)
    unscram_count = models.IntegerField(default=0)
    total_files = models.IntegerField(default=0)
    login_count = models.IntegerField(default=0)

    api_requests = models.IntegerField(default=0)
    api_scrams = models.IntegerField(default=0)
    api_unscrams = models.IntegerField(default=0)

    def __str__(self):
        return self.date.strftime("%B %d, %Y")

class RemoteToken(models.Model):
    user_name = models.CharField(default=0, max_length=255)
    token = models.CharField(default=0, max_length=255)
    uses = models.IntegerField(default=0)

    def __str__(self):
        return self.token

    def increment_uses(self):
        if self.uses < 20:
            self.uses += 1
            self.save()
            return True
        else:
            self.expire()
            return False

    def expire(self):
        exptoken, check = ExpiredToken.objects.get_or_create(user_name=self.user_name, token=self.token)
        newtoken, check = RemoteToken.objects.get_or_create(user_name=self.user_name)
        newtoken.create_token()
        self.delete()
        return True

    def create_token(self):
        user = str(self.user_name)
        time = str(datetime.now().isoformat())
        hashkey = (user + time).encode("UTF-8")

        userhash = user.encode("UTF-8")
        userhash = sha1(userhash).hexdigest()[:5]

        otherhash = sha1(hashkey).hexdigest()[:15]

        self.token = str(otherhash) + str(userhash)[::-1]
        self.save()
        return self.token

class ExpiredToken(models.Model):
    user_name = models.CharField(default=0, max_length=255)
    token = models.CharField(default=0, max_length=255)

    def __str__(self):
        return self.token

    def propagate(self, user, token):
        self.user_name = user
        self.token = token
        self.save()

class RemoteInteraction(models.Model):
    rm_id = models.CharField(default=0, max_length=255, unique=True)
    user_name = models.CharField(default=0, max_length=255)
    created = models.DateTimeField(default=timezone.now, null=True)
    mode = models.CharField(default="Scramble", max_length=255)

    def __str__(self):
        return self.rm_id
