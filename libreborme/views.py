from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.generic.base import TemplateView

from borme.mixins import CacheMixin
from djstripe.models import Customer, Plan

from pathlib import Path
import datetime

from alertas.models import LBInvoice

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


def checkout(request):
    # TODO: make params
    qty = 1
    nickname = "Subscription Yearly"
    tax_percent = 21.0  # TODO: tax per country (?)

    plan = Plan.objects.get(nickname=nickname)
    customer = Customer.objects.get(subscriber=request.user)
    next_first_timestamp = utils.date_next_first(timestamp=True)

    if request.method == "POST":
        user_input = utils.stripe_parse_input(request)
        try:
            new_invoice.ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            new_invoice.ip = request.META['REMOTE_ADDR']
        new_invoice.subscription_id = subscription.id

    except stripe.error.CardError as ce:
        return False, ce

    else:
        new_invoice.save()
        return redirect("dashboard-index")
        # The payment was successfully processed, the user's card was charged.
        # You can now redirect the user to another page or whatever you want


def register(request):
    if request.method == 'POST':
        form = LBUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')

    else:
        form = LBUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
