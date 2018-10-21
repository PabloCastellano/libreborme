import datetime
import logging
import os
import subprocess

import libreborme
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def get_git_revision_short_hash():
    os.chdir(os.path.dirname(libreborme.__file__))
    try:
        version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        if isinstance(version, bytes):
            version = version.decode('unicode_escape')
    except subprocess.CalledProcessError:
        logger.warning("Couldn't guess git revision")
        version = 'Unknown'
    return version


# TODO: remove unused stuff
def stripe_parse_input(request):
    user_input = {}
    user_input["token"] = request.POST.get("stripeToken")
    user_input["email"] = request.POST.get("stripeEmail")
    # Billing
    user_input["name"] = request.POST.get("stripeBillingName")
    user_input["address"] = request.POST.get("stripeBillingAddressLine1")
    user_input["zipcode"] = request.POST.get("stripeBillingAddressZip")
    user_input["state"] = request.POST.get("stripeBillingAddressState", "")
    user_input["city"] = request.POST.get("stripeBillingAddressCity")
    user_input["country"] = request.POST.get("stripeBillingAddressCountry")
    user_input["countrycode"] = request.POST.get("stripeBillingAddressCountryCode")

    # TODO: send some alert somewhere
    # if user_input["country"] != "Spain":
    #     logger.warning("Customer {} has entered a billing address whose "
    #                    "country is not Spain: {}".format(
    #                         customer.stripe_id, user_input["country"]))

    return user_input


def date_next_first(timestamp=False):
    """Return timestamp for next month 1st day"""
    next_first = datetime.date.today() + relativedelta(months=1, day=1)
    if timestamp:
        return int(next_first.strftime("%s"))
    else:
        return next_first
