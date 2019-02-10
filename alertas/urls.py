from django.urls import path

from . import views

urlpatterns = [
    path('alertas/', views.MyAccountView.as_view(), name='dashboard-index'),
    path('alertas/profile/', views.ProfileView.as_view(), name='alertas-profile'),
    path('alertas/events/', views.AlertaEventsView.as_view(), name='alertas-events'),
    path('alertas/stripe/', views.StripeView.as_view(), name='alertas-stripe'),
    path('alertas/service/follow/', views.ServiceAlertaView.as_view(), name='service-follow'),
    path('alertas/service/api/', views.ServiceAPIView.as_view(), name='service-api'),
    path('alertas/service/subscriptions/', views.ServiceSubscriptionView.as_view(), name='service-subscription'),
    path('alertas/billing/', views.BillingView.as_view(), name='alertas-billing'),
    path('alertas/payment/', views.PaymentView.as_view(), name='alertas-payment'),
    path('alertas/payment/new_card/', views.add_card, name='alertas-payment-add-card'),
    path('alertas/payment/checkout/', views.checkout_page, name="checkout_page"),
    path('alertas/payment/checkout2/', views.checkout_existing_card, name="checkout_existing"),
    path('alertas/new/acto/', views.alerta_acto_create, name='alertas-new-acto'),
    path('alertas/history/', views.DashboardHistoryView.as_view(), name='alertas-history'),
    path('alertas/remove/acto/<id>/', views.alerta_remove_acto, name='alerta-remove-acto'),
    path('alertas/ayuda/', views.DashboardSupportView.as_view(), name='alertas-ayuda'),
    path('alertas/cart/', views.CartView.as_view(), name='alertas-cart'),
    path('alertas/cart/buy/', views.add_to_cart_new, name='buy-product-new'),
    path('alertas/cart/buy/<product>/', views.add_to_cart, name='buy-product'),
    path('alertas/cart/removecart/', views.remove_cart, name='alertas-removecart'),
    path('alertas/settings/update/billing/', views.settings_update_billing, name='alertas-settings-billing'),
    path('alertas/history/download/<id>/', views.download_alerta_history_csv, name='alerta-history-download'),
    path('alertas/termsofservice/', views.TermsOfServiceView.as_view(), name='alertas-tos'),
    path('alertas/<id>/', views.AlertaDetailView.as_view(), name='alertas-detail'),
#    url(r'^(?P<id>\d+)/$', views.alertas_view, name='alertas-detail'),

    # AJAX
    path('alertas/suggest_company/', views.suggest_company, name='suggest_company'),
    path('alertas/suggest_person/', views.suggest_person, name='suggest_person'),
    path('alertas/remove_card/', views.remove_card, name='remove_card'),
    path('alertas/set_default_card/', views.set_default_card, name='set_default_card'),

    path('ajax/follow/', views.ajax_follow, name='borme-ajax-follow'),
]
