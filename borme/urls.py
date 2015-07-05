from django.conf.urls import patterns, include, url

from .views import *

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='borme-home'),
    url(r'^empresa/(?P<slug>[\w-]+)$', CompanyView.as_view(), name='borme-empresa'),
    url(r'^empresas/$', CompanyListView.as_view()),
    url(r'^persona/(?P<slug>[\w-]+)$', PersonView.as_view(), name='borme-persona'),
    url(r'^personas/$', PersonListView.as_view()),
    url(r'^busqueda/$', BusquedaView.as_view(), name='borme-search'),
)
