from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.generic.base import TemplateView

from borme.mixins import CacheMixin
from djstripe.models import Customer, Plan

from pathlib import Path

from .forms import LBUserCreationForm
from . import utils

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class AvisoLegalView(CacheMixin, TemplateView):
    template_name = "libreborme/aviso_legal.html"

    def get_context_data(self, **kwargs):
        context = super(AvisoLegalView, self).get_context_data(**kwargs)
        context['lopd'] = settings.LOPD
        return context


class AboutView(CacheMixin, TemplateView):
    template_name = "libreborme/about.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['HOST_BUCKET'] = settings.HOST_BUCKET
        return context


def robotstxt(request):
    """Check if static robots.txt exists, otherwise return default template"""
    response = None
    static_root = settings.STATIC_ROOT
    if static_root is not None:
        filename = Path(static_root) / "robots.txt"
        if filename.exists():
            with open(filename.as_posix()) as fp:
                response = fp.read()

    if response is None:
        template = get_template('robots.txt')
        response = template.render()

    return HttpResponse(response, content_type='text/plain')


# XXX: Do we really need this?
"""Creates new invoice (LBInvoice)

Set the following fields: start_date, end_date, amount, payment_type
name, email, address, ip, subscription_id and nif (TODO)
"""
"""
def create_new_invoice(request, customer, subscription, plan, user_input):
    new_invoice = LBInvoice(user=request.user)
    new_invoice.start_date = subscription.current_period_start
    new_invoice.end_date = subscription.current_period_end
    new_invoice.amount = plan.amount
    new_invoice.payment_type = 'stripe'
    new_invoice.name = user_input["name"]
    new_invoice.email = user_input["email"]
    new_invoice.address = ", ".join([user_input["address"],
                                     user_input["zipcode"],
                                     user_input["state"],
                                     user_input["city"],
                                     user_input["country"]])
    new_invoice.ip = request.META.get('HTTP_X_FORWARDED_FOR',
                                      request.META['REMOTE_ADDR'])
    new_invoice.subscription_id = subscription.stripe_id
    new_invoice.nif = customer.business_vat_id or "TODO"
    return new_invoice
"""
