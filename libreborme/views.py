from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.generic.base import TemplateView

from borme.mixins import CacheMixin
from alertas.models import Car
from djstripe.models import Customer, Plan

from pathlib import Path

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

    # Lo que vamos a vender

    new_car = Car(name="Honda Civic", year=2017)

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
        new_car.charge_id = subscription.id

    except stripe.error.CardError as ce:
        return False, ce

    else:
        new_car.save()
        return redirect("dashboard-index")
        # The payment was successfully processed, the user's card was charged.
        # You can now redirect the user to another page or whatever you want


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')

    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
