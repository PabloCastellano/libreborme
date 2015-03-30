from django.shortcuts import get_object_or_404

#from django.views.generic import TemplateView, ListView, DetailView
from mongogeneric.list import ListView
from mongogeneric.detail import DetailView
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from models import Company, Person, Acto

from random import randint

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['total_companies'] = Company.objects.count()
        context['total_persons'] = Person.objects.count()
        context['total_regs'] = Acto.objects.count()
        context['random_companies'] = Company.objects.filter().limit(10).skip(randint(0, context['total_companies']))
        context['random_persons'] = Person.objects.filter().limit(10).skip(randint(0, context['total_persons']))
        return context


class BusquedaView(TemplateView):
    template_name = "busqueda.html"

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        if 'q' in self.request.GET:
            page = self.request.GET.get('page', 1)
            q_companies = Company.objects.filter(name__icontains=self.request.GET['q'])
            companies = Paginator(q_companies, 25)
            q_persons = Person.objects.filter(name__icontains=self.request.GET['q'])
            persons = Paginator(q_persons, 25)

            context['num_companies'] = persons.count
            context['num_persons'] = companies.count
            context['page'] = page
            context['query'] = self.request.GET['q']

            try:
                context['companies'] = companies.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                context['companies'] = companies.page(1)
                context['page'] = 1
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                context['companies'] = companies.page(companies.num_pages)

            try:
                context['persons'] = persons.page(page)
            except PageNotAnInteger:
                context['persons'] = persons.page(1)
                context['page'] = 1
            except EmptyPage:
                context['persons'] = persons.page(persons.num_pages)

        else:
            context['num_companies'] = 0
            context['num_persons'] = 0
            context['companies'] = []
            context['persons'] = []

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

        try:
            context['registros'] = Acto.objects.filter(company=self.company[0].slug)
        except Acto.DoesNotExist:
            context['registros'] = ()

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
