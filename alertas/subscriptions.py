from alertas.models import UserSubscription


def create(user, evento, provincia, send_email='daily', subscription=None):
    obj = UserSubscription.objects.create(
        user=user,
        evento=evento,
        provincia=provincia,
        send_email=send_email,
        stripe_subscription=subscription,
    )
    return obj
