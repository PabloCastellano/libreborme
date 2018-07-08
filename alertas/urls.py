from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^alertas/$', views.DashboardIndexView.as_view(), name='dashboard-index'),
    url(r'^alertas/events/$', views.AlertaEventsView.as_view(), name='alertas-events'),
    url(r'^alertas/list/$', views.AlertaListView.as_view(), name='alertas-list'),
    url(r'^alertas/billing/$', views.BillingView.as_view(), name='alertas-billing'),
    url(r'^alertas/billing/(?P<id>\d+)/$', views.BillingDetailView.as_view(), name='alertas-invoice-view'),
    url(r'^alertas/new/acto/$', views.alerta_acto_create, name='alertas-new-acto'),
    url(r'^alertas/new/person/$', views.alerta_person_create, name='alertas-new-person'),
    url(r'^alertas/new/company/$', views.alerta_company_create, name='alertas-new-company'),
    url(r'^alertas/(?P<id>\d+)/$', views.AlertaDetailView.as_view(), name='alertas-detail'),
    url(r'^alertas/remove/acto/(?P<id>\d+)/$', views.alerta_remove_acto, name='alerta-remove-acto'),
    url(r'^alertas/remove/person/(?P<id>\d+)/$', views.alerta_remove_person, name='alerta-remove-person'),
    url(r'^alertas/remove/company/(?P<id>\d+)/$', views.alerta_remove_company, name='alerta-remove-company'),
    url(r'^alertas/ayuda/$', views.DashboardSupportView.as_view(), name='alertas-ayuda'),
    url(r'^alertas/settings/$', views.DashboardSettingsView.as_view(), name='alertas-settings'),
    url(r'^alertas/settings/update/personal/$', views.settings_update_personal, name='alertas-settings-personal'),
    url(r'^alertas/settings/update/notifications/$', views.settings_update_notifications, name='alertas-settings-notifications'),
    url(r'^alertas/history/$', views.DashboardHistoryView.as_view(), name='dashboard-history'),

    url(r'^alertas/history/download/(?P<id>\d+)$', views.download_alerta_history_csv, name='alerta-history-download'),

#    url(r'^(?P<id>\d+)/$', views.alertas_view, name='alertas-detail'),

    # AJAX
    url(r'^alertas/suggest_company/$', views.suggest_company, name='suggest_company'),
    url(r'^alertas/suggest_person/$', views.suggest_person, name='suggest_person'),
]
