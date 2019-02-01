from django.contrib.auth import get_user_model
from django.forms import BooleanField, EmailField
from django.utils.translation import ugettext_lazy as _

from django_registration.forms import RegistrationForm


class LBUserCreationForm(RegistrationForm):

    # email is already required in RegistrationForm but it doesn't hurt
    # to make sure again
    email = EmailField(label=_("Email address"), required=True,
                       help_text=_("Required."))
    accept_tos = BooleanField(label=_("Accept terms of service"),
                              required=True)

    class Meta:
        model = get_user_model()
        fields = ("email", "password1", "password2", "accept_tos")

    def save(self, commit=True):
        user = super(LBUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
