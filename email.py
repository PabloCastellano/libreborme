from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.template import loader

from .utils import get_alertas_config

import logging
import os.path


EMAIL_FROM = "noreply@libreborme.net"
EMAIL_TEMPLATES_PATH = os.path.join("alertas", "templates", "email")
NOTIFICATION_SUBJECT = "Su período de pruebas en Libreborme Alertas ha expirado"


LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)


def send_expiration_email(user):
    try:
        validate_email(user.email)
    except ValidationError:
        LOG.error("User {0} has an invalid email: {1}, no email sent.".format(user.username, user.email))
        return

    template_name = os.path.join(settings.BASE_DIR, EMAIL_TEMPLATES_PATH, "user_expired_{lang}.txt".format(lang=user.profile.language))
    expire_after_days = int(get_alertas_config("days_test_subscription_expire"))
    context = {"fullname": user.get_full_name(), 'test_days': expire_after_days, "SITE_URL": settings.SITE_URL}
    message = loader.render_to_string(template_name, context)
    html_message = None

    if user.profile.send_html:
        template_name = os.path.join(settings.BASE_DIR, EMAIL_TEMPLATES_PATH, "user_expired_{lang}.html".format(lang=user.profile.language))
        html_message = loader.render_to_string(template_name, context)

    sent_emails = send_mail(NOTIFICATION_SUBJECT,
                            message,
                            EMAIL_FROM,
                            [user.email],
                            html_message=html_message)
    if sent_emails == 1:
        print("Email sent successfully to {0}".format(user.email))
    else:
        print("It looks like there was an error while sending the email to {0}".format(user.email))
