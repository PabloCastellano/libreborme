"""
https://stripe.com/docs/api/events/types

Docs:
https://github.com/dj-stripe/dj-stripe/issues/791
https://github.com/dj-stripe/dj-stripe/issues/782
https://github.com/dj-stripe/dj-stripe/issues/419
"""
from django.core.mail import mail_admins

from djstripe import webhooks

import datetime


@webhooks.handler("customer.subscription.created")
def customer_subscription_created(event, **kwargs):
    """
    Notify to admins
    """
    print("Webhook " + event.type)
    now = datetime.datetime.now()
    user = event.customer.subscriber
    full_name = user.get_full_name()
    subject = 'Libreborme webhook triggered: ' + event.type
    message = """\
Nueva suscripción

El {} se ha suscrito al usuario {} ({})
""".format(
        now.strftime("%c"), full_name, user.email)
    mail_admins(subject, message)


# https://stripe.com/docs/recipes/sending-emails-for-failed-payments
@webhooks.handler("invoice.payment_failed")
def invoice_payment_failed(event, **kwargs):
    """
    Notify to admins and user
    """
    print("Webhook " + event.type)
    now = datetime.datetime.now()
    user = event.customer.subscriber
    full_name = user.get_full_name()
    subject = 'Libreborme webhook triggered: ' + event.type
    subject = 'Payment failed ({}) (webhook)'.format(full_name)
    message = """\
Pago fallido

El {} ha fallado al cobrar al usuario {} ({})
""".format(
        now.strftime("%c"), full_name, user.email)
    mail_admins(subject, message)

    # TODO: Usar MailTemplate's
    subject = "Tu último pago ha fallado"
    message = """No hemos podido hacer el cargo de la última factura de %(amount) euros.
Esto puede ser debido a un cambio en el número de tu tarjeta o a que la tarjeta ha expirado o ha sido cancelada.

Por favor actualiza tu método de pago tan pronto como sea posible para que no interrumpamos el servicio.

%(url) métodos de pago
"""
    user.email_user(
        subject=subject,
        message=message
    )


@webhooks.handler("customer.created")
def customer_created(event, **kwargs):
    """
    Notify to admins
    """
    print("Webhook " + event.type)
    now = datetime.datetime.now()
    customer = event.customer
    # FIXME: If created thru the Stripe dashboard, user won't exist
    # user = event.customer.subscriber
    # full_name = user.get_full_name()
    subject = 'Libreborme webhook triggered: ' + event.type
    message = """\
Nuevo customer

El {} se ha creado un nuevo customer {}.
""".format(
        now.strftime("%c"), customer.email)
    mail_admins(subject, message)


"""
@webhooks.handler("customer")
def customer_created(event, **kwargs):
    print("Webhook " + event.type)
    subject = 'Webhook: ' + event.type
    message = '%r\n' % (event)
    mail_admins(subject, message)
"""
