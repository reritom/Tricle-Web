from django.contrib import admin
from .models import Profile, ExpiringURL, ExpiredURL, DailyLedger, RemoteToken, ExpiredToken, RemoteInteraction
# Register your models here.

admin.site.register(Profile)
admin.site.register(ExpiringURL)
admin.site.register(ExpiredURL)
admin.site.register(DailyLedger)
admin.site.register(RemoteToken)
admin.site.register(ExpiredToken)
admin.site.register(RemoteInteraction)
