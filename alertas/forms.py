from django import forms
from django.contrib.auth import get_user_model

from unidecode import unidecode

from libreborme.models import NOTIFICATION_CHOICES, Profile
from libreborme.provincias import PROVINCIAS_CHOICES

from . import models
from .models import EVENTOS_CHOICES, PROVINCIAS_CHOICES_ALL


class FollowerModelForm(forms.ModelForm):
    class Meta:
        model = models.Follower
        exclude = ('user', 'is_enabled')


class FollowerForm(forms.Form):
    slug = forms.CharField()


class SubscriptionModelForm(forms.ModelForm):
    class Meta:
        model = models.UserSubscription
        fields = ['evento', 'provincia', 'send_email']
        exclude = ('user', 'is_enabled')

    def __init__(self, *args, **kwargs):
        super(SubscriptionModelForm, self).__init__(*args, **kwargs)
        self.fields['evento'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['provincia'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['send_email'].widget.attrs.update({'class': 'form-control form-control-sm'})

        # Sort <option>s for <select>
        self.fields['provincia'].widget.choices = sorted(self.fields['provincia'].widget.choices, key=lambda k: unidecode(k[1]))
        self.fields['evento'].widget.choices = sorted(self.fields['evento'].widget.choices, key=lambda k: unidecode(k[1]))


class SubscriptionPlusModelForm(SubscriptionModelForm):

    provincia = forms.ChoiceField(label="Provincia", choices=PROVINCIAS_CHOICES_ALL)

    class Meta:
        model = models.UserSubscription
        fields = ['evento', 'send_email']
        exclude = ('user', 'is_enabled')

    def __init__(self, *args, **kwargs):
        super(SubscriptionPlusModelForm, self).__init__(*args, **kwargs)
        self.fields['provincia'].widget.choices.remove(('all', 'Todas las provincias'))
        self.fields['provincia'].widget.choices.insert(0, ('all', 'Todas las provincias'))


class SubscriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = models.UserSubscription
        # fields = ['evento', 'provincia', 'send_email']
        fields = ['send_email']
        labels = {
            "send_email": "Recibir E-Mail",
        }
    # evento = forms.ChoiceField(disabled=True, label="Tipo de evento", choices=EVENTOS_CHOICES)
    # provincia = forms.ChoiceField(disabled=True, choices=PROVINCIAS_CHOICES_ALL)


class PersonalDataForm(forms.Form):
    # widget=forms.TextInput(attrs={'placeholder': '+34xxxxxxxxx'})
    # date_joined = forms.CharField(label="Fecha de alta", required=False, widget=forms.TextInput(attrs={'disabled': True}))
    # email = forms.CharField(label="E-Mail", required=False, widget=forms.TextInput(attrs={'disabled': True}))
    first_name = forms.CharField(label="Nombre", required=False)
    last_name = forms.CharField(label="Apellidos", required=False)
    home_phone = forms.CharField(label="Teléfono", required=False)


class PaymentForm(forms.Form):
    name = forms.CharField(label="Nombre")
    nif = forms.CharField(label="NIF")
    address = forms.CharField(label="Domicilio")
    city = forms.CharField(label="Población")
    state = forms.CharField(label="Provincia")
    zip = forms.CharField(label="Código postal")
    country = forms.CharField(label="País")


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


# UNUSED
class NotificationSettingsForm(forms.Form):
    # notification_method = forms.ChoiceField(choices=NOTIFICATION_CHOICES, widget=forms.RadioSelect(attrs={'class': "radio-inline"}))
    notification_method = forms.ChoiceField(label="Método de notificación", choices=NOTIFICATION_CHOICES)
    notification_email = forms.EmailField(label="E-mail notificación", required=False, help_text='E-mail donde desea recibir las alertas')
    notification_url = forms.URLField(label="URL notificación", required=False, help_text='Por ejemplo: http://myexample.org/borme_notifications.php (No disponible)')


class NewsletterForm(forms.Form):
    newsletter_promotions = forms.BooleanField(label="Promociones", required=False, help_text="Quiero recibir información sobre descuentos y nuevas promociones en mi correo electrónico")
    newsletter_features = forms.BooleanField(label="Novedades", required=False, help_text="Quiero recibir información sobre novedades de Librebor.me")


class CreditCardForm(forms.Form):
    cardholder = forms.CharField(label="Titular")
    address = forms.CharField(label="Dirección")
    post_code = forms.CharField(label="Código postal")
    province = forms.CharField(label="Provincia")
    country = forms.CharField(label="País")
    card_number = forms.CharField(label="Número de tarjeta")
    exp_month = forms.CharField(label="Caducidad (mes)")
    exp_year = forms.CharField(label="Caducidad (año)")
