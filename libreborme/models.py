from django.contrib.auth import get_user_model
from django.db import models as m
from django.dispatch import receiver
from django.db.models.signals import post_save

from alertas.email import send_expiration_email
from alertas.utils import insert_libreborme_log


NOTIFICATION_CHOICES = (
    ('email', "E-mail"),
    ('url', "URL"),
    # ('telegram', "Telegram"),
)

LANGUAGE_CHOICES = (
    ('es', 'Español'),
)

ACCOUNT_TYPE_CHOICE = (
    ('individual', 'Particular'),
    ('company', 'Empresa'),
)

COUNTRY_CHOICE = (
    ('ES', 'España'),
)

class Profile(m.Model):
    user = m.OneToOneField(get_user_model(), on_delete=m.CASCADE, related_name='profile')

    language = m.CharField(max_length=3,
                           choices=LANGUAGE_CHOICES,
                           default='es')

    # Subscriptions service
    notification_method = m.CharField(max_length=10,
                                      choices=NOTIFICATION_CHOICES,
                                      default='email')
    notification_email = m.EmailField(blank=True)
    notification_url = m.URLField(blank=True)
    send_html = m.BooleanField(default=True)

    # Datos de contacto
    home_phone = m.CharField(max_length=20, blank=True)

    # Datos de facturación
    account_type = m.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICE,
                               default='company')
    razon_social = m.CharField(max_length=200, blank=True)
    cif_nif = m.CharField(max_length=20, blank=True)
    address = m.CharField(max_length=200, blank=True)
    post_code = m.CharField(max_length=20, blank=True)
    poblacion = m.CharField(max_length=50, blank=True)
    provincia = m.CharField(max_length=50, blank=True)
    country = m.CharField(max_length=50, choices=COUNTRY_CHOICE, default='ES')

    # Newsletter
    newsletter_promotions = m.BooleanField(default=False)
    newsletter_features = m.BooleanField(default=False)

    # Servicios
    # User has contacted support or paid for a plan
    has_api_enabled = m.BooleanField(default=False)
    has_tried_subscriptions = m.BooleanField(default=False)

    def is_complete(self):
        return all([self.user.first_name, self.user.last_name,
                    self.user.email,
                    self.razon_social, self.cif_nif, self.address,
                    self.post_code, self.poblacion, self.provincia,
                    self.country])

    def save(self, *args, **kwargs):
        if not self.notification_email:
            self.notification_email = self.user.email
        super(Profile, self).save(*args, **kwargs)

    # TODO: review need
    def expire_subscription(self, send_email):
        if self.user.is_active:
            self.user.is_active = False
            self.user.save()
            insert_libreborme_log("subscription",
                                  "User subscription has expired.",
                                  self.user.email)
            if send_email:
                send_expiration_email(self.user)
            return True
        return False

    def __str__(self):
        return "Profile {}".format(self.user)


class MailTemplate(m.Model):
    name = m.CharField(max_length=20)
    description = m.CharField(max_length=200, blank=True)
    plain_text = m.TextField()
    html_text = m.TextField()


@receiver(post_save, sender=get_user_model())
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # TODO: set currency="eur"
    instance.profile.save()
