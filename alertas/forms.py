from django import forms
from . import models
from djstripe.models import Customer

from libreborme.models import NOTIFICATION_CHOICES, Profile
from libreborme.provincias import PROVINCIAS_CHOICES


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


class PersonalDataForm(forms.Form):
    date_joined = forms.CharField(label="Fecha de alta", required=False, widget=forms.TextInput(attrs={'disabled': True}))
    email = forms.CharField(label="E-Mail", required=False, widget=forms.TextInput(attrs={'disabled': True}))
    first_name = forms.CharField(label="Nombre", required=False)
    last_name = forms.CharField(label="Apellidos", required=False)
    home_phone = forms.CharField(label="Teléfono", required=False, widget=forms.TextInput(attrs={'placeholder': '+34xxxxxxxxx'}))


class PersonalSettingsForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            "email": "E-Mail",
        }
        widgets = {
            'email': forms.TextInput(attrs={'disabled': True}),
        }


class ProfileDataForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['account_type', 'razon_social', 'cif_nif', 'address',
                  'post_code', 'poblacion', 'provincia', 'country']
        labels = {
            "account_type": "Tipo",
            "razon_social": "Razón social",
            "cif_nif": "CIF / NIF",
            "address": "Dirección",
            "post_code": "C.P.",
            "poblacion": "Población",
            "provincia": "Provincia",
            "country": "País",
        }
        widgets = {
            'provincia': forms.Select(choices=PROVINCIAS_CHOICES),
        }


# FIXME: It doesn't work: https://github.com/dj-stripe/dj-stripe/issues/753
# class BillingSettingsForm(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['business_vat_id']


class NotificationSettingsForm(forms.Form):
    # notification_method = forms.ChoiceField(choices=NOTIFICATION_CHOICES, widget=forms.RadioSelect(attrs={'class': "radio-inline"}))
    notification_method = forms.ChoiceField(label="Método de notificación", choices=NOTIFICATION_CHOICES)
    notification_email = forms.EmailField(label="E-mail notificación", required=False, help_text='E-mail donde desea recibir las alertas')
    notification_url = forms.URLField(label="URL notificación", required=False, help_text='Por ejemplo: http://myexample.org/borme_notifications.php (No disponible)')


class NewsletterForm(forms.Form):
    newsletter_promotions = forms.BooleanField(label="Recibir promociones", required=False, help_text="¿Quieres recibir información sobre descuentos y nuevas promociones en tu correo electrónico?")
    newsletter_features = forms.BooleanField(label="Recibir novedades", required=False, help_text="Información sobre novedades de LibreBORME")
