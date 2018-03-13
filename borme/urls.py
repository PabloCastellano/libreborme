from django.conf.urls import url, include

from . import views

from tastypie.api import Api
#from borme.api.resources import CompanyResource, PersonResource

v1_api = Api(api_name='v1')
#v1_api.register(CompanyResource())
#v1_api.register(PersonResource())


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='borme-home'),
    url(r'^anuncio/(?P<year>\d+)/(?P<id>\d+)/$', views.AnuncioView.as_view(), name='borme-anuncio'),
    url(r'^borme/(?P<cve>[\w-]+)/$', views.BormeView.as_view(), name='borme-borme'),
    url(r'^provincia/(?P<provincia>[\w -]+)/$', views.BormeProvinciaView.as_view(), name='borme-provincia'),
    url(r'^provincia/(?P<provincia>[\w -]+)/fecha/(?P<year>[\d-]+)/$', views.BormeProvinciaView.as_view(), name='borme-provincia-fecha'),
    url(r'^fecha/(?P<date>[\d-]+)/$', views.BormeDateView.as_view(), name='borme-fecha'),
    url(r'^empresa/(?P<slug>[\w-]+)/$', views.CompanyView.as_view(), name='borme-empresa'),
    url(r'^empresa/(?P<slug>[\w-]+)/cargos_actual.csv$', views.generate_company_csv_cargos_actual, name='borme-empresa-csv-actual'),
    url(r'^empresa/(?P<slug>[\w-]+)/cargos_historial.csv$', views.generate_company_csv_cargos_historial, name='borme-empresa-csv-historial'),
    url(r'^persona/(?P<slug>[\w-]+)/$', views.PersonView.as_view(), name='borme-persona'),
    url(r'^persona/(?P<slug>[\w-]+)/cargos_actual.csv$', views.generate_person_csv_cargos_actual, name='borme-persona-csv-actual'),
    url(r'^persona/(?P<slug>[\w-]+)/cargos_historial.csv$', views.generate_person_csv_cargos_historial, name='borme-persona-csv-historial'),
    #url(r'^busqueda/$', BusquedaView.as_view(), name='borme-busqueda'),
    url(r'^api/', include(v1_api.urls)),
    #url(r'^search/', views.LBSearchView(), name='borme-search'),

    url(r'^ajax/empresa/(?P<slug>[\w-]+)/more', views.ajax_empresa_more, name='borme-ajax-empresa'),
]
