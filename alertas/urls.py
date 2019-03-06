from django.urls import path

from . import views

urlpatterns = [
    path('', views.MyAccountView.as_view(), name='dashboard-index'),
    path('profile/', views.ProfileView.as_view(), name='alertas-profile'),
    path('events/', views.AlertaEventsView.as_view(), name='alertas-events'),
    path('stripe/', views.StripeView.as_view(), name='alertas-stripe'),
    path('service/follow/', views.ServiceFollowView.as_view(), name='service-follow'),
    path('service/api/', views.ServiceAPIView.as_view(), name='service-api'),
    path('service/subscriptions/cancel/<int:pk>/', views.cancel_subscription, name='cancel-subscription'),
    path('service/subscriptions/edit/<int:pk>/', views.SubscriptionUpdate.as_view(), name='update-subscription'),
    path('service/subscriptions/', views.ServiceSubscriptionView.as_view(), name='service-subscription'),
    path('billing/', views.BillingView.as_view(), name='alertas-billing'),
    path('payment/', views.PaymentView.as_view(), name='alertas-payment'),
    path('payment/new_card/', views.add_card, name='alertas-payment-add-card'),
    path('payment/checkout/', views.checkout_page, name="checkout_page"),
    path('payment/checkout2/', views.checkout_existing_card, name="checkout_existing"),
    path('new/acto/', views.alerta_acto_create, name='alertas-new-acto'),
    path('history/', views.DashboardHistoryView.as_view(), name='alertas-history'),
    path('ayuda/', views.DashboardSupportView.as_view(), name='alertas-ayuda'),
    path('cart/', views.CartView.as_view(), name='alertas-cart'),
    path('cart/buy/', views.add_to_cart_new, name='buy-product-new'),
    path('cart/removecart/', views.remove_cart, name='alertas-removecart'),
    path('settings/update/billing/', views.settings_update_billing, name='alertas-settings-billing'),
    path('history/download/<id>/', views.download_alerta_history_csv, name='alerta-history-download'),
    path('termsofservice/', views.TermsOfServiceView.as_view(), name='alertas-tos'),
#    url(r'^(?P<id>\d+)/$', views.alertas_view, name='alertas-detail'),

    # AJAX
    path('suggest_company/', views.suggest_company, name='suggest_company'),
    path('suggest_person/', views.suggest_person, name='suggest_person'),
    path('remove_card/', views.remove_card, name='remove_card'),

    path('follow/', views.ajax_follow, name='borme-ajax-follow'),

    # UNUSED?
    path('cart/buy/<product>/', views.add_to_cart, name='buy-product'),
    path('<id>/', views.AlertaDetailView.as_view(), name='alertas-detail'),
]
