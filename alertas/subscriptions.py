from alertas.models import UserSubscription


def create(user, evento, provincia, subscription, periodicidad='daily'):
    obj = UserSubscription.objects.create(
        user=user,
        evento=evento,
        provincia=provincia,
        stripe_subscription=subscription,
        periodicidad=periodicidad,
    )
    return obj
