from django.conf.urls import patterns, url

from .views import CompanyView, PersonView, HomeView, PersonListView, CompanyListView, BusquedaView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='borme-home'),
    url(r'^empresa/(?P<slug>[\w-]+)$', CompanyView.as_view(), name='borme-empresa'),
    url(r'^empresas/$', CompanyListView.as_view(), name='borme-empresas-list'),
    url(r'^persona/(?P<slug>[\w-]+)$', PersonView.as_view(), name='borme-persona'),
    url(r'^personas/$', PersonListView.as_view(), name='borme-personas-list'),
    url(r'^busqueda/$', BusquedaView.as_view(), name='borme-search'),
)
