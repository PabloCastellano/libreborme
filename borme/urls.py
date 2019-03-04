from django.urls import include, path

from . import views

from tastypie.api import Api
from borme.api.resources import CompanyResource, PersonResource

v1_api = Api(api_name='v1')
v1_api.register(CompanyResource())
v1_api.register(PersonResource())


urlpatterns = [
    path('', views.HomeView.as_view(), name='borme-home'),
    path('anuncio/<int:year>/<int:id>/', views.AnuncioView.as_view(), name='borme-anuncio'),
    path('borme/<cve>/', views.BormeView.as_view(), name='borme-borme'),
    path('provincia/<provincia>/', views.BormeProvinciaView.as_view(), name='borme-provincia'),
    path('provincia/<provincia>/fecha/<int:year>/', views.BormeProvinciaView.as_view(), name='borme-provincia-fecha'),
    path('fecha/<date>/', views.BormeDateView.as_view(), name='borme-fecha'),
    path('empresa/<slug:slug>/', views.CompanyView.as_view(), name='borme-empresa'),
    path('empresa/<slug:slug>/cargos_actual.csv', views.generate_company_csv_cargos_actual, name='borme-empresa-csv-actual'),
    path('empresa/<slug:slug>/cargos_historial.csv', views.generate_company_csv_cargos_historial, name='borme-empresa-csv-historial'),
    path('persona/<slug:slug>/', views.PersonView.as_view(), name='borme-persona'),
    path('persona/<slug:slug>/cargos_actual.csv', views.generate_person_csv_cargos_actual, name='borme-persona-csv-actual'),
    path('persona/<slug:slug>/cargos_historial.csv', views.generate_person_csv_cargos_historial, name='borme-persona-csv-historial'),
    path('busqueda/', views.BusquedaView.as_view(), name='borme-search'),
    # path(r'^search/', views.LBSearchView.as_view(), name='borme-search'),

    # Tastypie API
    path('api/', include(v1_api.urls)),

    path('ajax/empresa/<slug:slug>/more', views.ajax_empresa_more, name='borme-ajax-empresa'),
]
