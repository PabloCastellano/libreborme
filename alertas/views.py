from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.urls import reverse

from .models import (
        AlertaActo, AlertaCompany, AlertaHistory,
        AlertaPerson, LBInvoice)
from borme.models import Person
from borme.templatetags.utils import slug, slug2
from . import forms

from djstripe.models import Customer, Event, Plan
from libreborme.models import Profile

import datetime
import json
import stripe

from .utils import get_alertas_config


MAX_RESULTS_AJAX = 15


@method_decorator(login_required, name='dispatch')
class MyAccountView(TemplateView):
    template_name = 'alertas/myaccount.html'

    def get_context_data(self, **kwargs):
        context = super(MyAccountView, self).get_context_data(**kwargs)

        context['active'] = 'dashboard'

        context['count_c'] = AlertaCompany.objects.filter(
                                    user=self.request.user).count()
        context['count_p'] = AlertaPerson.objects.filter(
                                    user=self.request.user).count()
        context['count_a'] = AlertaActo.objects.filter(
                                    user=self.request.user).count()
        context['n_alertas'] = context['count_c'] + context['count_p'] + context['count_a']

        today = datetime.date.today()
        context['lbinvoices'] = LBInvoice.objects.filter(
                                    user=self.request.user, end_date__gt=today)

        alertas_config = get_alertas_config()
        account_type = self.request.user.profile.account_type

        context['limite_c'] = alertas_config['max_alertas_company_' + account_type]
        context['limite_p'] = alertas_config['max_alertas_person_' + account_type]
        context['limite_a'] = alertas_config['max_alertas_actos_' + account_type]

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer

        try:
            context['ip'] = self.request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            context['ip'] = self.request.META['REMOTE_ADDR']
        return context


@method_decorator(login_required, name='dispatch')
class DashboardSupportView(TemplateView):
    template_name = 'alertas/dashboard_support.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSupportView, self).get_context_data(**kwargs)
        n_alertas = AlertaActo.objects.filter(user=self.request.user).count()
        n_alertas += AlertaCompany.objects.filter(user=self.request.user).count()
        n_alertas += AlertaPerson.objects.filter(user=self.request.user).count()
        context['n_alertas'] = n_alertas
        context['active'] = 'ayuda'
        return context


@method_decorator(login_required, name='dispatch')
class DashboardSettingsView(TemplateView):
    template_name = 'alertas/dashboard_settings.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSettingsView, self).get_context_data(**kwargs)
        context['active'] = 'settings'
        context['form_personal'] = forms.PersonalSettingsForm(initial={'email': self.request.user.email})

        initial = {}
        initial['notification_method'] = self.request.user.profile.notification_method
        initial['notification_email'] = self.request.user.profile.notification_email
        initial['notification_url'] = self.request.user.profile.notification_url

        context['form_notification'] = forms.NotificationSettingsForm(initial=initial)

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer
        context["form_billing"] = forms.BillingSettingsForm(initial={'business_vat_id': customer.business_vat_id})
        return context


# TODO: Pagination
@method_decorator(login_required, name='dispatch')
class DashboardHistoryView(TemplateView):
    template_name = 'alertas/dashboard_history.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardHistoryView, self).get_context_data(**kwargs)
        context['alertas'] = AlertaHistory.objects.filter(user=self.request.user)
        context['active'] = 'history'
        return context


@method_decorator(login_required, name='dispatch')
class PaymentView(TemplateView):
    template_name = 'alertas/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['active'] = 'payment'

        # TODO: get or 500
        customer = Customer.objects.get(subscriber=self.request.user)
        context['customer'] = customer

        context["cards"] = customer.sources.order_by('-exp_year', '-exp_month')
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY

        return context


@method_decorator(login_required, name='dispatch')
class BillingView(TemplateView):
    template_name = 'alertas/billing.html'

    def get_context_data(self, **kwargs):
        context = super(BillingView, self).get_context_data(**kwargs)
        context['active'] = 'billing'
        context['lbinvoices'] = LBInvoice.objects.filter(user=self.request.user)

        # TODO: get or 500
        customer = Customer.objects.get(subscriber=self.request.user)
        context['customer'] = customer
        context['charges'] = customer.charges.all()
        context['invoices'] = customer.invoices.all()

        try:
            context["upcoming_invoice"] = customer.upcoming_invoice()
        except stripe.error.InvalidRequestError:
            context["upcoming_invoice"] = None

        return context


@method_decorator(login_required, name='dispatch')
class BillingDetailView(DetailView):
    model = LBInvoice

    def get_object(self):
        self.invoice = LBInvoice.objects.get(user=self.request.user, pk=self.kwargs['id'])
        return self.invoice

    def get_context_data(self, **kwargs):
        context = super(BillingDetailView, self).get_context_data(**kwargs)
        context['active'] = 'billing'
        return context


@method_decorator(login_required, name='dispatch')
class AlertaDetailView(DetailView):
    model = AlertaActo
    context_object_name = 'alerta'

    def get_object(self):
        self.alerta = AlertaActo.objects.get(pk=self.kwargs['id'])
        return self.alerta


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AlertaEventsView(TemplateView):
    template_name = "alertas/events_list.html"

    def get_context_data(self, **kwargs):
        context = super(AlertaEventsView, self).get_context_data(**kwargs)
        context['active'] = 'events'

        events_by_date = {}
        for e in Event.objects.all().order_by('-created'):
            e.data_json = json.dumps(e.data)
            e.metadata_json = json.dumps(e.metadata)
            date = e.created.date()
            events_by_date.setdefault(date, [])
            events_by_date[date].append(e)
        context['events_by_date'] = events_by_date
        return context


@method_decorator(login_required, name='dispatch')
class SubscriptionListView(TemplateView):
    template_name = "alertas/subscription_list.html"

    def get_context_data(self, **kwargs):
        context = super(SubscriptionListView, self).get_context_data(**kwargs)

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY

        return context


@method_decorator(login_required, name='dispatch')
class AlertaListView(TemplateView):
    template_name = "alertas/alerta_list.html"

    def get_context_data(self, **kwargs):
        context = super(AlertaListView, self).get_context_data(**kwargs)
        context['alertas_c'] = AlertaCompany.objects.filter(user=self.request.user)
        context['alertas_p'] = AlertaPerson.objects.filter(user=self.request.user)
        context['alertas_a'] = AlertaActo.objects.filter(user=self.request.user)
        context['form_c'] = forms.AlertaCompanyForm()
        context['form_p'] = forms.AlertaPersonForm()
        context['form_a'] = forms.AlertaActoModelForm()

        context['count_c'] = context['alertas_c'].count()
        context['count_p'] = context['alertas_p'].count()
        context['count_a'] = context['alertas_a'].count()

        alertas_config = get_alertas_config()
        account_type = self.request.user.profile.account_type

        context['limite_c'] = alertas_config['max_alertas_company_' + account_type]
        context['limite_p'] = alertas_config['max_alertas_person_' + account_type]
        context['limite_a'] = alertas_config['max_alertas_actos_' + account_type]

        context['restantes_c'] = int(context['limite_c']) - context['count_c']
        context['restantes_p'] = int(context['limite_p']) - context['count_p']
        context['restantes_a'] = int(context['limite_a']) - context['count_a']

        context['active'] = 'alertas'

        context['email'] = self.request.user.email

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer

        plan_year = Plan.objects.get(nickname=settings.DEFAULT_PLAN_YEAR)
        context["plan_year"] = {
            "label": "Suscripción anual",
            "amount": plan_year.amount * 100
        }
        plan_month = Plan.objects.get(nickname=settings.DEFAULT_PLAN_MONTH)
        context["plan_month"] = {
            "label": "Suscripción mensual",
            "amount": plan_month.amount * 100
        }

        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY
        return context


@login_required
def alerta_person_create(request):
    if request.method == 'POST':
        form = forms.AlertaPersonModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


@login_required
def alerta_company_create(request):
    if request.method == 'POST':
        form = forms.AlertaCompanyModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


@login_required
def alerta_acto_create(request):
    if request.method == 'POST':
        form = forms.AlertaActoModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


@login_required
def settings_update_notifications(request):
    if request.method == 'POST':
        form = forms.NotificationSettingsForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile.notification_method = form.cleaned_data['notification_method']
            profile.notification_email = form.cleaned_data['notification_email']
            profile.notification_url = form.cleaned_data['notification_url']
            profile.save()
    return redirect(reverse('alertas-settings'))


@login_required
def settings_update_personal(request):
    if request.method == 'POST':
        instance = User.objects.get(pk=request.user.id)
        form = forms.PersonalSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    return redirect(reverse('alertas-settings'))


@login_required
def settings_update_billing(request):
    if request.method == 'POST':
        instance = Customer.objects.get(subscriber=request.user)
        form = forms.BillingSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    return redirect(reverse('alertas-settings'))


@login_required
def settings_update_stripe(request):

    user_input = {}

    if request.method == 'POST':
        customer = Customer.objects.get(subscriber=request.user)

        user_input["token"] = request.POST.get("stripeToken")
        user_input["email"] = request.POST.get("stripeEmail")
        # Billing
        user_input["name"] = request.POST.get("stripeBillingName")
        user_input["address"] = request.POST.get("stripeBillingAddressLine1")
        user_input["zipcode"] = request.POST.get("stripeBillingAddressZip")
        user_input["state"] = request.POST.get("stripeBillingAddressState", "")
        user_input["city"] = request.POST.get("stripeBillingAddressCity")
        user_input["country"] = request.POST.get("stripeBillingAddressCountry")
        user_input["countrycode"] = request.POST.get("stripeBillingAddressCountryCode")

        if user_input["country"] != "Spain":
            logger.warning("Customer {} has entered a billing address whose "
                           "country ir not Spain: {}".format(
                                customer.stripe_id, user_input["country"]))

        customer.add_card(source=user_input["token"])
        customer.save()
        messages.add_message(request, messages.INFO,
                             'Tarjeta añadida correctamente')

    return redirect(reverse('alertas-payment'))


@login_required
def set_default_card(request):

    # FIXME: weird, mixed POST + GET
    if request.method == 'POST':
        card_id = request.GET.get("cardId")

        customer = Customer.objects.get(subscriber=request.user)
        customer.default_source_id = card_id
        try:
            customer.save()
            messages.add_message(request, messages.INFO,
                                 'Tarjeta modificada correctamente')
            return HttpResponse("Success", status=200)
        except Exception:
            print("Could not set default card " + card_id + " for customer " + customer.stripe_id)
            return HttpResponse("Fail", status=400)

    return HttpResponse("Fail", status=400)


@login_required
def remove_card(request):

    # FIXME: weird, mixed POST + GET
    if request.method == 'POST':
        card_id = request.GET.get("cardId")

        customer = Customer.objects.get(subscriber=request.user)
        cards = customer.sources.all()
        for card in cards:
            if card.stripe_id == card_id:
                card.remove()
                messages.add_message(request, messages.INFO,
                                     'Tarjeta eliminada correctamente')
                return HttpResponse("Success", status=200)

        print("Could not delete card " + card_id + " for customer " + customer.stripe_id)

    return HttpResponse("Fail", status=400)


@login_required
def alerta_remove_acto(request, id):
    alerta = AlertaActo.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('alertas-list'))


@login_required
def alerta_remove_person(request, id):
    alerta = AlertaPerson.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('alertas-list'))


@login_required
def alerta_remove_company(request, id):
    alerta = AlertaCompany.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('alertas-list'))


@method_decorator(login_required, name='dispatch')
class AlertaActoCreateView(CreateView):
    model = AlertaCompany
    fields = ("company", "send_html")


# TODO: CSRF con POST
@login_required
def suggest_company(request):
    results = []
    if request.method == "GET" and request.is_ajax():
        term = request.GET.get("term").strip()
        if len(term) > 2:
            # FIXME: elasticsearch
            # search_results = SearchQuerySet().filter(content=term).models(Company)[:MAX_RESULTS_AJAX]
            search_results = []

            for result in search_results:
                results.append({"id": slug2(result.text), "value": result.text})

    return HttpResponse(json.dumps(results), content_type="application/json")


@login_required
def suggest_person(request):
    results = []
    if request.method == "GET" and request.is_ajax():
        term = request.GET.get("term").strip()
        if len(term) > 2:
            search_results = SearchQuerySet().filter(content=term).models(Person)[:MAX_RESULTS_AJAX]

            for result in search_results:
                results.append({"id": slug(result.text), "value": result.text})

    return HttpResponse(json.dumps(results), content_type="application/json")


@login_required
def download_alerta_history_csv(request, id):

    try:
        alerta = AlertaHistory.objects.get(pk=id, user=request.user)

        path = alerta.get_csv_path()
        provincia = alerta.get_provincia_display().replace(" ", "_")
        filename = '{0}_{1}_{2}.csv'.format(alerta.type, provincia, alerta.date.isoformat())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

        # TODO: Passing iterators
        # https://docs.djangoproject.com/en/dev/ref/request-response/#passing-iterators
        with open(path) as fp:
            response.write(fp.read())

    except AlertaHistory.DoesNotExist:
        response = HttpResponse()

    return response


# No vale CreateView porque la lista para elegir empresa/persona sería inmensa

# #        - En liquidación
#        - Concurso de acreedores