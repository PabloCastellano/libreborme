from django.conf.urls import patterns, url, include

from .views import AnuncioView, CompanyView, PersonView, HomeView, BusquedaView,\
                    BormeView, BormeProvinciaView, BormeDateView, LBSearchView, generate_company_csv_cargos_actual, generate_company_csv_cargos_historial,\
                    generate_person_csv_cargos_actual, generate_person_csv_cargos_historial

from tastypie.api import Api
from borme.api.resources import CompanyResource, PersonResource

v1_api = Api(api_name='v1')
v1_api.register(CompanyResource())
v1_api.register(PersonResource())


urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='borme-home'),
    url(r'^anuncio/(?P<year>\d+)/(?P<id>\d+)/$', AnuncioView.as_view(), name='borme-anuncio'),
    url(r'^borme/(?P<cve>[\w-]+)/$', BormeView.as_view(), name='borme-borme'),
    url(r'^provincia/(?P<provincia>[\w -]+)/$', BormeProvinciaView.as_view(), name='borme-provincia'),
    url(r'^provincia/(?P<provincia>[\w -]+)/fecha/(?P<year>[\d-]+)/$', BormeProvinciaView.as_view(), name='borme-provincia-fecha'),
    url(r'^fecha/(?P<date>[\d-]+)/$', BormeDateView.as_view(), name='borme-fecha'),
    url(r'^empresa/(?P<slug>[\w-]+)/$', CompanyView.as_view(), name='borme-empresa'),
    url(r'^empresa/(?P<slug>[\w-]+)/cargos_actual.csv$', generate_company_csv_cargos_actual, name='borme-empresa-csv-actual'),
    url(r'^empresa/(?P<slug>[\w-]+)/cargos_historial.csv$', generate_company_csv_cargos_historial, name='borme-empresa-csv-historial'),
    url(r'^persona/(?P<slug>[\w-]+)/$', PersonView.as_view(), name='borme-persona'),
    url(r'^persona/(?P<slug>[\w-]+)/cargos_actual.csv$', generate_person_csv_cargos_actual, name='borme-persona-csv-actual'),
    url(r'^persona/(?P<slug>[\w-]+)/cargos_historial.csv$', generate_person_csv_cargos_historial, name='borme-persona-csv-historial'),
    #url(r'^busqueda/$', BusquedaView.as_view(), name='borme-busqueda'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^search/', LBSearchView(), name='borme-search'),
)
