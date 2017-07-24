from django.contrib import admin
from .models import Profile, ExpiringURL, ExpiredURL
# Register your models here.

admin.site.register(Profile)
admin.site.register(ExpiringURL)
admin.site.register(ExpiredURL)
