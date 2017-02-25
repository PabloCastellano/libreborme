from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import TemplateView

from .models import AlertaActo, AlertaCompany, AlertaPerson


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


class AlertaCompanyCreateView(CreateView):
    model = AlertaCompany
    fields = ("user", "company", "send_html")
