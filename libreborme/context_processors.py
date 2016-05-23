from django.conf import settings
from borme.models import Config


def piwik(request):
    return {'PIWIK_URL': settings.PIWIK_URL, 'PIWIK_SITE_ID': settings.PIWIK_SITE_ID}

def common(request):
    config = Config.objects.first()
    version = getattr(config, 'version', 'Unknown')
    return {'version': version, 'email_contact': settings.EMAIL_CONTACT}
