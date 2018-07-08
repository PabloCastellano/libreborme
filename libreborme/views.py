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
    plan = Plan.objects.get(nickname="nuevacreacion_300")
    customer = Customer.objects.get(subscriber=request.user)
    # customer.subscribe(plan)

    new_invoice = LBInvoice(user=request.user)

    if request.method == "POST":
        token = request.POST.get("stripeToken")

    try:
        subscription = stripe.Subscription.create(
            customer=customer.stripe_id,
            items=[
                {"plan": plan.stripe_id, "quantity": 1}
            ],
            source=token
            # prorate=
        )
        new_invoice.start_date = datetime.fromtimestamp(subscription.current_period_start)
        new_invoice.end_date = datetime.fromtimestamp(subscription.current_period_end)
        new_invoice.amount = plan.amount
        new_invoice.payment_type = 'stripe'
        new_invoice.name = request.user.get_full_name()
        new_invoice.address = "TODO"
        new_invoice.nif = "TODO"
        new_invoice.is_paid = True
        new_invoice.charge_id = subscription.id

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
