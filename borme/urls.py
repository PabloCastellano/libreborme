from django.conf.urls import patterns, url, include

from .views import AnuncioView, CompanyView, PersonView, HomeView, PersonListView, CompanyListView, BusquedaView,\
                    BormeView, BormeProvinciaView, BormeDateView

from tastypie.api import Api
from borme.api.resources import CompanyResource, PersonResource

v1_api = Api(api_name='v1')
v1_api.register(CompanyResource())
v1_api.register(PersonResource())


urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='borme-home'),
    url(r'^anuncio/(?P<year>\d+)/(?P<id>\d+)$', AnuncioView.as_view(), name='borme-anuncio'),
    url(r'^borme/(?P<cve>[\w-]+)$', BormeView.as_view(), name='borme-borme'),
    url(r'^provincia/(?P<provincia>[\w -]+)$', BormeProvinciaView.as_view(), name='borme-provincia'),
    url(r'^fecha/(?P<date>[\d-]+)$', BormeDateView.as_view(), name='borme-fecha'),
    url(r'^empresa/(?P<slug>[\w-]+)$', CompanyView.as_view(), name='borme-empresa'),
    url(r'^empresas/$', CompanyListView.as_view(), name='borme-empresas-list'),
    url(r'^persona/(?P<slug>[\w-]+)$', PersonView.as_view(), name='borme-persona'),
    url(r'^personas/$', PersonListView.as_view(), name='borme-personas-list'),
    url(r'^busqueda/$', BusquedaView.as_view(), name='borme-search'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^search/', include('haystack.urls')),
)
