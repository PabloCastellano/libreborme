from django.contrib.auth.models import User
from django.db import models as m

from alertas.email import send_expiration_email
from alertas.utils import insert_libreborme_log

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
    user = m.OneToOneField(User, on_delete=m.CASCADE)
    account_type = m.CharField(max_length=4, choices=ACCOUNT_CHOICES)
    notification_method = m.CharField(max_length=10,
                                      choices=NOTIFICATION_CHOICES,
                                      default='email')
    notification_email = m.EmailField(blank=True)
    notification_url = m.URLField(blank=True)
    language = m.CharField(max_length=3, choices=LANGUAGE_CHOICES,
                           default='es')
    send_html = m.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False):
        if not self.notification_email:
            self.notification_email = self.user.email
        super(Profile, self).save(force_insert, force_update)

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
