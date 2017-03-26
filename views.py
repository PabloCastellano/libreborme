from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import AlertaActo, AlertaCompany, AlertaHistory, AlertaPerson, LBInvoice, Profile
from borme.models import Company, Person
from borme.templatetags.utils import slug, slug2
from . import forms

import datetime
import json

from .utils import get_alertas_config

from haystack.query import SearchQuerySet


MAX_RESULTS_AJAX = 15


@method_decorator(login_required, name='dispatch')
class DashboardIndexView(TemplateView):
    template_name = 'alertas/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardIndexView, self).get_context_data(**kwargs)

        context['active'] = 'dashboard'

        context['count_c'] = AlertaCompany.objects.filter(user=self.request.user).count()
        context['count_p'] = AlertaPerson.objects.filter(user=self.request.user).count()
        context['count_a'] = AlertaActo.objects.filter(user=self.request.user).count()
        context['n_alertas'] = context['count_c'] + context['count_p'] + context['count_a']

        today = datetime.date.today()
        context['subscriptions'] = LBInvoice.objects.filter(user=self.request.user, end_date__gt=today)

        alertas_config = get_alertas_config()
        account_type = self.request.user.profile.account_type

        context['limite_c'] = alertas_config['max_alertas_company_' + account_type]
        context['limite_p'] = alertas_config['max_alertas_person_' + account_type]
        context['limite_a'] = alertas_config['max_alertas_actos_' + account_type]
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
        context['active'] = 'soporte'
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
class BillingView(TemplateView):
    template_name = 'alertas/billing.html'

    def get_context_data(self, **kwargs):
        context = super(BillingView, self).get_context_data(**kwargs)
        context['active'] = 'billing'
        context['invoices'] = LBInvoice.objects.filter(user=self.request.user)

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
            search_results = SearchQuerySet().filter(content=term).models(Company)[:MAX_RESULTS_AJAX]

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
        filename = '{0}_{1}_{2}_{3}.csv'.format(alerta.type, alerta.provincia, alerta.periodicidad, alerta.date.isoformat())
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
