from django.http import HttpResponse
from django.conf import settings
from django.contrib import auth
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect
import dateutil.parser

class AutoLogout(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def process_request(self, request):
            if not request.user.is_authenticated() :
                #Can't log out if not logged in
                #print("not logged in")
                return

            try:
                parsed = dateutil.parser.parse(request.session['last_touch'])

                if parsed + timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0) < timezone.now():
                    #print("last: " + request.session['last_touch'])
                    #print("cur: " + timezone.now().isoformat())
                    #print("user logged out")

                    del request.session['last_touch']
                    auth.logout(request)
                    return HttpResponseRedirect('/')
                else:
                    #print("last: " + request.session['last_touch'])
                    #print("cur: " + timezone.now().isoformat())
                    #print("still active")
                    pass

            except KeyError:
                pass

            request.session['last_touch'] = timezone.now().isoformat()


        process_request(self, request)

        return self.get_response(request)
