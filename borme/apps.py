from django.apps import AppConfig

from borme.utils.sanity import check_permissions

import logging

logger = logging.getLogger(__name__)


class BormeConfig(AppConfig):
    name = 'borme'

    def ready(self):
        # Note that it runs twice, check https://stackoverflow.com/questions/43577426/appconfig-ready-is-running-twice-on-django-setup-using-heroku/46206432
        check_permissions()
        logger.debug('Borme is ready')
