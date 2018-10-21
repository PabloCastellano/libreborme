from django.conf import settings
from borme.models import Config


def piwik(request):
    return {'PIWIK_URL': settings.PIWIK_URL,
            'PIWIK_SITE_ID': settings.PIWIK_SITE_ID}


def common(request):
    config = Config.objects.first()
    version = getattr(config, 'version', 'Unknown')
    num_cart = 1 if 'cart' in request.session else 0
    return {'version': version,
            'email_contact': settings.EMAIL_CONTACT,
            'DOMAIN': settings.DOMAIN,
            'registration_open': settings.REGISTRATION_OPEN,
            'num_cart': num_cart}
