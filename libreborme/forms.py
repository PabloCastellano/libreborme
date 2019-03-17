from django.contrib.auth import get_user_model
from django import forms
from django.utils.translation import ugettext_lazy as _

from django_registration.forms import RegistrationFormUniqueEmail


# TODO: Mejroar el form, poner errores en rojo y alineados, la cuenta ya existe...
class LBUserCreationForm(RegistrationFormUniqueEmail):

    # email is already required in RegistrationForm but it doesn't hurt
    # to make sure again
    email = forms.EmailField(label=_("Email address"), required=True)
    accept_tos = forms.BooleanField(label=_("He leído y acepto las Condiciones de Uso, Política de Privacidad y el Uso de Cookies."),
                              required=True)
    # Remove help_text in password2
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
    )


    class Meta:
        model = get_user_model()
        fields = ("email", "password1", "password2", "accept_tos")

    def save(self, commit=True):
        user = super(LBUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


CONTACT_CHOICES = (
    ('services', 'Servicios'),
    ('gdpr', 'RGPD'),
    ('other', 'Otros'),

)
class ContactForm(forms.Form):
    name = forms.CharField(label="Nombre")
    subject = forms.ChoiceField(label="Tema", choices=CONTACT_CHOICES)
    # TODO: Placeholder "Mensaje"
    # TODO: No seleccionar opcion por defecto
    message = forms.CharField(label="Mensaje", widget=forms.Textarea)
