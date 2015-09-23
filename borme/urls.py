from django.conf.urls import patterns, url

from .views import AnuncioView, CompanyView, PersonView, HomeView, PersonListView, CompanyListView, BusquedaView, BormeView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='borme-home'),
    url(r'^anuncio/(?P<id>\d+)$', AnuncioView.as_view(), name='borme-anuncio'),
    url(r'^borme/(?P<cve>[\w-]+)$', BormeView.as_view(), name='borme-borme'),
    url(r'^empresa/(?P<slug>[\w-]+)$', CompanyView.as_view(), name='borme-empresa'),
    url(r'^empresas/$', CompanyListView.as_view(), name='borme-empresas-list'),
    url(r'^persona/(?P<slug>[\w-]+)$', PersonView.as_view(), name='borme-persona'),
    url(r'^personas/$', PersonListView.as_view(), name='borme-personas-list'),
    url(r'^busqueda/$', BusquedaView.as_view(), name='borme-search'),
)
