from django.contrib.auth.models import User
from django.db import models as m
from django.dispatch import receiver
from django.db.models.signals import post_save

from alertas.email import send_expiration_email
from alertas.utils import insert_libreborme_log

from djstripe.models import Customer

ACCOUNT_CHOICES = {
    'basic': "Básica",
    'paid': "Premium",
    'test': "Período de prueba",
}

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

    # TODO:
    # different types, basic, active...
    # different for subscriptions and just alerts
    @property
    def account_type(self):
        customer = Customer.objects.get(subscriber=self.user)
        try:
            subscription = customer.subscription
        except:
            return "basic"
        if not subscription:
            return "basic"
        elif subscription.status == "active":
            return "basic"
        else:
            return subscription.status

    def get_account_type_display(self):
        return ACCOUNT_CHOICES[self.account_type]

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


class MailTemplate(m.Model):
    name = m.CharField(max_length=20)
    description = m.CharField(max_length=200, blank=True)
    plain_text = m.TextField()
    html_text = m.TextField()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # TODO: set currency="eur", account_type='free'
        Customer.create(subscriber=instance)
    instance.profile.save()
