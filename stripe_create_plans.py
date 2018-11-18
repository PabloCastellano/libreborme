#!/usr/bin/env python3
import os

import stripe

stripe.log = 'debug'
stripe.api_key = os.getenv("STRIPE_SECRET_KEY",
                           "sk_test_eVEoxiTuoWOlSw104llgXvcs")

# Definition: 20181015
ALERTS_YEAR_PLAN = "follow100"
SUBSCRIPTION_MONTH_PLAN = "subscription_month"
SUBSCRIPTION_YEAR_PLAN = "subscription_year"
API_MONTH_PLAN = "api_month"
API_YEAR_PLAN = "api_year"
TRIAL_PERIOD_DAYS = 7


def create_follow100_product_and_plan():
    """Plan anual para 100 followers"""
    product = stripe.Product.create(
        name='Suscripción Seguimiento 100',
        type='service',
    )
    product.save()
    print("Created product '{}' ({})".format(product.name, product.id))

    plan = stripe.Plan.create(
        nickname=ALERTS_YEAR_PLAN,
        product=product.id,
        amount=3600,
        currency='eur',
        interval='year'
    )
    print("Created plan '{}' ({})".format(plan.nickname, plan.id))


def create_subscription_product_and_plans():
    """Planes mensual y anual de subscripción a actos mercantiles"""
    product = stripe.Product.create(
        name='Suscripción Empresas',
        type='service',
        active=False,
    )
    product.active = True
    product.save()
    print("Created product '{}' ({})".format(product.name, product.id))

    plan = stripe.Plan.create(
        nickname=SUBSCRIPTION_MONTH_PLAN,
        product=product.id,
        amount=3000,
        currency='eur',
        interval='month',
        trial_period_days=TRIAL_PERIOD_DAYS
    )
    print("Created plan '{}' ({})".format(plan.nickname, plan.id))

    plan = stripe.Plan.create(
        nickname=SUBSCRIPTION_YEAR_PLAN,
        product=product.id,
        amount=30000,
        currency='eur',
        interval='year',
        trial_period_days=TRIAL_PERIOD_DAYS
    )
    print("Created plan '{}' ({})".format(plan.nickname, plan.id))


def create_api_product_and_plans():
    """Planes mensual y anual de uso de API"""
    product = stripe.Product.create(
        name='Suscripción API',
        type='service',
    )
    product.save()
    print("Created product '{}' ({})".format(product.name, product.id))

    plan = stripe.Plan.create(
        nickname=API_MONTH_PLAN,
        product=product.id,
        amount=8000,
        currency='eur',
        interval='month',
    )
    print("Created plan '{}' ({})".format(plan.nickname, plan.id))

    plan = stripe.Plan.create(
        nickname=API_YEAR_PLAN,
        product=product.id,
        amount=80000,
        currency='eur',
        interval='year'
    )
    print("Created plan '{}' ({})".format(plan.nickname, plan.id))


# UNUSED
def rest(plan):
    customer = stripe.Customer.create(
        email='pablo@anche.no',
        source='src_18eYalAHEMiOZZp1l9ZTjSU0',
    )
    print("Created customer '{}' ({})".format(customer.email, customer.id))

    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{'plan': plan.id}],
    )
    print("Created subscription " + subscription.id)

    # Flat fee
    stripe.Subscription.create(
        customer="{{CUSTOMER_ID}}",
        items=[
            {
                "plan": "plan_xxxxxxxxxxxxxx",
                "quantity": 1,
            },
            {
                "plan": "plan_zzzzzzzzzzzzzz",
                "quantity": 3,
            },
        ]
    )

    # Flat fee
    # <https://stripe.com/docs/billing/subscriptions/examples#flat-fee>
    plan = stripe.Plan.create(
        nickname='Monthly Base Fee',
        product=product.id,
        amount=2000,
        currency='eur',
        interval='month',
    )

    # plan = stripe.Plan.create(
    #     nickname='Subscription Monthly Tiered',
    #     product=product.id,
    #     currency='eur',
    #     interval='month',
    #     trial_period_days=TRIAL_PERIOD_DAYS,
    #     usage_type='metered',
    #     billing_scheme='tiered',
    #     tiers_mode='graduated',
    #     tiers=[
    #         {"amount": 2000, "up_to": "5"},
    #         {"amount": 1500, "up_to": "25"},
    #         {"amount": 1200, "up_to": "inf"}
    #     ]
    # )
    # DETAIL:  Failing row contains (3, plan_DC6jokyevf8XEK, f, 2018-07-08 19:26:10+00, {}, null, 2018-07-08 19:29:18.916316+00, 2018-07-08 19:29:18.916385+00, null, null, tiered, eur, month, 1, Subscription Monthly Tiered, [{"amount":2000,"up_to":5},{"amount":1500,"up_to":25},{"amount":..., graduated, null, 7, metered, null, null, null).
    return customer, subscription


if __name__ == "__main__":
    create_follow100_product_and_plan()
    create_subscription_product_and_plans()
    create_api_product_and_plans()
    # rest(plan)
