#!/usr/bin/env python3
import os

import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY",
                           "sk_test_eVEoxiTuoWOlSw104llgXvcs")


def create_product():
    product = stripe.Product.create(
        name='Suscripción Libreborme',
        type='service',
        active=False,
    )
    product.active = True
    product.save()
    print("Created product " + product.id)
    return product


def create_plans(product):
    plan = stripe.Plan.create(
        nickname='Subscription Monthly',
        product=product.id,
        amount=2000,
        currency='eur',
        interval='month',
        trial_period_days=7,
    )
    print("Created plan " + plan.id)
    # plan = stripe.Plan.create(
    #     nickname='Subscription Monthly Tiered',
    #     product=product.id,
    #     currency='eur',
    #     interval='month',
    #     trial_period_days=7,
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
    print("Created plan " + plan.id)
    plan = stripe.Plan.create(
        nickname='Subscription Yearly',
        product={"name": "Subscripción Libreborme"},
        amount=30000,
        currency='eur',
        interval='year',
    )
    print("Created plan " + plan.id)

    # Flat fee
    # <https://stripe.com/docs/billing/subscriptions/examples#flat-fee>
    plan = stripe.Plan.create(
        nickname='Monthly Base Fee',
        product=product.id,
        amount=2000,
        currency='eur',
        interval='month',
    )



def rest(plan):
    customer = stripe.Customer.create(
        email='pablo@anche.no',
        source='src_18eYalAHEMiOZZp1l9ZTjSU0',
    )
    print("Created customer " + customer.id)

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
    return customer, subscription


if __name__ == "__main__":
    product = create_product()
    create_plans(product)
    # rest(plan)
