from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.utils.safestring import mark_safe

from .models import Company, Person, Anuncio, Config, Borme
from .forms import LBSearchForm
from .utils import LibreBormeCalendar, estimate_count_fast

import datetime


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # FIXME: performance-killer: .count()

        last_modified = Config.objects.first().last_modified.date()
        context['total_companies'] = estimate_count_fast('borme_company')  #
        context['total_persons'] = estimate_count_fast('borme_person')  #
        context['total_anuncios'] = estimate_count_fast('borme_anuncio')  #
        #context['random_companies'] = Company.objects.all().order_by('?')[:10]
        #context['random_persons'] = Person.objects.all().order_by('?')[:10]
        #context['last_modified'] = Config.objects.first().last_modified
        context['random_companies'] = Company.objects.all().order_by('-date_updated')[:10]
        context['random_persons'] = Person.objects.all().order_by('-date_updated')[:10]
        #context['random_companies'] = Company.objects.filter(date_updated=last_modified).order_by('?')[:10]
        #context['random_persons'] = Person.objects.filter(date_updated=last_modified).order_by('?')[:10]
        context['last_modified'] = last_modified

        today = datetime.date.today()
        calendar = LibreBormeCalendar().formatmonth(today.year, today.month)
        context['calendar'] = mark_safe(calendar)
        return context


class BusquedaView(TemplateView):
    template_name = "busqueda.html"

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        if 'q' in self.request.GET:
            page = self.request.GET.get('page', 1)
            q_companies = Company.objects.filter(name__icontains=self.request.GET['q'])
            q_companies = list(q_companies)  # Force
            companies = Paginator(q_companies, 25)
            q_persons = Person.objects.filter(name__icontains=self.request.GET['q'])
            q_persons = list(q_persons)  # Force
            persons = Paginator(q_persons, 25)

            context['page'] = page
            context['query'] = self.request.GET['q']

            try:
                pg_companies = companies.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                pg_companies = companies.page(1)
                context['page'] = 1
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                pg_companies = companies.page(companies.num_pages)
            finally:
                context['page_companies'] = pg_companies
                context['paginator_companies'] = companies
                pagerange = companies.page_range[:3] + companies.page_range[-3:]
                pagerange.append(pg_companies.number)
                pagerange = list(set(pagerange))
                pagerange.sort()
                if len(pagerange) == 1:
                    pagerange = []
                context['page_companies'].myrange = pagerange

            try:
                pg_persons = persons.page(page)
            except PageNotAnInteger:
                pg_persons = persons.page(1)
                context['page'] = 1
            except EmptyPage:
                pg_persons = persons.page(persons.num_pages)
            finally:
                context['page_persons'] = pg_persons
                context['paginator_persons'] = persons
                pagerange = persons.page_range[:3] + persons.page_range[-3:]
                pagerange.append(pg_persons.number)
                pagerange = list(set(pagerange))
                pagerange.sort()
                if len(pagerange) == 1:
                    pagerange = []
                context['page_persons'].myrange = pagerange

        else:
            context['page_companies'] = []
            context['page_persons'] = []
            context['page'] = 1

        return context


class AnuncioView(DetailView):
    model = Anuncio
    context_object_name = 'anuncio'

    def get_object(self):
        try:
            self.anuncio = Anuncio.objects.get(id_anuncio=self.kwargs['id'], year=self.kwargs['year'])
            return self.anuncio
        except Anuncio.DoesNotExist:
            raise Http404('Anuncio does not exist')

    def get_context_data(self, **kwargs):
        context = super(AnuncioView, self).get_context_data(**kwargs)

        context['borme'] = Borme.objects.get(cve=self.anuncio.borme)
        return context


class BormeView(DetailView):
    model = Borme
    context_object_name = 'borme'

    def get_object(self):
        try:
            self.borme = Borme.objects.get(cve=self.kwargs['cve'])
            return self.borme
        except Borme.DoesNotExist:
            raise Http404('Borme does not exist')

    def get_context_data(self, **kwargs):
        context = super(BormeView, self).get_context_data(**kwargs)

        context['total_anuncios'] = self.borme.until_reg - self.borme.from_reg + 1
        context['bormes_dia'] = Borme.objects.filter(date=self.borme.date).order_by('cve')
        bormes_dia = list(context['bormes_dia'])
        bormes_dia.remove(self.borme)
        bormes_dia.sort(key=lambda b: b.province)
        context['bormes_dia'] = bormes_dia
        return context


class BormeDateView(TemplateView):
    template_name = 'borme/borme_fecha.html'

    def get_context_data(self, **kwargs):
        context = super(BormeDateView, self).get_context_data(**kwargs)

        year, month, _ = self.kwargs['date'].split('-')
        calendar = LibreBormeCalendar().formatmonth(int(year), int(month))  # TODO: LocaleHTMLCalendar(firstweekday=0, locale=None)
        #calendar = HTMLCalendar().formatyear(int(year))  # formatyearpage()

        resumen_dia = {}
        bormes = Borme.objects.filter(date=self.kwargs['date'])
        if len(bormes) > 0:
            from_reg = min([b.from_reg for b in bormes])
            until_reg = max([b.until_reg for b in bormes])
            anuncios = Anuncio.objects.filter(id_anuncio__gte=from_reg, id_anuncio__lte=until_reg)

            # FIXME: performance-killer. Guardar resultados en el modelo Borme
            from collections import Counter
            resumen_dia = Counter()
            for anuncio in anuncios:
                resumen_dia += Counter(anuncio.actos.keys())

        # TODO: Guardar la fecha en el anuncio
        context['calendar'] = mark_safe(calendar)
        context['date'] = self.kwargs['date']
        context['bormes'] = bormes
        context['resumen_dia'] = dict(resumen_dia)
        return context


class BormeProvinciaView(TemplateView):
    template_name = 'borme/borme_provincia.html'

    def get_context_data(self, **kwargs):
        context = super(BormeProvinciaView, self).get_context_data(**kwargs)
        bormes = Borme.objects.filter(province=self.kwargs['provincia'])

        year, month = 2015, 1
        calendar = LibreBormeCalendar().formatmonth(int(year), int(month))  # TODO: LocaleHTMLCalendar(firstweekday=0, locale=None)
        #calendar = HTMLCalendar().formatyear(int(year))  # formatyearpage()

        context['calendar'] = mark_safe(calendar)
        #context['date'] = self.kwargs['date']
        context['bormes'] = bormes
        context['anuncios'] = []
        return context


class CompanyView(DetailView):
    model = Company
    context_object_name = 'company'

    def get_object(self):
        try:
            self.company = Company.objects.get(slug=self.kwargs['slug'])
            return self.company
        except Company.DoesNotExist:
            raise Http404('Company does not exist')

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)

        context['anuncios'] = Anuncio.objects.filter(company=self.company).order_by('-id_anuncio')

        context['persons'] = []
        for cargo in self.company.todos_cargos_p:
            if cargo['name'] not in context['persons']:
                context['persons'].append(cargo['name'])

        context['companies'] = []
        for cargo in self.company.todos_cargos_c:
            if cargo['name'] not in context['companies']:
                context['companies'].append(cargo['name'])
        return context


class PersonView(DetailView):
    model = Person
    context_object_name = 'person'

    def get_object(self):
        try:
            self.person = Person.objects.get(slug=self.kwargs['slug'])
            return self.person
        except Person.DoesNotExist:
            raise Http404('Person does not exist')

    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)

        context['companies'] = []
        for cargo in self.person.todos_cargos:
            if cargo['name'] not in context['companies']:
                context['companies'].append(cargo['name'])
        return context


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
