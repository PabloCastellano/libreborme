from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.generic.base import TemplateView

from borme.mixins import CacheMixin
from djstripe.models import Customer, Plan

from pathlib import Path

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


def create_new_invoice(request, customer, subscription, plan, user_input):
    """Creates new invoice (LBInvoice)

    Set the following fields: start_date, end_date, amount, payment_type
    name, email, address, ip, subscription_id and nif (TODO)
    """
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


def checkout(request):
    # TODO: make params
    qty = 1
    nickname = settings.DEFAULT_PLAN_MONTH
    tax_percent = 21.0  # TODO: tax per country (?)

    plan = Plan.objects.get(nickname=nickname)
    customer = Customer.objects.get(subscriber=request.user)
    next_first_timestamp = utils.date_next_first(timestamp=True)

    if request.method == "POST":
        user_input = utils.stripe_parse_input(request)
        try:
            # TODO: if not saved/save card, use the token once, otherwise
            # attach to customer
            # If the customer has already a source, use it
            if customer.has_valid_source():
                subscription = customer.subscribe(plan, quantity=qty,
                                                  tax_percent=tax_percent)
            else:
                # TODO: Use djstripe.Subscription
                subscription = stripe.Subscription.create(
                    customer=customer.stripe_id,
                    items=[
                        {"plan": plan.stripe_id, "quantity": qty}
                    ],
                    source=user_input["token"],
                    tax_percent=tax_percent,
                    billing_cycle_anchor=next_first_timestamp,
                )
            new_invoice = create_new_invoice(request, customer, subscription, plan, user_input)

        except stripe.error.CardError as ce:
            # :?
            return False, ce

        else:
            new_invoice.save()
            return redirect("dashboard-index")

    return HttpResponse("", status=400)


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
