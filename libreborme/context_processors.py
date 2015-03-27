from django.conf import settings


def piwik(request):
    return {'PIWIK_URL': settings.PIWIK_URL, 'PIWIK_SITE_ID': settings.PIWIK_SITE_ID}
