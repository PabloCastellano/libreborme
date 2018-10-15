from django import forms
from . import models
from djstripe.models import Customer

from libreborme.models import NOTIFICATION_CHOICES


class FollowerModelForm(forms.ModelForm):
    class Meta:
        model = models.Follower
        exclude = ('user', 'is_enabled')


class FollowerForm(forms.Form):
    slug = forms.CharField()


class AlertaActoModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaActo
        fields = ['evento', 'provincia', 'periodicidad', 'send_html']
        exclude = ('user', 'is_enabled')


class PersonalSettingsForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['email']


class BillingSettingsForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['business_vat_id']


class NotificationSettingsForm(forms.Form):
    # notification_method = forms.ChoiceField(choices=NOTIFICATION_CHOICES, widget=forms.RadioSelect(attrs={'class': "radio-inline"}))
    notification_method = forms.ChoiceField(label="Método de notificación", choices=NOTIFICATION_CHOICES)
    notification_email = forms.EmailField(label="E-mail notificación", required=False, help_text='E-mail donde desea recibir las alertas')
    notification_url = forms.URLField(label="URL notificación", required=False, help_text='Por ejemplo: http://myexample.org/borme_notifications.php (No disponible)')


class NewsletterForm(forms.Form):
    promotions = forms.BooleanField(label="Recibir promociones", help_text="¿Quieres recibir información sobre descuentos y nuevas promociones en tu correo electrónico?")
    features = forms.BooleanField(label="Recibir novedades", help_text="Información sobre novedades de LibreBORME")
