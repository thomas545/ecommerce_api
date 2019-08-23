from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from core.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/<filename>
    return 'users/{0}/{1}'.format(instance.user.username, filename)


class Profile(TimeStampedModel):
    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    OTHER = 'o'

    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (OTHER,'Other'),
    )


    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True)
    phone_number = PhoneNumberField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    about = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Address(TimeStampedModel):
    user = models.ForeignKey(User, related_name='address', on_delete=models.CASCADE)
    country = CountryField(blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    district = models.CharField(max_length=100, blank=False, null=False)
    street_address = models.CharField(max_length=250, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    primary = models.BooleanField(default=False)
    phone_number = PhoneNumberField(null=True, blank=True)
    building_number = models.IntegerField(blank=True, null=True,validators=[MinValueValidator(1)])
    apartment_number = models.IntegerField(blank=True, null=True,validators=[MinValueValidator(1)])
