from random import randint

#from django.conf import settings
##from django.contrib.auth.models import User
#from .models import Profile
from faker import Faker


test_user_amount = randint(2000,3000)

print(test_user_amount)


for usernum in range(test_user_amount):
    fake = Faker()

    test_username = fake.first_name() + fake.last_name()
    test_email = fake.email()
    test_password = 'test'

    '''
    u = User.objects.get(username = test_username)
    profile, check = Profile.objects.get_or_create(user=test_username)
    '''

    print(test_username + " " + test_email)
