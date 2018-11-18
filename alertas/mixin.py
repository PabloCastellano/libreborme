from django.conf import settings

from djstripe.models import Customer


class CustomerMixin(object):
    def get_context_data(self, **kwargs):
        context = super(CustomerMixin, self).get_context_data(**kwargs)

        try:
            customer = Customer.objects.get(subscriber=self.request.user)
        except Customer.DoesNotExist:
            customer = None
        context["customer"] = customer
        return context


class StripeMixin(object):
    def get_context_data(self, **kwargs):
        context = super(StripeMixin, self).get_context_data(**kwargs)
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY
        return context
