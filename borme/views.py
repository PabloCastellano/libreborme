from django.shortcuts import get_object_or_404

#from django.views.generic import TemplateView, ListView, DetailView
from mongogeneric.list import ListView
from mongogeneric.detail import DetailView
from django.views.generic import TemplateView

from models import Company, Person, Acto

from random import randint

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['total_companies'] = Company.objects.count()
        context['total_persons'] = Person.objects.count()
        context['total_regs'] = Acto.objects.count()
        context['random_companies'] = Company.objects.filter().limit(5).skip(randint(0, context['total_companies']))
        context['random_persons'] = Person.objects.filter().limit(5).skip(randint(0, context['total_persons']))
        return context


class BusquedaView(TemplateView):
    template_name = "busqueda.html"

    # TODO: paginar
    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        if self.request.GET['q']:
            context['companies'] = Company.objects.filter(name__icontains=self.request.GET['q'])
            context['persons'] = Person.objects.filter(name__icontains=self.request.GET['q'])
            context['num_persons'] = len(context['persons'])
            context['num_companies'] = len(context['companies'])
        return context


class CompanyView(DetailView):
    model = Company
    context_object_name = 'company'
    #queryset = Company.objects.all()

    def get_queryset(self):
        #self.company = get_object_or_404(Company, slug=self.kwargs['slug'])
        self.company = Company.objects.filter(slug=self.kwargs['slug'])
        return self.company

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)
        from django.utils import timezone
        context['now'] = timezone.now()
        #print self.company
        try:
            context['registros'] = Acto.objects.filter(company=self.company[0].slug)
        except Acto.DoesNotExist:
            context['registros'] = ()
        print context['registros']
        for reg in context['registros']:
            print reg.__dict__
            print
        # filter None
        return context


class PersonView(DetailView):
    model = Person
    context_object_name = 'person'
    #queryset = Person.objects.all()

    def get_queryset(self):
        #self.company = get_object_or_404(Company, slug=self.kwargs['slug'])
        self.person = Person.objects.filter(slug=self.kwargs['slug'])
        return self.person


class PersonListView(ListView):
    model = Person
    context_object_name = 'people'
    queryset = Person.objects.all()[:100]


class CompanyListView(ListView):
    model = Company
    context_object_name = 'companies'
    queryset = Company.objects.all()[:100]


class CompanyProvinceListView(ListView):
    #model = Company
    context_object_name = 'companies'
    #queryset = Book.objects.filter(province==X).order_by('-name')
