from alertas.models import UserSubscription


def create(user, evento, provincia, periodicidad='daily', subscription=None):
    obj = UserSubscription.objects.create(
        user=user,
        evento=evento,
        provincia=provincia,
        periodicidad=periodicidad,
        stripe_subscription=subscription,
    )
    return obj
