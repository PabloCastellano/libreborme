from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.template.loader import get_template
from django.conf import settings

from .documents import CompanyDocument, PersonDocument
from .models import Company, Person, Anuncio, Config, Borme
from .calendar import LibreBormeCalendar, LibreBormeAvailableCalendar
from .utils.postgres import estimate_count_fast, search_fts
from .mixins import CacheMixin

import datetime
import csv


def ajax_empresa_more(request, slug):
    company = Company.objects.get(slug=slug)
    offset = int(request.GET.get('offset', 0)) + settings.CARGOS_LIMIT
    t = request.GET.get('t', 'actuales')

    if t == 'actuales':
        cargos, show_more = company.get_cargos_actuales(offset=offset)
        template = get_template('borme/tables/cargos_actuales.html')
    else:
        cargos, show_more = company.get_cargos_historial(offset=offset)
        template = get_template('borme/tables/cargos_historial.html')

    response = ""
    for cargo in cargos:
        response += template.render({'cargo': cargo})

    if show_more:
        next_ajax_url = reverse('borme-ajax-empresa', kwargs={'slug': slug}) + '?offset=' + str(offset) + '&t=' + t
        response += ('<tr id="vermascargos_{t}">'
                    '  <td class="text-center" colspan=4>'
                    '    <a href="#" onclick="javascript:moreData(\'{url}\',\'vermascargos_{t}\',\'tabla_cargos_{t}\');return false;">Ver más</a>'
                    '  </td>'
                    '</tr>').format(t=t, url=next_ajax_url)
    return HttpResponse(response)


@cache_page(3600)
def generate_person_csv_cargos_actual(context, slug):
    person = Person.objects.get(slug=slug)
    filename = 'cargos_actuales_%s_%s' % (slug, datetime.date.today().isoformat())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename

    writer = csv.writer(response)
    writer.writerow(['Cargo', 'Nombre', 'Desde', 'Hasta'])
    for cargo in person.get_cargos_actuales(limit=0)[0]:
        writer.writerow([cargo['title'], cargo['name'], cargo['date_from'], ""])

    return response


@cache_page(3600)
def generate_person_csv_cargos_historial(context, slug):
    person = Person.objects.get(slug=slug)
    filename = 'cargos_historial_%s_%s' % (slug, datetime.date.today().isoformat())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename

    writer = csv.writer(response)
    writer.writerow(['Cargo', 'Nombre', 'Desde', 'Hasta'])
    for cargo in person.get_cargos_historial(limit=0)[0]:
        date_from = cargo.get('date_from', '')
        writer.writerow([cargo['title'], cargo['name'], date_from, cargo['date_to']])

    return response


@cache_page(3600)
def generate_company_csv_cargos_actual(context, slug):
    company = Company.objects.get(slug=slug)
    filename = 'cargos_actuales_%s_%s' % (slug, datetime.date.today().isoformat())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename

    writer = csv.writer(response)
    writer.writerow(['Cargo', 'Nombre', 'Desde', 'Hasta', 'Tipo'])
    for cargo in company.get_cargos_actuales(limit=0)[0]:
        name = cargo['name'] if cargo['type'] == 'company' else cargo['name'].title()
        writer.writerow([cargo['title'], name, cargo['date_from'], '', cargo['type']])

    return response


@cache_page(3600)
def generate_company_csv_cargos_historial(context, slug):
    company = Company.objects.get(slug=slug)
    filename = "cargos_historial_{}_{}" \
               .format(slug, datetime.date.today().isoformat())
    content_disposition = 'attachment; filename="%s.csv"' % filename

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition

    writer = csv.writer(response)
    writer.writerow(['Cargo', 'Nombre', 'Desde', 'Hasta', 'Tipo'])
    for cargo in company.get_cargos_historial(limit=0)[0]:
        date_from = cargo.get('date_from', '')
        name = cargo['name'] if cargo['type'] == 'company' else cargo['name'].title()
        writer.writerow(
            [cargo['title'], name, date_from, cargo['date_to'], cargo['type']]
        )

    return response


class HomeView(CacheMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        """
        Using .count() in PostgreSQL kills performance,
        so we use a method to estimate the number of rows in the tables
        """
        context = super(HomeView, self).get_context_data(**kwargs)

        random_companies = Company.objects.all().order_by('-date_updated')[:10]
        random_persons = Person.objects.all().order_by('-date_updated')[:10]
        last_modified = Config.objects.first().last_modified.date()
        lb_calendar = LibreBormeCalendar().formatmonth(datetime.date.today())

        context.update({
            "total_companies": estimate_count_fast('borme_company'),
            "total_persons": estimate_count_fast('borme_person'),
            "total_anuncios": estimate_count_fast('borme_anuncio'),
            "random_companies": random_companies,
            "random_persons": random_persons,
            "last_modified": last_modified,
            "calendar": mark_safe(lb_calendar),
        })

        return context


# TODO:  if 'q' not in request.GET
class BusquedaView(TemplateView):
    template_name = "busqueda.html"
    # template = "search/search.html"

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        if 'q' in self.request.GET:
            page = self.request.GET.get('page', 1)
            raw_query = self.request.GET['q']
            q_companies = CompanyDocument.search().query("match", name=raw_query)
            q_persons = PersonDocument.search().query("match", name=raw_query)

            companies = Paginator(q_companies.to_queryset(), 25)
            persons = Paginator(q_persons.to_queryset(), 25)

            context['page'] = page
            context['query'] = raw_query

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
                pagerange = list(companies.page_range[:3]) + list(companies.page_range[-3:])
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
                pagerange = list(persons.page_range[:3]) + list(persons.page_range[-3:])
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


class AnuncioView(CacheMixin, DetailView):
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


class BormeView(CacheMixin, DetailView):
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

        anuncios = Anuncio.objects.filter(id_anuncio__gte=self.borme.from_reg,
                                          id_anuncio__lte=self.borme.until_reg,
                                          year=self.borme.date.year)
        from collections import Counter
        resumen_dia = Counter()
        for anuncio in anuncios:
            resumen_dia += Counter(anuncio.actos.keys())

        bormes_dia = Borme.objects.filter(date=self.borme.date).order_by('province')
        bormes_dia = list(bormes_dia)
        bormes_dia.remove(self.borme)
        bormes_dia.sort(key=lambda b: b.province)

        context.update({
            "bormes_dia": bormes_dia,
            "total_anuncios": self.borme.until_reg - self.borme.from_reg + 1,
            "resumen_dia": sorted(resumen_dia.items(), key=lambda t: t[0]),
        })

        return context


class BormeDateView(CacheMixin, TemplateView):
    template_name = 'borme/borme_fecha.html'

    def dispatch(self, request, *args, **kwargs):
        year, month, day = self.kwargs['date'].split('-')
        redirect_today = False

        try:
            self.date = datetime.date(int(year), int(month), int(day))
            if self.date > datetime.date.today():
                redirect_today = True
        except ValueError:
            redirect_today = True

        # Redirect to today's date when date is not valid
        if redirect_today:
            return redirect('borme-fecha', date=datetime.date.today().isoformat())

        return super(BormeDateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BormeDateView, self).get_context_data(**kwargs)

        # TODO: LocaleHTMLCalendar(firstweekday=0, locale=None)
        lb_calendar = LibreBormeCalendar().formatmonth(self.date)

        bormes = Borme.objects.filter(date=self.date).order_by('province')
        if len(bormes) > 0:
            from_reg = min([b.from_reg for b in bormes])
            until_reg = max([b.until_reg for b in bormes])
            anuncios = Anuncio.objects.filter(id_anuncio__gte=from_reg,
                                              id_anuncio__lte=until_reg,
                                              year=self.date.year)

            # FIXME: performance-killer? Guardar resultados en el modelo Borme
            from collections import Counter
            resumen_dia = Counter()
            for anuncio in anuncios:
                resumen_dia += Counter(anuncio.actos.keys())

            context['resumen_dia'] = sorted(resumen_dia.items(), key=lambda t: t[0])

        # TODO: Guardar la fecha en el anuncio?
        next_day = self.date + datetime.timedelta(days=1)
        prev_day = self.date - datetime.timedelta(days=1)

        context.update({
            "calendar": mark_safe(lb_calendar),
            "bormes": bormes,
            "date": self.date,
            "next_day": next_day.isoformat(),
            "prev_day": prev_day.isoformat(),
        })

        return context


class BormeProvinciaView(CacheMixin, TemplateView):
    template_name = 'borme/borme_provincia.html'

    def dispatch(self, request, *args, **kwargs):
        if 'year' not in self.kwargs:
            this_year = datetime.date.today().year
            return redirect('borme-provincia-fecha',
                            provincia=self.kwargs['provincia'],
                            year=this_year)

        return super(BormeProvinciaView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BormeProvinciaView, self).get_context_data(**kwargs)

        year = int(self.kwargs['year'])
        bormes = Borme.objects.filter(date__gte=datetime.date(year, 1, 1),
                                      date__lte=datetime.date(year, 12, 31),
                                      province=self.kwargs['provincia'])

        # TODO: LocaleHTMLCalendar(firstweekday=0, locale=None)
        lb_calendar = LibreBormeAvailableCalendar().formatyear(year, bormes)

        if len(bormes) > 0:
            # FIXME: No se puede hacer minimo y maximo. Hacer where in
            # from_reg = min([b.from_reg for b in bormes])
            # until_reg = max([b.until_reg for b in bormes])
            from_reg = bormes[0].from_reg
            until_reg = bormes[0].until_reg

            anuncios = Anuncio.objects.filter(id_anuncio__gte=from_reg,
                                              id_anuncio__lte=until_reg,
                                              year=year)

            # FIXME: performance-killer. Guardar resultados en el modelo Borme
            from collections import Counter
            resumen_dia = Counter()
            for anuncio in anuncios:
                resumen_dia += Counter(anuncio.actos.keys())

            context['resumen_dia'] = sorted(resumen_dia.items(), key=lambda t: t[0])

        context.update({
            "calendar": mark_safe(lb_calendar),
            "bormes": bormes,
        })

        return context


class CompanyView(CacheMixin, DetailView):
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

        context['anuncios'] = Anuncio.objects.filter(company=self.company).order_by('-year', '-id_anuncio')

        context['persons'] = []
        for cargo in self.company.todos_cargos_p:
            if cargo['name'] not in context['persons']:
                context['persons'].append(cargo['name'])

        context['companies'] = []
        for cargo in self.company.todos_cargos_c:
            if cargo['name'] not in context['companies']:
                context['companies'].append(cargo['name'])

        context.update({
            "companies": sorted(list(set(context['companies']))),
            "persons": sorted(list(set(context['persons']))),
            "activity": 'Activa' if self.company.is_active else 'Inactiva',
        })

        return context


class PersonView(CacheMixin, DetailView):
    model = Person
    context_object_name = 'person'

    def get_object(self):
        try:
            self.person = Person.objects.get(slug=self.kwargs['slug'])
            return self.person
        except Person.DoesNotExist:
            raise Http404('Person does not exist')


class CompanyProvinceListView(CacheMixin, ListView):
    # model = Company
    context_object_name = 'companies'
    # queryset = Book.objects.filter(province==X).order_by('-name')
