import logging
from datetime import datetime, timezone, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAcceptable
from allauth.account.signals import user_signed_up
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from randompinfield import RandomPinField
import phonenumbers
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from .signals import register_signal
from .managers import NationalIDImageManager
from core.models import TimeStampedModel
from core.handle_images import compress_image

User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/<filename>
    return "users/{0}/{1}".format(instance.user.username, filename)


def national_image_path(instance, filename):
    return f"national/{instance.user.username}/images/{filename}"


class Profile(TimeStampedModel):
    GENDER_MALE = "m"
    GENDER_FEMALE = "f"
    OTHER = "o"

    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (OTHER, "Other"),
    )

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True)
    phone_number = PhoneNumberField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    about = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.user.username

    @property
    def last_seen(self):
        return cache.get(f"seen_{self.user.username}")

    @property
    def online(self):
        if self.last_seen:
            now = datetime.now(timezone.utc)
            if now > self.last_seen + timedelta(minutes=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Address(TimeStampedModel):
    user = models.ForeignKey(User, related_name="address", on_delete=models.CASCADE)
    country = CountryField(blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    district = models.CharField(max_length=100, blank=False, null=False)
    street_address = models.CharField(max_length=250, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    primary = models.BooleanField(default=False)
    phone_number = PhoneNumberField(null=True, blank=True)
    building_number = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(1)]
    )
    apartment_number = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(1)]
    )


class SMSVerification(TimeStampedModel):
    user = models.OneToOneField(User, related_name="sms", on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    pin = RandomPinField(length=6)
    sent = models.BooleanField(default=False)
    phone = PhoneNumberField(null=False, blank=False)

    def send_confirmation(self):

        logging.debug("Sending PIN %s to phone %s" % (self.pin, self.phone))

        if all(
            [
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_FROM_NUMBER,
            ]
        ):
            try:
                twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
                )
                twilio_client.messages.create(
                    body="Your forgeter activation code is %s" % self.pin,
                    to=str(self.user.profile.phone_number),
                    from_=settings.TWILIO_FROM_NUMBER,
                )
                self.sent = True
                self.save()
                return True
            except TwilioRestException as e:
                logging.error(e)
        else:
            logging.warning("Twilio credentials are not set")

    def confirm(self, pin):
        if pin == self.pin and self.verified == False:
            self.verified = True
            self.save()
        else:
            raise NotAcceptable("your Pin is wrong, or this phone is verified before.")

        return self.verified


@receiver(post_save, sender=Profile)
def send_sms_verification(sender, instance, *args, **kwargs):
    try:
        sms = instance.user.sms
        if sms:
            pin = sms.pin
            sms.delete()
            verification = SMSVerification.objects.create(
                user=instance.user,
                phone=instance.user.profile.phone_number,
                sent=True,
                verified=True,
                pin=pin,
            )
    except:
        if instance.user.profile.phone_number:
            verification = SMSVerification.objects.create(
                user=instance.user, phone=instance.user.profile.phone_number
            )
            # TODO Remove send confirm from here and make view for it.
            verification.send_confirmation()

    # if instance.user.profile.phone_number:
    #     verification = SMSVerification.objects.create(user=instance.user, phone=instance.user.profile.phone_number)
    #     # TODO Remove send confirm from here and make view for it.
    #     verification.send_confirmation()


class DeactivateUser(TimeStampedModel):
    user = models.OneToOneField(
        User, related_name="deactivate", on_delete=models.CASCADE
    )
    deactive = models.BooleanField(default=True)


class NationalIDImage(models.Model):
    user = models.ForeignKey(
        User, related_name="national_ids", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=national_image_path, blank=True)
    is_deleted = models.BooleanField(default=False)

    objects = NationalIDImageManager()

    def __str__(self):
        return self.user.username

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
        *args,
        **kwargs,
    ):
        # if size greater than 300kb then it will send to compress image function
        image = self.image
        if image and image.size > (0.3 * 1024 * 1024):
            self.image = compress_image(image)
        super(NationalIDImage, self).save(*args, **kwargs)
