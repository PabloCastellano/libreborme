from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import TemplateView

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
        context['breadcrumb'] = 'TODO BREADCRUMB'
        return context

@login_required
def alerta_create(request):
    context = {}
    context['form_c'] = forms.AlertaCompanyForm()
    context['form_p'] = forms.AlertaPersonForm()
    context['form_a'] = forms.AlertaActoForm()

    return render(request, 'alertas/alerta_new.html', context)


@method_decorator(login_required, name='dispatch')
class AlertaActoCreateView(CreateView):
    model = AlertaCompany
    fields = ("company", "send_html")

# No vale CreateView porque la lista para elegir empresa/persona sería inmensa 

# #        - En liquidación
#        - Concurso de acreedores