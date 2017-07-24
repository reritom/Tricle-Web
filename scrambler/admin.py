from django.contrib import admin
from .models import Profile, ExpiringURL, ExpiredURL, DailyLedger
# Register your models here.

admin.site.register(Profile)
admin.site.register(ExpiringURL)
admin.site.register(ExpiredURL)
admin.site.register(DailyLedger)
