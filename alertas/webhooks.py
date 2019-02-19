from django.core.mail import mail_admins

from djstripe import webhooks

import datetime

# Docs:
# https://github.com/dj-stripe/dj-stripe/issues/791
# https://github.com/dj-stripe/dj-stripe/issues/782
# https://github.com/dj-stripe/dj-stripe/issues/419
@webhooks.handler("customer.subscription.created")
def subscription_created(event, event_data, event_type, event_subtype):
    user = event.customer.subscriber
    full_name = user.get_full_name()
    now = datetime.datetime.now()
    subject = 'Nueva suscripción ({}) (webhook)'.format(full_name)
    message = 'En {} Stripe ha suscrito al usuario {}'.format(
        now.strftime("%c"), full_name)
    mail_admins(subject, message)
