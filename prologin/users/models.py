from django.db import models
from django.contrib.auth.models import User
from prologin.utils import limit_charset

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    short_name = models.CharField(max_length=16)
    title = models.CharField(max_length=16)
    address = models.TextField()
    postal_code = models.CharField(max_length=5)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)
    birthday = models.DateField(max_length=64, blank=True, null=True)
    newsletter = models.BooleanField()

class ProloginUser():
    def getShortName(self, name):
        short_name = limit_charset(name)
        try:
            UserProfile.objects.get(short_name=short_name)
        except UserProfile.DoesNotExist:
            return short_name
        
        raise ValueError('%s: user with the same short name already exists' % short_name)

    def register(self, name, email, password, newsletter):
        short_name = self.getShortName(name)
        
        user = User.objects.create_user(name, email, password)
        user.save()

        profile = UserProfile(user=user, short_name=short_name, newsletter=newsletter)
        profile.save()
        
        return profile
