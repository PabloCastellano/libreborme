from django import forms
from django.contrib.auth import get_user_model
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
        fields = ['evento', 'provincia', 'periodicidad']
        exclude = ('user', 'is_enabled')


class PersonalDataForm(forms.Form):
    # widget=forms.TextInput(attrs={'placeholder': '+34xxxxxxxxx'})
    # date_joined = forms.CharField(label="Fecha de alta", required=False, widget=forms.TextInput(attrs={'disabled': True}))
    # email = forms.CharField(label="E-Mail", required=False, widget=forms.TextInput(attrs={'disabled': True}))
    first_name = forms.CharField(label="Nombre", required=False)
    last_name = forms.CharField(label="Apellidos", required=False)
    home_phone = forms.CharField(label="Teléfono", required=False)


class PersonalSettingsForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
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
            "razon_social": "Razón social o nombre",
            "cif_nif": "CIF / NIF",
            "address": "Dirección",
            "post_code": "Código postal",
            "poblacion": "Población",
            "provincia": "Provincia",
            "country": "País",
        }
        widgets = {
            'provincia': forms.Select(choices=PROVINCIAS_CHOICES),
        }


class NotificationSettingsForm(forms.Form):
    # notification_method = forms.ChoiceField(choices=NOTIFICATION_CHOICES, widget=forms.RadioSelect(attrs={'class': "radio-inline"}))
    notification_method = forms.ChoiceField(label="Método de notificación", choices=NOTIFICATION_CHOICES)
    notification_email = forms.EmailField(label="E-mail notificación", required=False, help_text='E-mail donde desea recibir las alertas')
    notification_url = forms.URLField(label="URL notificación", required=False, help_text='Por ejemplo: http://myexample.org/borme_notifications.php (No disponible)')


class NewsletterForm(forms.Form):
    newsletter_promotions = forms.BooleanField(label="Recibir promociones", required=False, help_text="¿Quieres recibir información sobre descuentos y nuevas promociones en tu correo electrónico?")
    newsletter_features = forms.BooleanField(label="Recibir novedades", required=False, help_text="Información sobre novedades de LibreBORME")


class CreditCardForm(forms.Form):
    cardholder = forms.CharField(label="Titular")
    address = forms.CharField(label="Dirección")
    post_code = forms.CharField(label="Código postal")
    province = forms.CharField(label="Provincia")
    country = forms.CharField(label="País")
    card_number = forms.CharField(label="Número de tarjeta")
    exp_month = forms.CharField(label="Caducidad (mes)")
    exp_year = forms.CharField(label="Caducidad (año)")
