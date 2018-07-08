from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.generic.base import TemplateView

from borme.mixins import CacheMixin
from djstripe.models import Customer, Plan

from pathlib import Path
from datetime import datetime

from alertas.models import LBInvoice

from .forms import LBUserCreationForm

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

    new_invoice = LBInvoice(user=request.user)
    user_input = {}

    if request.method == "POST":
        user_input["token"] = request.POST.get("stripeToken")
        user_input["email"] = request.POST.get("stripeEmail")
        # Billing
        user_input["name"] = request.POST.get("stripeBillingName")
        user_input["address"] = request.POST.get("stripeBillingAddressLine1")
        user_input["zipcode"] = request.POST.get("stripeBillingAddressZip")
        user_input["state"] = request.POST.get("stripeBillingAddressState")
        user_input["city"] = request.POST.get("stripeBillingAddressCity")
        user_input["country"] = request.POST.get("stripeBillingAddressCountry")

    try:
        # TODO: if not saved/save card, use the token once, otherwise
        # attach to customer
        # If the customer has already a source, use it
        if customer.default_source:
            subscription = customer.subscribe(plan, quantity=qty,
                                              tax_percent=tax_percent)
        else:
            subscription = stripe.Subscription.create(
                customer=customer.stripe_id,
                items=[
                    {"plan": plan.stripe_id, "quantity": qty}
                ],
                source=user_input["token"],
                tax_percent=tax_percent,  # TODO: tax per country (?)
                # prorate=
            )
        new_invoice.start_date = datetime.fromtimestamp(subscription.current_period_start)
        new_invoice.end_date = datetime.fromtimestamp(subscription.current_period_end)
        new_invoice.amount = plan.amount
        new_invoice.payment_type = 'stripe'
        new_invoice.name = user_input["name"]
        new_invoice.email = user_input["email"]
        new_invoice.address = ", ".join(user_input["address"], user_input["zipcode"], user_input["state"], user_input["city"], user_input["country"])
        new_invoice.nif = "TODO"
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
