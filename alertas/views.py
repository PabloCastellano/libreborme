from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
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

from djstripe.models import Customer, Event, Plan, Subscription
from borme.models import Company, Person
from borme.templatetags.utils import slug, slug2
from libreborme.models import Profile
from libreborme import utils

from . import forms
from .models import (
    AlertaActo, AlertaHistory,
    Follower, LBInvoice
)
from .utils import get_alertas_config


MAX_RESULTS_AJAX = 15


@method_decorator(login_required, name='dispatch')
class MyAccountView(TemplateView):
    template_name = 'alertas/myaccount.html'

    def get_context_data(self, **kwargs):
        context = super(MyAccountView, self).get_context_data(**kwargs)

        context['active'] = 'dashboard'

        context['count_a'] = AlertaActo.objects.filter(
                                    user=self.request.user).count()
        context['count_f'] = Follower.objects.filter(
                                    user=self.request.user).count()
        context['n_alertas'] = context['count_a'] + context['count_f']

        today = datetime.date.today()
        context['lbinvoices'] = LBInvoice.objects.filter(
                                    user=self.request.user, end_date__gt=today)

        aconfig = get_alertas_config()
        account_type = self.request.user.profile.account_type

        context['limite_f'] = aconfig['max_alertas_follower_' + account_type]
        context['limite_a'] = aconfig['max_alertas_actos_' + account_type]

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer

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
        n_alertas = AlertaActo.objects.filter(user=self.request.user).count()
        n_alertas += Follower.objects.filter(user=self.request.user).count()
        context['n_alertas'] = n_alertas
        context['active'] = 'ayuda'
        return context


@method_decorator(login_required, name='dispatch')
class DashboardSettingsView(TemplateView):
    template_name = 'alertas/dashboard_settings.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardSettingsView, self).get_context_data(**kwargs)
        context['active'] = 'settings'

        initial = {}
        initial['notification_method'] = self.request.user.profile.notification_method
        initial['notification_email'] = self.request.user.profile.notification_email
        initial['notification_url'] = self.request.user.profile.notification_url

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer

        context["form_billing"] = forms.BillingSettingsForm(initial={'business_vat_id': customer.business_vat_id})
        context['form_notification'] = forms.NotificationSettingsForm(initial=initial)
        context['form_personal'] = forms.PersonalSettingsForm(initial={'email': self.request.user.email})
        context['form_newsletter'] = forms.NewsletterForm(initial={'email': self.request.user.email})
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


@method_decorator(login_required, name='dispatch')
class PaymentView(TemplateView):
    template_name = 'alertas/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['active'] = 'payment'

        # TODO: get or 500
        customer = Customer.objects.get(subscriber=self.request.user)
        context['customer'] = customer

        context["cards"] = customer.sources.order_by('-exp_year', '-exp_month')
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY

        return context


@method_decorator(login_required, name='dispatch')
class BillingView(TemplateView):
    template_name = 'alertas/billing.html'

    def get_context_data(self, **kwargs):
        context = super(BillingView, self).get_context_data(**kwargs)
        context['active'] = 'billing'
        context['lbinvoices'] = LBInvoice.objects.filter(user=self.request.user)

        # TODO: get or 500
        customer = Customer.objects.get(subscriber=self.request.user)
        context['customer'] = customer
        context['invoices'] = customer.invoices.all()

        try:
            context["upcoming_invoice"] = customer.upcoming_invoice()
        except stripe.error.InvalidRequestError:
            context["upcoming_invoice"] = None

        return context


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
class SubscriptionListView(TemplateView):
    template_name = "alertas/subscription_list.html"

    def get_context_data(self, **kwargs):
        context = super(SubscriptionListView, self).get_context_data(**kwargs)
        context['active'] = 'subscriptions'

        context['alertas_a'] = AlertaActo.objects.filter(user=self.request.user)
        context['form_a'] = forms.AlertaActoModelForm()
        context['count_a'] = context['alertas_a'].count()

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY

        plan_month = Plan.objects.get(nickname=settings.SUBSCRIPTION_MONTH_PLAN)
        context["plan_month"] = plan_month
        plan_year = Plan.objects.get(nickname=settings.SUBSCRIPTION_YEAR_PLAN)
        context["plan_year"] = plan_year

        context["subscriptions"] = Subscription.objects.filter(
                plan__nickname__in=(settings.SUBSCRIPTION_MONTH_PLAN, settings.SUBSCRIPTION_YEAR_PLAN),
                customer=customer)

        return context


@method_decorator(login_required, name='dispatch')
class AlertaListView(TemplateView):
    template_name = "alertas/alerta_list.html"

    def get_context_data(self, **kwargs):
        context = super(AlertaListView, self).get_context_data(**kwargs)
        context['active'] = 'alertas'

        context['alertas_f'] = Follower.objects.filter(user=self.request.user)
        context['count_f'] = context['alertas_f'].count()

        alertas_config = get_alertas_config()
        account_type = self.request.user.profile.account_type

        context['limite_f'] = alertas_config['max_alertas_follower_' + account_type]
        context['restantes_f'] = int(context['limite_f']) - context['count_f']

        context["followers"] = Follower.objects.filter(user=self.request.user)
        context['form_f'] = forms.FollowerForm()

        customer = Customer.objects.get(subscriber=self.request.user)
        context["customer"] = customer

        context["plan_year"] = Plan.objects.get(nickname=settings.ALERTS_YEAR_PLAN)

        context["subscriptions"] = Subscription.objects.filter(
                plan__nickname=settings.ALERTS_YEAR_PLAN, customer=customer)
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY
        return context


@method_decorator(login_required, name='dispatch')
class CartView(TemplateView):
    template_name = "alertas/cart.html"

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)

        if 'cart' in self.request.session:
            plan_name = self.request.session['cart']['name']
            price = self.request.session['cart']['price']

            # TODO: Get product from plan

            context['product'] = {'name': plan_name, 'qty': 1, 'price': price}
            context['total_price'] = price
            context['tax_amount'] = 0.21 * context['total_price']
            context['tax_percentage'] = 21
            context['total_with_tax'] = context['total_price'] + context['tax_amount']

        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['active'] = 'cart'
        return context


@method_decorator(login_required, name='dispatch')
class APIView(TemplateView):
    template_name = "alertas/alerta_api.html"

    def get_context_data(self, **kwargs):
        context = super(APIView, self).get_context_data(**kwargs)
        context['active'] = 'api'

        context["plan_month"] = Plan.objects.get(nickname=settings.API_MONTH_PLAN)
        context["plan_year"] = Plan.objects.get(nickname=settings.API_YEAR_PLAN)

        customer = Customer.objects.get(subscriber=self.request.user)
        context["subscriptions"] = Subscription.objects.filter(
                plan__nickname__in=(settings.API_MONTH_PLAN, settings.API_YEAR_PLAN),
                customer=customer)
        # TODO: api enabled if contated support or paid
        context["api_enabled"] = "yes"
        return context


@login_required
def alerta_person_create(request):
    if request.method == 'POST':
        form = forms.AlertaPersonModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


@login_required
def alerta_acto_create(request):
    if request.method == 'POST':
        form = forms.AlertaActoModelForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.user = request.user
            alerta.save()
    return redirect(reverse('alertas-list'))


@login_required
def add_to_cart(request, product):
    # TODO: no cobrar si ya tiene la suscripción
    try:
        plan = Plan.objects.get(nickname=product)
    except Plan.DoesNotExist:
        return redirect(reverse('dashboard-index'))

    customer = Customer.objects.get(subscriber=request.user)
    # TODO: filter status=active?
    existing_subscriptions = Subscription.objects.filter(
            plan__nickname=product, customer=customer)

    if existing_subscriptions:
        # TODO: return to correct page
        messages.add_message(request, messages.WARNING,
                             'Ya tienes una suscripción activa')
        return redirect(reverse('alertas-cart'))

    price = float(plan.amount)  # Decimal
    product = {'name': product, 'qty': 1, 'price': price}
    request.session['cart'] = product
    return redirect(reverse('alertas-cart'))


@login_required
def settings_update_notifications(request):
    if request.method == 'POST':
        form = forms.NotificationSettingsForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile.notification_method = form.cleaned_data['notification_method']
            profile.notification_email = form.cleaned_data['notification_email']
            profile.notification_url = form.cleaned_data['notification_url']
            profile.save()
    return redirect(reverse('alertas-settings'))


@login_required
def settings_update_personal(request):
    if request.method == 'POST':
        instance = User.objects.get(pk=request.user.id)
        form = forms.PersonalSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    return redirect(reverse('alertas-settings'))


@login_required
def settings_update_billing(request):
    if request.method == 'POST':
        instance = Customer.objects.get(subscriber=request.user)
        form = forms.BillingSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    return redirect(reverse('alertas-settings'))


@login_required
def add_card(request):

    if request.method == 'POST':
        customer = Customer.objects.get(subscriber=request.user)
        user_input = utils.stripe_parse_input(request)
        customer.add_card(source=user_input["token"])
        customer.save()
        messages.add_message(request, messages.SUCCESS,
                             'Tarjeta añadida correctamente')

    return redirect(reverse('alertas-payment'))


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

        # TODO: Log user created
        try:
            customer = Customer.objects.get(subscriber=request.user)
        except Customer.DoesNotExist:
            customer = Customer.create(subscriber=request.user)

        nickname = request.session['cart']['name']
        qty = request.session['cart']['qty']
        plan = Plan.objects.get(nickname=nickname)
        tax_percent = 21.0  # TODO: tax per country (?) - limit to Spain
        # next_first_timestamp = utils.date_next_first(timestamp=True)

        token = request.POST.get("stripeToken")
        try:
            # TODO: if not saved/save card, use the token once, otherwise
            # attach to customer
            # If the customer has already a source, use it
            # TODO: cuanto hay un source, se puede sacar tambien un token?
            # if customer.has_valid_source():
            #     subscription = customer.subscribe(plan, quantity=qty,
            # else:

            # TODO: Use djstripe.Subscription
            # qty = 555
            stripe.Subscription.create(
                customer=customer.stripe_id,
                items=[
                    {"plan": plan.stripe_id, "quantity": qty}
                ],
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
            del request.session['cart']
            return redirect("dashboard-index")

    """
    acct = stripe.Account.create(
      country="US",
      type="custom",
      account_token=token,
    )
    """
    # https://stripe.com/docs/api/account/object#account_object-tos_acceptance

    return HttpResponse("", status=400)


@login_required
def set_default_card(request):

    # FIXME: weird, mixed POST + GET
    if request.method == 'POST':
        card_id = request.GET.get("cardId")

        customer = Customer.objects.get(subscriber=request.user)
        customer.default_source_id = card_id
        try:
            customer.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Tarjeta modificada correctamente')
            return HttpResponse("Success", status=200)
        except Exception:
            print("Could not set default card " + card_id + " for customer " + customer.stripe_id)
            return HttpResponse("Fail", status=400)

    return HttpResponse("Fail", status=400)


@login_required
def remove_card(request):

    # FIXME: weird, mixed POST + GET
    if request.method == 'POST':
        card_id = request.GET.get("cardId")

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
    return redirect(reverse('alertas-list'))


@login_required
def alerta_remove_person(request, id):
    alerta = AlertaPerson.objects.get(user=request.user, pk=id)
    alerta.delete()
    return redirect(reverse('alertas-list'))


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

    html_message = ('<span class="glyphicon glyphicon-check" '
                    'aria-hidden="true"></span>')
    jsonr = json.dumps({"tag": "success",
                        "html": html_message,
                        "slug": slug,
                        "following": following})
    return HttpResponse(jsonr, status=200)

# No vale CreateView porque la lista para elegir empresa/persona sería inmensa

# #        - En liquidación
#        - Concurso de acreedores
