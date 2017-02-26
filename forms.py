from django import forms
from . import models

# TODO: ajax CharField


class AlertaCompanyModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaCompany
        exclude = ('user', 'is_enabled')


class AlertaPersonModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaPerson
        exclude = ('user', 'is_enabled')


class AlertaActoModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaActo
        fields = ['evento', 'provincia', 'periodicidad', 'send_html']
        exclude = ('user', 'is_enabled')


class PersonalSettingsForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }


class PersonalSettingsForm2(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class NotificationSettingsForm(forms.Form):
    #notification_method = forms.ChoiceField(choices=models.NOTIFICATION_CHOICES, widget=forms.RadioSelect(attrs={'class': "radio-inline"}))
    notification_method = forms.ChoiceField(choices=models.NOTIFICATION_CHOICES)
    notification_email = forms.EmailField(help_text='E-mail donde desea recibir las alertas')
    notification_url = forms.URLField(help_text='Por ejemplo: http://myexample.org/borme_notifications.php')

