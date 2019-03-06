from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy

import datetime
import json
import stripe

from collections import OrderedDict

from djstripe.models import Customer, Event, Plan, Product, Subscription

import alertas.subscriptions
from borme.models import Company, Person
from borme.utils.strings import empresa_slug
from libreborme.models import Profile
from libreborme import utils

from . import forms
from .models import (
    UserSubscription, AlertaHistory,
    Follower, EVENTOS_DICT, PROVINCIAS_DICT, PROVINCIAS_DICT_ALL
)
from .mixin import CustomerMixin, StripeMixin
from .utils import get_alertas_config


MAX_RESULTS_AJAX = 15
User = get_user_model()

# http://calculadoraigic.onlinegratis.tv/
# IVA: 21%
# IGIC (Canarias): 6,5%
# IPSI (Ceuta): 8%
# IPSI (Melilla): 4%
TAXES = {
    'IVA': 21.0,
    'IGIC': 6.5,
    'IPSI-Ceuta': 8.0,
    'IPSI-Melilla': 4.0
}


class SubscriptionUpdate(UpdateView):
    """ Once a subscription is created, the user is allowed to change some only some fields """
    model = UserSubscription
    # fields = ["send_email"]
    form_class = forms.SubscriptionUpdateForm
    success_url = reverse_lazy('service-subscription')
    template_name_suffix = '_update_form'



# TODO: Pagination
@method_decorator(login_required, name='dispatch')
class MyAccountView(CustomerMixin, TemplateView):
    template_name = 'alertas/myaccount.html'

    def get_context_data(self, **kwargs):
        context = super(MyAccountView, self).get_context_data(**kwargs)

        context['active'] = 'dashboard'

        aconfig = get_alertas_config()
        context['free_follows'] = aconfig['max_alertas_follower_free']

        if context['customer']:
            context['subscriptions'] = context["customer"].active_subscriptions.order_by('-start')

        """:
            context['ip'] = self.request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            context['ip'] = self.request.META['REMOTE_ADDR']
        """
        return context


@method_decorator(login_required, name='dispatch')
class ProfileView(CustomerMixin, TemplateView):
    template_name = 'alertas/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        # Prepare forms
        user_profile = self.request.user.profile

        # context['form_notification'] = forms.NotificationSettingsForm(initial={
        #     'notification_method': user_profile.notification_method,
        #     'notification_email': user_profile.notification_email,
        #     'notification_url': user_profile.notification_url})

        context['form_personal'] = forms.PersonalDataForm(initial={
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'email': self.request.user.email,
            'home_phone': user_profile.home_phone,
            'date_joined': self.request.user.date_joined.date()})

        context['form_profile'] = forms.ProfileDataForm(initial={
            'home_phone': user_profile.home_phone,
            'razon_social': user_profile.razon_social,
            'cif_nif': user_profile.cif_nif,
            'address': user_profile.address,
            'post_code': user_profile.post_code,
            'poblacion': user_profile.poblacion,
            'provincia': user_profile.provincia,
            'country': user_profile.country})

        context['form_newsletter'] = forms.NewsletterForm(initial={
            'newsletter_promotions': user_profile.newsletter_promotions,
            'newsletter_features': user_profile.newsletter_features})

        context['active'] = 'profile'

        """
        try:
            context['ip'] = self.request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            context['ip'] = self.request.META['REMOTE_ADDR']
        """
        return context


@method_decorator(login_required, name='dispatch')
class DashboardSupportView(TemplateView):
    template_name = 'alertas/dashboard_support.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSupportView, self).get_context_data(**kwargs)
        context['active'] = 'ayuda'
        return context


@method_decorator(login_required, name='dispatch')
class TermsOfServiceView(TemplateView):
    template_name = 'alertas/terms_of_service.html'

    def get_context_data(self, **kwargs):
        context = super(TermsOfServiceView, self).get_context_data(**kwargs)
        context['active'] = 'tos'

        aconfig = get_alertas_config()
        context['free_follows'] = aconfig['max_alertas_follower_free']
        context["service_subscription_trial_day"] = aconfig["service_subscription_trial_day"]
        return context


# TODO: Pagination
@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class DashboardHistoryView(TemplateView):
    template_name = 'alertas/dashboard_history.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardHistoryView, self).get_context_data(**kwargs)
        context['alertas'] = AlertaHistory.objects.filter(user=self.request.user)
        context['active'] = 'history'
        return context


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class StripeView(TemplateView):
    template_name = 'alertas/stripe.html'

    def get_context_data(self, **kwargs):
        context = super(StripeView, self).get_context_data(**kwargs)
        context['customers'] = Customer.objects.all().order_by('created')
        context['plans'] = Plan.objects.all().order_by('created')
        context['products'] = Product.objects.all().order_by('created')
        context['subscriptions'] = Subscription.objects.all().order_by('created')
        context['active'] = 'stripe'
        return context


@method_decorator(login_required, name='dispatch')
class PaymentView(StripeMixin, CustomerMixin, TemplateView):
    template_name = 'alertas/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['active'] = 'payment'
        if context["customer"].has_valid_source():
            context['card'] = context["customer"].default_source.resolve()

        # context["form"] = forms.CreditCardForm()

        return context


@method_decorator(login_required, name='dispatch')
class BillingView(CustomerMixin, TemplateView):
    template_name = 'alertas/billing.html'

    def get_context_data(self, **kwargs):
        context = super(BillingView, self).get_context_data(**kwargs)
        context['active'] = 'billing'

        if context['customer']:
            context['invoices'] = context["customer"].invoices.all()

            # TODO: esta llamada relentiza bastante la carga
            try:
                upcoming_invoice = context['customer'].upcoming_invoice()
            except stripe.error.InvalidRequestError:
                upcoming_invoice = None
            context["upcoming_invoice"] = upcoming_invoice

        return context


def cancel_subscription(request, pk):
    """ Cancel djstripe.models.Subscription

    :param pk: UserSubscription primary key
    :type pk: int

    Once it is cancelled:
    subscription.cancel_at_period_end changes from False to True
    subscription.canceled_at will be datetime.datetime.now()
    subscription.status will be active until subscription.current_period_end
    subscription.start is datetime.datetime.now(), is it a bug?? <https://github.com/dj-stripe/dj-stripe/issues/852>
    """

    try:
        subscription = UserSubscription.objects.get(
            pk=pk,
            user=request.user,
        )
    except UserSubscription.DoesNotExist:
        return redirect(reverse('dashboard-index'))

    if request.method == "GET":
        ctx = dict(object=subscription)
        return render(request,
                      template_name="alertas/usersubscription_cancel.html",
                      context=ctx)
    elif request.method == "POST":

        if subscription:
            subscription = subscription.stripe_subscription.cancel()
            messages.add_message(request, messages.SUCCESS,
                                 'Se ha cancelado la suscripción')
    return redirect(reverse('dashboard-index'))


@method_decorator(login_required, name='dispatch')
class AlertaDetailView(DetailView):
    model = UserSubscription
    context_object_name = 'alerta'

    def get_object(self):
        self.alerta = UserSubscription.objects.get(pk=self.kwargs['id'])
        return self.alerta


# TODO: Use |dictsort in template instead
@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AlertaEventsView(TemplateView):
    template_name = "alertas/events_list.html"

    def get_context_data(self, **kwargs):
        context = super(AlertaEventsView, self).get_context_data(**kwargs)
        context['active'] = 'events'

        events_by_date = {}
        for e in Event.objects.all().order_by('-created'):
            e.data_json = json.dumps(e.data)
            e.metadata_json = json.dumps(e.metadata)
            date = e.created.date()
            events_by_date.setdefault(date, [])
            events_by_date[date].append(e)
        context['events_by_date'] = OrderedDict(sorted(events_by_date.items(), reverse=True))
        context["events_list"] = sorted(events_by_date.keys(), reverse=True)
        return context


@method_decorator(login_required, name='dispatch')
class ServiceSubscriptionView(CustomerMixin, StripeMixin, TemplateView):
    template_name = "alertas/service_subscription.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceSubscriptionView, self).get_context_data(**kwargs)
        context['active'] = 'subscription'

        # TODO: Si tiene suscripciones pagadas y no ha definido qué quiere, mostrarle form
        # TODO: Solo una suscripción de prueba

        if context['customer']:
            context["subscriptions"] = context["customer"].active_subscriptions.filter(
                    plan__nickname__in=(settings.SUBSCRIPTION_MONTH_ONE_PLAN, settings.SUBSCRIPTION_MONTH_FULL_PLAN, settings.SUBSCRIPTION_YEAR_PLAN),
            )

        context['alertas_a'] = UserSubscription.objects.filter(user=self.request.user, is_enabled=True)
        context['current'] = context['alertas_a'].count()
        context['form_alertas'] = forms.SubscriptionModelForm(initial={'send_email': 'daily'})

        if 'subscriptions' in context:
            context["total"] = len(context["subscriptions"])
        else:
            context["total"] = 0

        context['form_subscription_buy'] = forms.SubscriptionPlusModelForm(
                initial={'evento': 'adm', 'send_email': 'daily', 'provincia': 1},
                auto_id="id_buy_%s",
        )
        context["remaining"] = context["total"] - context["current"]

        aconfig = get_alertas_config()
        context["service_subscription_trial_day"] = aconfig["service_subscription_trial_day"]
        plan_month_one = Plan.objects.get(nickname=settings.SUBSCRIPTION_MONTH_ONE_PLAN)
        context["plan_month_one"] = plan_month_one
        plan_month_full = Plan.objects.get(nickname=settings.SUBSCRIPTION_MONTH_FULL_PLAN)
        context["plan_month_full"] = plan_month_full

        return context


@method_decorator(login_required, name='dispatch')
class ServiceFollowView(CustomerMixin, StripeMixin, TemplateView):
    template_name = "alertas/service_follow.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceFollowView, self).get_context_data(**kwargs)
        context['active'] = 'alertas'

        context['alertas_f'] = Follower.objects.filter(user=self.request.user)
        context['count_f'] = context['alertas_f'].count()

        alertas_config = get_alertas_config()

        context['free_follows'] = int(alertas_config['max_alertas_follower_free'])
        context['remaining_follows'] = int(context['free_follows']) - context['count_f']
        context['current_follows'] = context['free_follows'] - context['remaining_follows']
        context['max_alertas_follower_free'] = int(alertas_config['max_alertas_follower_free'])
        context['max_alertas_follower_paid'] = int(alertas_config['max_alertas_follower_paid'])

        context["followers"] = Follower.objects.filter(user=self.request.user)
        context['form_f'] = forms.FollowerForm()

        # TODO: self.request.user.djstripe_customers.get().subscriptions.filter()
        if context["customer"]:
            context["subscriptions"] = context["customer"].active_subscriptions.filter(plan__nickname__in=(settings.ALERTS_YEAR_PLAN))

        context["plan_year"] = Plan.objects.get(nickname=settings.ALERTS_YEAR_PLAN)
        plan_follow_year = Plan.objects.get(nickname=settings.ALERTS_YEAR_PLAN)
        context["plan_follow_month_price"] = plan_follow_year.amount / 12
        return context


@method_decorator(login_required, name='dispatch')
class CartView(CustomerMixin, StripeMixin, TemplateView):
    template_name = "alertas/cart.html"

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)

        profile = self.request.user.profile

        if profile.is_complete() and 'cart' in self.request.session:
            taxname = 'IVA'  # TODO
            plan_name = self.request.session['cart']['name']
            price = self.request.session['cart']['price']

            # session
            context["evento"] = EVENTOS_DICT[self.request.session["cart"]["evento"]]
            context["provincia"] = PROVINCIAS_DICT_ALL[self.request.session["cart"]["provincia"]]

            plan = Plan.objects.get(nickname=plan_name)
            if context["provincia"] == "all":
                provincia_text = "todas las provincias"
            else:
                provincia_text = "una provincia"
            if plan.interval == "month":
                pago_text = "Pago mensual"
            elif plan.interval == "year":
                pago_text = "Pago anual"
            product_text = "<strong>{0} ({1})</strong>\n{2}, {3}".format(plan.product.name, pago_text, context["evento"], provincia_text)
            context['product'] = {'name': product_text, 'price': price}
            context['tax_amount'] = round(price * (TAXES[taxname] / 100), 2)
            context['total_with_tax'] = round(price * (1 + TAXES[taxname] / 100), 2)
            context['tax_percentage'] = TAXES[taxname]

            if context["customer"]:
                cards = context['customer'].sources.order_by('-exp_year', '-exp_month')
            else:
                cards = None
            context["cards"] = cards

            if plan_name in ('subscription_month_one', 'subscription_month_full', 'subscription_year') and not profile.has_tried_subscriptions:
                context['show_subscription_trial'] = True

            aconfig = get_alertas_config()
            context['service_subscription_trial_day'] = aconfig['service_subscription_trial_day']
            context["has_tried_subscriptions"] = profile.has_tried_subscriptions

            # Prepare forms
            # TODO: Falta población
            user_profile = self.request.user.profile
            context['form_payment'] = forms.PaymentForm(
                initial={
                    'name': user_profile.razon_social,
                    'address': user_profile.address,
                    'city': user_profile.poblacion,
                    'state': user_profile.provincia,
                    'zip': user_profile.post_code,
                    'country': user_profile.country,
                    'nif': user_profile.cif_nif,
                },
                auto_id="example2-%s",
            )

            # TODO: test when Customer doesn't exist
            # TODO: No solo plan.nickname sino las del mismo tipo
            context["active_subscriptions"] = context["customer"].active_subscriptions.filter(plan__nickname=plan.nickname).count()

        context['active'] = 'cart'
        return context


@method_decorator(login_required, name='dispatch')
class ServiceAPIView(CustomerMixin, TemplateView):
    template_name = "alertas/service_api.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceAPIView, self).get_context_data(**kwargs)
        context['active'] = 'api'

        context["plan_api_month"] = Plan.objects.get(nickname=settings.API_MONTH_PLAN)

        if context["customer"]:
            context["subscriptions"] = context["customer"].active_subscriptions.filter(
                    plan__nickname__in=(settings.API_MONTH_PLAN, settings.API_YEAR_PLAN))

        aconfig = get_alertas_config()
        context['service_api_free_req_day'] = aconfig['service_api_free_req_day']
        context['service_api_advanced_req_day'] = aconfig['service_api_advanced_req_day']

        context["api_enabled"] = self.request.user.profile.has_api_enabled
        return context


@login_required
def alerta_person_create(request):
    if request.method == 'POST':
        form = forms.AlertaPersonModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('service-follow'))


@login_required
def alerta_acto_create(request):
    """ Comprueba que el form es válido y que el usuario tiene suscripciones suficientes """
    if request.method == 'POST':
        form = forms.SubscriptionModelForm(request.POST)
        if form.is_valid():

            # customer = Customer.objects.get(subscriber=request.user)
            customer = request.user.djstripe_customers.get()
            # TODO: hacer un metodo en Manager: user.has_remaining_subscriptions o algo asi
            subscriptions = customer.active_subscriptions.filter(plan__nickname__in=(settings.SUBSCRIPTION_MONTH_ONE_PLAN, settings.SUBSCRIPTION_MONTH_FULL_PLAN, settings.SUBSCRIPTION_YEAR_PLAN))
            alertas_a = UserSubscription.objects.filter(user=request.user)
            remaining = len(subscriptions) - alertas_a.count()

            if remaining > 0:
                alerta = form.save(commit=False)
                alerta.user = request.user
                alerta.save()
    return redirect(reverse('service-subscription'))


@login_required
def add_to_cart(request, product):
    # TODO: avisar si ya tiene la suscripción, aunque puede
    # querer pagar dos veces para tener más followers o suscripciones
    try:
        plan = Plan.objects.get(nickname=product)
    except Plan.DoesNotExist:
        return redirect(reverse('dashboard-index'))

    # TODO: test when Customer doesn't exist
    customer = Customer.objects.get(subscriber=request.user)
    profile = request.user.profile
    # TODO: filter status=active?
    existing_subscriptions = Subscription.objects.filter(
            plan__nickname=product, customer=customer)

    if existing_subscriptions:
        messages.add_message(request, messages.WARNING,
                             'Ya tienes una suscripción activa')

    price = float(plan.amount)  # Decimal
    product = {'name': product, 'price': price}
    request.session['cart'] = product
    return redirect(reverse('alertas-cart'))


@login_required
def add_to_cart_new(request):
    if request.method == 'POST':
        form = forms.SubscriptionPlusModelForm(request.POST)
        if form.is_valid():
            product = request.POST['product']
            try:
                plan = Plan.objects.get(nickname=product)
            except Plan.DoesNotExist:
                return redirect(reverse('dashboard-index'))

            price = float(plan.amount)  # Decimal
            cart = {
                'name': product,
                'price': price,
                'provincia': form.cleaned_data['provincia'],
                'evento': form.cleaned_data['evento'],
            }
            request.session['cart'] = cart
    return redirect(reverse('alertas-cart'))


@login_required
def settings_update_billing(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        profile = user.profile

        profile_was_complete = user.profile.is_complete()

        # Process forms
        # TODO: Update business_vat_id in Customer model

        form = forms.PersonalDataForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            # Do not update the following fields:
            # email - use another procedure
            # date_joined
            user.save()
            profile.home_phone = form.cleaned_data['home_phone']
        form = forms.NewsletterForm(request.POST)
        if form.is_valid():
            profile.newsletter_promotions = form.cleaned_data['newsletter_promotions']
            profile.newsletter_features = form.cleaned_data['newsletter_features']
        form = forms.ProfileDataForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

        # dj-stripe does not allow you to sync Customer saved attributes
        # https://github.com/dj-stripe/dj-stripe/issues/753
        user.refresh_from_db()
        if user.profile.is_complete():
            # TODO: Do only if some field has changed
            customer, _ = Customer.get_or_create(subscriber=request.user)
            customer_sdk = stripe.Customer.retrieve(customer.id)
            customer_sdk.business_vat_id = user.profile.cif_nif
            customer_sdk.description = "{} ({}) / {}".format(user.get_full_name(), user.profile.account_type, user.profile.provincia)
            customer_sdk.shipping = {
                'address': {
                    'line1': user.profile.address,
                    'line2': '',
                    'postal_code': user.profile.post_code,
                    'city': user.profile.poblacion,
                    'state': user.profile.provincia,
                    'country': user.profile.country,
                },
                'name': user.profile.razon_social,
                'phone': user.profile.home_phone,
            }
            customer_sdk.save()
            if profile_was_complete:
                messages.add_message(request, messages.SUCCESS,
                                     'Se han guardado los cambios')
            else:
                messages.add_message(request, messages.SUCCESS,
                                     'Tu perfil está completo ahora')
        else:
            messages.add_message(request, messages.SUCCESS,
                             'Se han guardado los cambios')
    return redirect(reverse('alertas-profile'))


@login_required
def add_card(request):

    if request.method == 'POST':
        customer, created = Customer.get_or_create(subscriber=request.user)
        user_input = utils.stripe_parse_input(request)
        customer.add_card(source=user_input["token"])
        customer.save()
        messages.add_message(request, messages.SUCCESS,
                             'Tarjeta añadida correctamente')

    return redirect(reverse('alertas-payment'))


@login_required
def checkout_page(request):
    """Checkout

    Llegados a este punto, la compra ya está aceptada y tenemos el token,
    solo nos falta crear la suscripción
    """
    # TODO: make params
    # TODO: Promotion code
    # TODO: description en el payment
    # TODO: Guardar si ya ha hecho el periodo de prueba
    # Para acelerar la carga, se puede dejar corriendo subscribe() que automáticamente luego
    if request.method == "POST":
        nickname = request.session['cart']['name']
        plan = Plan.objects.get(nickname=nickname)
        # TODO: Log user created
        customer, _ = Customer.get_or_create(subscriber=request.user)

        taxname = 'IVA'  # TODO: tax per province - limited to Spain
        tax_percent = TAXES[taxname]

        token = request.POST.get("stripeToken")
        save_card = 'save-card' in request.POST

        # TODO: default source
        use_default_source = 'use-default-source' in request.POST

        try:

            # if customer.has_valid_source():
            #     subscription = customer.subscribe(plan)
            # else:

            # TODO: Save card
            card = customer.add_card(token, set_default=save_card)

            # Pending issues:
            # trial_from_plan: https://github.com/dj-stripe/dj-stripe/issues/809
            # billing_cycle_anchor: https://github.com/dj-stripe/dj-stripe/issues/814
            if request.user.profile.has_tried_subscriptions:
                trial_end = None
            else:
                trial_period_days = plan.trial_period_days
                trial_end = datetime.datetime.now() + datetime.timedelta(days=trial_period_days)

            description = "Suscripcion a {evento} de la provincia {provincia}".format(**request.session['cart'])
            metadata = {
                "description": description,
                "evento": request.session['cart']["evento"],
                "provincia": request.session['cart']["provincia"]
            }

            # coupon=None, quantity=1
            billing_cycle_anchor = utils.date_next_first(timestamp=True)

            subscription = customer.subscribe(plan, trial_end=trial_end,
                                              tax_percent=tax_percent,
                                              metadata=metadata,
                                              billing_cycle_anchor=billing_cycle_anchor)

            if not save_card:
                card.remove()
            # TODO: fix new invoice
            # new_invoice = create_new_invoice(request, customer, subscription, plan, user_input)

        except stripe.error.CardError as ce:
            # :?
            return False, ce

        else:
            # TODO
            # new_invoice.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Pago realizado con éxito. Tenga en cuenta que la activación del servicio puede tardar unos minutos.')

            if nickname in (settings.SUBSCRIPTION_MONTH_ONE_PLAN, settings.SUBSCRIPTION_MONTH_FULL_PLAN, settings.SUBSCRIPTION_YEAR_PLAN):
                request.user.mark_has_tried_subscriptions()


            alertas.subscriptions.create(
                user=request.user,
                evento=request.session['cart']['evento'],
                provincia=request.session['cart']['provincia'],
                subscription=subscription,
                send_email='daily',
            )

            del request.session['cart']

            return redirect("dashboard-index")

    return HttpResponse("", status=400)


@login_required
def remove_card(request):

    # TODO: customer does not exist (if customer doesn't exist, ignore, shouldn't be called?)
    # TODO: Create customer by default?
    if request.method == 'GET':
        card_id = request.GET.get("cardId")

        customer = request.user.djstripe_customers.get()
        customer.default_source = None
        customer.save()
        messages.add_message(request, messages.SUCCESS,
                             'Tarjeta modificada correctamente')
        return HttpResponse("Success", status=200)

    return HttpResponse("Fail", status=400)


@login_required
def alerta_remove_person(request, id):
    alerta = AlertaPerson.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('service-follow'))


"""
# UNUSED
@method_decorator(login_required, name='dispatch')
class UserSubscriptionCreateView(CreateView):
    model = UserSubscription
    fields = ("company", "send_html")
"""


# TODO: CSRF con POST
@login_required
def suggest_company(request):
    results = []
    if request.method == "GET" and request.is_ajax():
        term = request.GET.get("term").strip()
        if len(term) > 2:
            # FIXME: elasticsearch
            # search_results = SearchQuerySet().filter(content=term).models(Company)[:MAX_RESULTS_AJAX]
            search_results = []

            for result in search_results:
                results.append({"id": empresa_slug(result.text), "value": result.text})

    return HttpResponse(json.dumps(results), content_type="application/json")


@login_required
def suggest_person(request):
    results = []
    if request.method == "GET" and request.is_ajax():
        term = request.GET.get("term").strip()
        if len(term) > 2:
            search_results = SearchQuerySet().filter(content=term).models(Person)[:MAX_RESULTS_AJAX]

            for result in search_results:
                results.append({"id": slugify(result.text), "value": result.text})

    return HttpResponse(json.dumps(results), content_type="application/json")


@staff_member_required
@login_required
def download_alerta_history_csv(request, id):

    try:
        alerta = AlertaHistory.objects.get(pk=id, user=request.user)

        path = alerta.get_csv_path()
        provincia = alerta.get_provincia_display().replace(" ", "_")
        filename = '{0}_{1}_{2}.csv'.format(alerta.type, provincia, alerta.date.isoformat())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

        # TODO: Passing iterators
        # https://docs.djangoproject.com/en/dev/ref/request-response/#passing-iterators
        with open(path) as fp:
            response.write(fp.read())

    except AlertaHistory.DoesNotExist:
        response = HttpResponse()

    return response


@login_required
def remove_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect(reverse('alertas-cart'))


# login_required
# TODO: limit to max_alerts
def ajax_follow(request):
    """Follow/Unfollow a company or a person
    """
    slug = request.POST["slug"]
    type_ = request.POST["type"]

    if not request.user.is_authenticated:
        html_message = ('Necesitas <a href="{0}" class="alert-link">'
                        'registrarte</a> primero').format(reverse('login'))
        jsonr = json.dumps({"tag": "danger",
                            "html": html_message,
                            "slug": slug})
        return HttpResponse(jsonr, status=200)

    if type_ not in ('person', 'company'):
        return HttpResponse("Invalid", status=400)
    if type_ == 'company' and not Company.objects.filter(slug=slug).exists():
        return HttpResponse("Invalid", status=400)
    if type_ == 'person' and not Person.objects.filter(slug=slug).exists():
        return HttpResponse("Invalid", status=400)

    following = Follower.toggle_follow(request.user, slug, type_)

    # TODO:
    # request.user.follow(company)

    html_message = '<i class="fas fa-check"></i>'
    jsonr = json.dumps({"tag": "success",
                        "html": html_message,
                        "slug": slug,
                        "following": following})
    return HttpResponse(jsonr, status=200)

# No vale CreateView porque la lista para elegir empresa/persona sería inmensa

# #        - En liquidación
#        - Concurso de acreedores
