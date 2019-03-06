from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils.text import slugify
from django.template.loader import render_to_string

from .utils import (
    get_alertas_config, insert_alertas_history, insert_libreborme_log,
)

from borme.models import Company
from alertas.models import EVENTOS_DICT, UserSubscription, SubscriptionEvent

import logging
import os.path


EMAIL_FROM = "noreply@libreborme.net"

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def send_expiration_email(user):
    """ Send email to user when they have been testing the service for the specified days """
    try:
        validate_email(user.email)
    except ValidationError:
        LOG.error("User has an invalid email: {}, no email sent.".format(user.email))
        return

    template_name = "email/user_expired_{lang}.txt".format(lang=user.profile.language)
    expire_after_days = int(get_alertas_config("days_test_subscription_expire"))
    context = {"fullname": user.get_full_name(), 'test_days': expire_after_days, "SITE_URL": settings.SITE_URL}
    message = render_to_string(template_name, context)
    html_message = None

    if user.profile.send_html:
        template_name = "email/user_expired_{lang}.html".format(lang=user.profile.language)
        html_message = render_to_string(template_name, context)

    sent_emails = send_mail("Su período de pruebas en Libreborme Alertas ha expirado",
                            message,
                            EMAIL_FROM,
                            [user.email],
                            html_message=html_message)
    if sent_emails == 1:
        LOG.info("Email sent successfully to {0}".format(user.email))
    else:
        LOG.error("Error sending the email to {0}".format(user.email))


def _busca_suscriptores(evento, email=None):
    subscriptions = UserSubscription.objects.filter(
        evento=evento,
        is_enabled=True,
        user__is_active=True
    )
    subscriptions = subscriptions.exclude(send_email='disabled')
    if email:
        subscriptions = subscriptions.filter(user__email=email)
    LOG.info("Total {} subscribers for event '{}' (use -v 3 for more information).".format(
        len(subscriptions),
        evento))
    LOG.debug(EVENTOS_DICT[evento])
    for sub in subscriptions:
        LOG.debug("#{0}: {1} <{2}> ({3})".format(sub.id, sub.user.get_full_name(), sub.user.email, sub.get_provincia_display()))
    return subscriptions


# django-registration
# check src/django_registration/backends/activation/views.py
# TODO: url notification webhook
def send_email_to_subscriber(evento, date, email=None):

    if evento not in EVENTOS_DICT:
        print('Evento {} is invalid. Valid values are: {}'.format(
            evento,
            ', '.join(EVENTOS_DICT.keys()))
        )
        raise ValueError(evento)

    subscriptions = _busca_suscriptores(evento, email)
    total_sent = 0
    for sub in subscriptions:
        sent = _compose_and_send_notification(sub, evento, date)
        if sent:
            total_sent += 1

    return total_sent


def _compose_and_send_notification(subscription, evento, date):

    try:
        subscription_event = SubscriptionEvent.objects.get(
            province=subscription.provincia,
            event=evento,
            event_date=date
        )
    except SubscriptionEvent.DoesNotExist:
        # The user has a paid subscription but has not configured it properly
        LOG.error("There are user subscriptions for {} and {} on {}. However data has not been imported into the DB yet".format(subscription.provincia, evento, date.isoformat()))
        return False

    results = subscription_event.data_json

    language = subscription.user.profile.language
    provincia = subscription.get_provincia_display()
    evento_display = subscription.get_evento_display()

    subject = "Tus suscripciones en LibreBORME"
    message = str(results)

    companies = {}

    for result in results:
        company_name = result["company"]["name"]
        instance = Company.get_from_name(company_name)
        companies[instance] = result["new_roles"]

    context = {"companies": sorted(companies.items()),
               "name": subscription.user.first_name,
               "provincia": provincia,
               "evento": evento_display,
               "date": date,
               "SITE_URL": settings.SITE_URL}
    template_name = "email/alerta_acto_template_{0}.txt".format(language)
    message = render_to_string(template_name, context)

    if subscription.user.profile.send_html:
        template_name = "email/alerta_acto_template_{0}.html".format(language)
        html_message = render_to_string(template_name, context)
    else:
        html_message = None

    # TODO: Enviar todos de una y no componer el email y luego mandarlo a cada uno (eficiencia)
    # TODO: [LIBREBORME]
    # TODO: Capture Smtp error
    subscription.user.email_user(subject, message, html_message=html_message)

    log_line = "{0} subscriptions sent to {1}".format(
        subscription.evento,
        subscription.user.email
    )
    insert_libreborme_log(
            "email",
            log_line,
            subscription.user.email
    )
    insert_alertas_history(
            subscription.user,
            evento,
            date,
            provincia=subscription.provincia
    )

    return True


# DEPRECATED
def send_email_notification(alerta, evento, companies, today):
    """ Send subscription email to user when there has been an event to which
        they are subscribed """

    email = alerta.user.profile.notification_email
    language = alerta.user.profile.language
    provincia = alerta.get_provincia_display()
    evento_display = alerta.get_evento_display()
    send_html = alerta.send_html

    if provincia not in companies:
        LOG.debug("No se envia a {0} porque no hay alertas para {1}/{2}".format(email, provincia, evento))
        return False
    LOG.info("Se va a enviar a {0} porque hay alertas para {1}/{2}".format(email, provincia, evento))

    companies = companies[provincia]

    try:
        validate_email(email)
        context = {"companies": companies,
                   "name": alerta.user.first_name,
                   "provincia": provincia,
                   "evento": evento_display,
                   "date": today,
                   "SITE_URL": settings.SITE_URL}
        template_name = "email/alerta_acto_template_{0}.txt".format(language)
        message = render_to_string(template_name, context)
        html_message = None

        if send_html:
            template_name = "email/alerta_acto_template_{0}.html".format(language)
            html_message = render_to_string(template_name, context)

        today_format = today.strftime("%d/%m/%Y")
        sent_emails = send_mail("Notificaciones de LibreBORME ({0}, {1}, {2})".format(today_format, evento_display, provincia),
                                message,
                                EMAIL_FROM,
                                [email],
                                html_message=html_message)
        log_line = "{0} e-mail(s) sent to {1}".format(sent_emails, email)
        insert_libreborme_log("email", log_line, alerta.user.email)
    except ValidationError:
        LOG.error("User {0} has an invalid notification email: {1}. Nothing was sent to him!".format(alerta.user.get_full_name(), email))
        # Notify user about it. Add to history anyways
    finally:
        insert_alertas_history(
                alerta.user,
                evento,
                today,
                provincia=alerta.provincia
        )

    return sent_emails == 1


# TODO: send_mass_email()
# message1 = ('Subject here', 'Here is the message', 'from@example.com', ['first@example.com', 'other@example.com'])
# message2 = ('Another Subject', 'Here is another message', 'from@example.com', ['second@test.com'])
# send_mass_mail((message1, message2), fail_silently=False)
