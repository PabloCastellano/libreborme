# Functions defined in this file are not used anymore. They were written
# in order to test PostgreSQL FTS functionalities
#

from django.contrib.postgres.search import SearchVector
from django.db import connection, transaction

from borme.models import Company, Person

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def psql_update_documents():
    """
    Note: Postgres full text search is not used

    Update postgresql full text search attributes.
    This function must be run everytime new records are added to the database
    """
    affected_rows = 0

    with connection.cursor() as cursor:
        cursor.execute("UPDATE borme_company "
                       "SET document = to_tsvector(name) "
                       "WHERE document IS NULL")
        affected_rows += cursor.rowcount
        logger.info("Updated {} borme_company records".format(cursor.rowcount))

    with connection.cursor() as cursor:
        cursor.execute("UPDATE borme_person "
                       "SET document = to_tsvector(name) "
                       "WHERE document IS NULL")
        affected_rows += cursor.rowcount
        logger.info("Updated {} borme_company records".format(cursor.rowcount))

    return affected_rows


def psql_update_documents_batch():
    """
    Note: Postgres full text search is not used

    Same as psql_update_documents() but using atomic batches.
    This way, the table is not locked for a long time when the update is big
    """
    affected_rows = 0
    while Company.objects.filter(document__isnull=True).exists():
        with connection.cursor() as cursor:
            with transaction.atomic():
                for row in Company.objects.filter(document__isnull=True)[:1000]:
                    row.document = SearchVector("name")
                    row.save()
                    affected_rows += cursor.rowcount

            logger.info("Updated {} borme_company records"
                        .format(cursor.rowcount))

    while Person.objects.filter(document__isnull=True).exists():
        with connection.cursor() as cursor:
            with transaction.atomic():
                for row in Person.objects.filter(document__isnull=True)[:1000]:
                    row.document = SearchVector("name")
                    row.save()
                    affected_rows += cursor.rowcount

            logger.info("Updated {} borme_company records"
                        .format(cursor.rowcount))

    return affected_rows
