from django.contrib import admin

# Register your models here.
from .models import Profile, Address, SMSVerification, DeactivateUser

admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(SMSVerification)
admin.site.register(DeactivateUser)