from django.contrib.auth import get_user_model
from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _

from django_registration.forms import RegistrationForm


class LBUserCreationForm(RegistrationForm):

    class Meta:
        model = get_user_model()
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super(LBUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
