from django.contrib.auth.models import User
from django.db import models as m
from django.dispatch import receiver
from django.db.models.signals import post_save

from alertas.email import send_expiration_email
from alertas.utils import insert_libreborme_log

from djstripe.models import Customer

ACCOUNT_CHOICES = (
    ('free', "Gratuita"),
    ('paid', "Premium"),
    ('test', "Período de prueba"),
)

NOTIFICATION_CHOICES = (
    ('email', "E-mail"),
    ('url', "URL"),
    # ('telegram', "Telegram"),
)

LANGUAGE_CHOICES = (
    ('es', 'Español'),
)


class Profile(m.Model):
    user = m.OneToOneField(User, on_delete=m.CASCADE, related_name='profile')
    account_type = m.CharField(max_length=4, choices=ACCOUNT_CHOICES)
    notification_method = m.CharField(max_length=10,
                                      choices=NOTIFICATION_CHOICES,
                                      default='email')
    notification_email = m.EmailField(blank=True)
    notification_url = m.URLField(blank=True)
    language = m.CharField(max_length=3,
                           choices=LANGUAGE_CHOICES,
                           default='es')
    send_html = m.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.notification_email:
            self.notification_email = self.user.email
        super(Profile, self).save(*args, **kwargs)

    def is_premium(self):
        pass
        # return all(for invoice in self.invoices:
        #    invoice

    def expire_subscription(self, send_email):
        if self.user.is_active:
            self.user.is_active = False
            self.user.save()
            insert_libreborme_log("subscription",
                                  "User subscription has expired.",
                                  self.user.username)
            if send_email:
                send_expiration_email(self.user)
            return True
        return False

    def __str__(self):
        return "Profile {} ({})".format(self.user, self.account_type)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, account_type='free')
        # TODO: set currency="eur"
        Customer.create(subscriber=instance)
    instance.profile.save()
