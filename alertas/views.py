from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.urls import reverse

import datetime
import json
import stripe

from djstripe.models import Customer, Event, Plan, Product, Subscription
from borme.models import Company, Person
from borme.templatetags.utils import slug, slug2
from libreborme.models import Profile
from libreborme import utils

from . import forms
from .models import (
    AlertaActo, AlertaHistory,
    Follower
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


@method_decorator(login_required, name='dispatch')
class MyAccountView(CustomerMixin, TemplateView):
    template_name = 'alertas/myaccount.html'

    def get_context_data(self, **kwargs):
        context = super(MyAccountView, self).get_context_data(**kwargs)

        if context['customer'] is None:
            business_vat_id = None
        else:
            business_vat_id = context['customer'].business_vat_id

        # Prepare forms
        user_profile = self.request.user.profile

        # context["form_billing"] = forms.BillingSettingsForm(initial={
        #     'business_vat_id': business_vat_id})

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
            'account_type': user_profile.account_type,
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

        context['active'] = 'dashboard'
        context['count_a'] = AlertaActo.objects.filter(
                                    user=self.request.user).count()
        context['count_f'] = Follower.objects.filter(
                                    user=self.request.user).count()
        context['n_alertas'] = context['count_a'] + context['count_f']

        aconfig = get_alertas_config()
        context['free_follows'] = aconfig['max_alertas_follower_free']

        """
        try:
            context['ip'] = self.request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            context['ip'] = self.request.META['REMOTE_ADDR']
        """
        #import pdb; pdb.set_trace()
        return context


@method_decorator(login_required, name='dispatch')
class ProfileView(CustomerMixin, TemplateView):
    template_name = 'alertas/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        if context['customer'] is None:
            business_vat_id = None
        else:
            business_vat_id = context['customer'].business_vat_id

        # Prepare forms
        user_profile = self.request.user.profile

        # context["form_billing"] = forms.BillingSettingsForm(initial={
        #     'business_vat_id': business_vat_id})

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
        context['count_a'] = AlertaActo.objects.filter(
                                    user=self.request.user).count()
        context['count_f'] = Follower.objects.filter(
                                    user=self.request.user).count()
        context['n_alertas'] = context['count_a'] + context['count_f']

        """
        try:
            context['ip'] = self.request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            context['ip'] = self.request.META['REMOTE_ADDR']
        """
        #import pdb; pdb.set_trace()
        return context


@method_decorator(login_required, name='dispatch')
class DashboardSupportView(TemplateView):
    template_name = 'alertas/dashboard_support.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSupportView, self).get_context_data(**kwargs)
        n_alertas = AlertaActo.objects.filter(user=self.request.user).count()
        n_alertas += Follower.objects.filter(user=self.request.user).count()
        context['n_alertas'] = n_alertas
        context['active'] = 'ayuda'
        return context


@method_decorator(login_required, name='dispatch')
class TermsOfServiceView(TemplateView):
    template_name = 'alertas/terms_of_service.html'

    def get_context_data(self, **kwargs):
        context = super(TermsOfServiceView, self).get_context_data(**kwargs)
        context['active'] = 'tos'
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


class StripeView(TemplateView):
    template_name = 'alertas/stripe.html'

    def get_context_data(self, **kwargs):
        context = super(StripeView, self).get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['plans'] = Plan.objects.all()
        context['products'] = Product.objects.all()
        context['subscriptions'] = Subscription.objects.all()
        context['active'] = 'stripe'
        return context


@method_decorator(login_required, name='dispatch')
class PaymentView(StripeMixin, CustomerMixin, TemplateView):
    template_name = 'alertas/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['active'] = 'payment'

        # TODO: get or 500
        if context["customer"] is None:
            cards = None
        else:
            cards = context['customer'].sources.order_by('-exp_year', '-exp_month')
        context["cards"] = cards
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

"""
@method_decorator(login_required, name='dispatch')
class BillingDetailView(DetailView):
    model = LBInvoice

    def get_object(self):
        self.invoice = LBInvoice.objects.get(user=self.request.user, pk=self.kwargs['id'])
        return self.invoice

    def get_context_data(self, **kwargs):
        context = super(BillingDetailView, self).get_context_data(**kwargs)
        context['active'] = 'billing'
        return context
"""


@method_decorator(login_required, name='dispatch')
class AlertaDetailView(DetailView):
    model = AlertaActo
    context_object_name = 'alerta'

    def get_object(self):
        self.alerta = AlertaActo.objects.get(pk=self.kwargs['id'])
        return self.alerta


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
        context['events_by_date'] = events_by_date
        return context


@method_decorator(login_required, name='dispatch')
class ServiceSubscriptionView(CustomerMixin, StripeMixin, TemplateView):
    template_name = "alertas/service_subscription.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceSubscriptionView, self).get_context_data(**kwargs)
        context['active'] = 'subscriptions'

        context['alertas_a'] = AlertaActo.objects.filter(user=self.request.user)
        context['form_a'] = forms.AlertaActoModelForm()
        context['count_a'] = context['alertas_a'].count()

        # TODO: Si tiene suscripciones pagadas y no ha definido qué quiere, mostrarle form
        # TODO: Solo una suscripción de prueba

        if context['customer']:
            context["subscriptions"] = Subscription.objects.filter(
                    plan__nickname__in=(settings.SUBSCRIPTION_MONTH_ONE_PLAN, settings.SUBSCRIPTION_MONTH_FULL_PLAN, settings.SUBSCRIPTION_YEAR_PLAN),
                    customer=context["customer"])

        plan_month_one = Plan.objects.get(nickname=settings.SUBSCRIPTION_MONTH_ONE_PLAN)
        context["plan_month_one"] = plan_month_one
        plan_month_full = Plan.objects.get(nickname=settings.SUBSCRIPTION_MONTH_FULL_PLAN)
        context["plan_month_full"] = plan_month_full
        # plan_year = Plan.objects.get(nickname=settings.SUBSCRIPTION_YEAR_PLAN)
        # context["plan_year"] = plan_year

        return context


@method_decorator(login_required, name='dispatch')
class ServiceAlertaView(CustomerMixin, StripeMixin, TemplateView):
    template_name = "alertas/service_follow.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceAlertaView, self).get_context_data(**kwargs)
        context['active'] = 'alertas'

        context['alertas_f'] = Follower.objects.filter(user=self.request.user)
        context['count_f'] = context['alertas_f'].count()

        alertas_config = get_alertas_config()

        context['free_follows'] = int(alertas_config['max_alertas_follower_free'])
        context['remaining_follows'] = int(context['free_follows']) - context['count_f']
        context['current_follows'] = context['free_follows'] - context['remaining_follows']
        context['max_alertas_follower_paid'] = int(alertas_config['max_alertas_follower_paid'])

        context["followers"] = Follower.objects.filter(user=self.request.user)
        context['form_f'] = forms.FollowerForm()

        if context["customer"]:
            context["subscriptions"] = Subscription.objects.filter(
                    plan__nickname=settings.ALERTS_YEAR_PLAN,
                    customer=context["customer"])

        # context["plan_year"] = Plan.objects.get(nickname=settings.ALERTS_YEAR_PLAN)
        return context


@method_decorator(login_required, name='dispatch')
class CartView(CustomerMixin, StripeMixin, TemplateView):
    template_name = "alertas/cart.html"

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)

        profile = self.request.user.profile
        context['user_complete'] = profile.is_complete()
        if not context['user_complete']:
            url = reverse('alertas-profile')
            message = 'Necesitas completar <a href="{}">tu perfil</a> antes para poder contratar algún servicio.'.format(url)
            messages.add_message(self.request, messages.WARNING, message)

        elif 'cart' in self.request.session:
            taxname = 'IVA'  # TODO
            plan_name = self.request.session['cart']['name']
            price = self.request.session['cart']['price']

            plan = Plan.objects.get(nickname=plan_name)
            product_text = "{0} ({1})".format(plan.product.name, plan_name)
            context['product'] = {'name': product_text, 'price': price}
            context['total_with_tax'] = price
            context['total_price'] = round(price / (1 + TAXES[taxname]), 2)
            context['tax_amount'] = round(context['total_with_tax'] - context['total_price'], 2)
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

        context['active'] = 'cart'
        return context


@method_decorator(login_required, name='dispatch')
class ServiceAPIView(CustomerMixin, TemplateView):
    template_name = "alertas/service_api.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceAPIView, self).get_context_data(**kwargs)
        context['active'] = 'api'

        context["plan_month"] = Plan.objects.get(nickname=settings.API_MONTH_PLAN)
        # context["plan_year"] = Plan.objects.get(nickname=settings.API_YEAR_PLAN)

        if context["customer"]:
            context["subscriptions"] = Subscription.objects.filter(
                    plan__nickname__in=(settings.API_MONTH_PLAN, settings.API_YEAR_PLAN),
                    customer=context["customer"])

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
    if request.method == 'POST':
        form = forms.AlertaActoModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('service-follow'))


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
def settings_update_billing(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        profile = user.profile

        # Process forms

        # TODO: Update business_vat_id in Customer model
        # TODO: Salvar en Profile ne vez de Customer?

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


def send_email_new_subscription(user):
    full_name = user.get_full_name()
    now = datetime.datetime.now()
    mail_admins('Nueva suscripción ({})'.format(full_name),
                'En {} Stripe ha suscrito al usuario {}'.format(now, full_name))


def mark_user_has_tried_subscriptions(user):
    if not user.profile.has_tried_subscriptions:
        user.profile.has_tried_subscriptions = True
        user.profile.save()


@login_required
def checkout_existing_card(request):
    if request.method == "POST":
        nickname = request.session['cart']['name']
        plan = Plan.objects.get(nickname=nickname)
        # Customer is cheargeable so he already exists
        customer = Customer.objects.get(subscriber=request.user)
        profile = request.user.profile

        if not profile.has_tried_subscriptions:
            do_trial = True
            profile.has_tried_subscriptions = True
        else:
            do_trial = None
        customer.subscribe(plan=plan, trial_from_plan=do_trial)
        profile.save()
        # TODO: review parameters: tax_percent, trial_end, ...
        # tax_percent se suma al precio
        messages.add_message(request, messages.SUCCESS,
                             'Pago realizado con éxito. Tenga en cuenta que la activación del servicio puede tardar unos minutos.')
        send_email_new_subscription(request.user)

        if nickname in (settings.SUBSCRIPTION_MONTH_ONE_PLAN, settings.SUBSCRIPTION_MONTH_FULL_PLAN, settings.SUBSCRIPTION_YEAR_PLAN):
            mark_user_has_tried_subscriptions(request.user)

        del request.session['cart']
        return redirect("dashboard-index")


@login_required
def checkout(request):
    """Checkout

    Llegados a este punto, la compra ya está aceptada y tenemos el token,
    solo nos falta crear la suscripción
    """
    # TODO: make params
    # TODO: Capture name when get token
    # TODO: description en el payment
    # TODO: no salvar el metodo de pago si no se pide expresamente
    # TODO: Guardar si ya ha hecho el periodo de prueba
    if request.method == "POST":
        nickname = request.session['cart']['name']
        plan = Plan.objects.get(nickname=nickname)
        # TODO: Log user created
        customer, _ = Customer.get_or_create(subscriber=request.user)

        taxname = 'IVA'  # TODO: tax per province - limited to Spain
        tax_percent = TAXES[taxname]
        # next_first_timestamp = utils.date_next_first(timestamp=True)

        token = request.POST.get("stripeToken")
        try:
            # TODO: if not saved/save card, use the token once, otherwise
            # attach to customer
            # If the customer has already a source, use it
            # TODO: cuanto hay un source, se puede sacar tambien un token?
            # if customer.has_valid_source():
            #     subscription = customer.subscribe(plan)
            # else:

            # TODO: Use djstripe.Subscription
            stripe.Subscription.create(
                customer=customer.stripe_id,
                items=[
                    {"plan": plan.stripe_id}
                ],
                # TODO: source here is deprecated
                # Changes since API version 2018-05-21:
                # The subscription endpoints no longer support the source parameter.
                # If you want to change the default source for a customer, instead
                # use the source creation API to add the new source and then
                # the customer update API to set it as the default.
                source=token,
                tax_percent=tax_percent
            )
            # billing_cycle_anchor=next_first_timestamp,

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
            send_email_new_subscription(request.user)

            if nickname in (settings.SUBSCRIPTION_MONTH_ONE_PLAN, settings.SUBSCRIPTION_MONTH_FULL_PLAN, settings.SUBSCRIPTION_YEAR_PLAN):
                mark_user_has_tried_subscriptions(request.user)

            del request.session['cart']
            return redirect("dashboard-index")

    return HttpResponse("", status=400)


@login_required
def set_default_card(request):

    # FIXME: weird, mixed POST + GET
    if request.method == 'POST':
        card_id = request.GET.get("cardId")

        try:
            customer = Customer.objects.get(subscriber=request.user)
            customer.default_source_id = card_id
            customer.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Tarjeta modificada correctamente')
            return HttpResponse("Success", status=200)
        except Customer.DoesNotExist:
            # TODO: create customer if doesn't exist
            pass
        except Exception:
            print("Could not set default card " + card_id + " for customer " + customer.stripe_id)
            return HttpResponse("Fail", status=400)

    return HttpResponse("Fail", status=400)


@login_required
def remove_card(request):

    # TODO: if customer doesn't exist, ignore, shouldn't be called
    # FIXME: weird, mixed POST + GET
    if request.method == 'POST':
        card_id = request.GET.get("cardId")

        # Check self.request.user.customer
        # or .djstripe_customers
        customer = Customer.objects.get(subscriber=request.user)
        cards = customer.sources.all()
        for card in cards:
            if card.stripe_id == card_id:
                card.remove()
                messages.add_message(request, messages.SUCCESS,
                                     'Tarjeta eliminada correctamente')
                return HttpResponse("Success", status=200)

        print("Could not delete card " + card_id + " for customer " + customer.stripe_id)

    return HttpResponse("Fail", status=400)


@login_required
def alerta_remove_acto(request, id):
    alerta = AlertaActo.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('service-follow'))


@login_required
def alerta_remove_person(request, id):
    alerta = AlertaPerson.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('service-follow'))


@method_decorator(login_required, name='dispatch')
class AlertaActoCreateView(CreateView):
    model = AlertaActo
    fields = ("company", "send_html")


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
                results.append({"id": slug2(result.text), "value": result.text})

    return HttpResponse(json.dumps(results), content_type="application/json")


@login_required
def suggest_person(request):
    results = []
    if request.method == "GET" and request.is_ajax():
        term = request.GET.get("term").strip()
        if len(term) > 2:
            search_results = SearchQuerySet().filter(content=term).models(Person)[:MAX_RESULTS_AJAX]

            for result in search_results:
                results.append({"id": slug(result.text), "value": result.text})

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
