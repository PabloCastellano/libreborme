from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.template import RequestContext

from .models import AlertaActo, AlertaCompany, AlertaPerson
from . import forms


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'alertas/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        n_alertas = AlertaActo.objects.filter(user=self.request.user).count()
        n_alertas += AlertaCompany.objects.filter(user=self.request.user).count()
        n_alertas += AlertaPerson.objects.filter(user=self.request.user).count()
        context['n_alertas'] = n_alertas
        return context


@method_decorator(login_required, name='dispatch')
class BillingView(TemplateView):
    template_name = 'alertas/billing.html'


@method_decorator(login_required, name='dispatch')
class AlertaDetailView(DetailView):
    model = AlertaActo
    context_object_name = 'alerta'

    def get_object(self):
        self.alerta = AlertaActo.objects.get(pk=self.kwargs['id'])
        return self.alerta

    def get_context_data(self, **kwargs):
        context = super(AlertaDetailView, self).get_context_data(**kwargs)
        context['breadcrumb'] = 'TODO BREADCRUMB'
        return context


@method_decorator(login_required, name='dispatch')
class AlertaListView(TemplateView):
    template_name = "alertas/alerta_list.html"

    def get_context_data(self, **kwargs):
        context = super(AlertaListView, self).get_context_data(**kwargs)
        context['alertas_c'] = AlertaCompany.objects.filter(user=self.request.user)
        context['alertas_p'] = AlertaPerson.objects.filter(user=self.request.user)
        context['alertas_a'] = AlertaActo.objects.filter(user=self.request.user)
        context['form_c'] = forms.AlertaCompanyModelForm()
        context['form_p'] = forms.AlertaPersonModelForm()
        context['form_a'] = forms.AlertaActoModelForm()
        context['breadcrumb'] = 'TODO BREADCRUMB'
        return context


def alerta_person_create(request):
    if request.method == 'POST':
        form = forms.AlertaPersonModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


def alerta_company_create(request):
    if request.method == 'POST':
        form = forms.AlertaCompanyModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


def alerta_acto_create(request):
    if request.method == 'POST':
        form = forms.AlertaActoModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


# TODO: una funcion por cada tipo de form
# No mezclarlas

@login_required
def alerta_create(request):
    context = {}
    context['form_c'] = forms.AlertaCompanyModelForm()
    context['form_p'] = forms.AlertaPersonModelForm()
    context['form_a'] = forms.AlertaActoModelForm()

    return render(request, 'alertas/alerta_new.html', context)


@method_decorator(login_required, name='dispatch')
class AlertaActoCreateView(CreateView):
    model = AlertaCompany
    fields = ("company", "send_html")

# No vale CreateView porque la lista para elegir empresa/persona sería inmensa 

# #        - En liquidación
#        - Concurso de acreedores