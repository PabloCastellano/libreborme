from django import forms
from . import models


class AlertaCompanyModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaCompany
        exclude = ('user', 'is_enabled')


class AlertaPersonModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaPerson
        exclude = ('user', 'is_enabled')


class AlertaCompanyForm(forms.Form):
    company = forms.CharField()
    send_html = forms.BooleanField()


class AlertaPersonForm(forms.Form):
    person = forms.CharField()
    send_html = forms.BooleanField()


class AlertaActoModelForm(forms.ModelForm):
    class Meta:
        model = models.AlertaActo
        fields = ['evento', 'provincia', 'periodicidad', 'send_html']
        exclude = ('user', 'is_enabled')


class PersonalSettingsForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['email']


class NotificationSettingsForm(forms.Form):
    #notification_method = forms.ChoiceField(choices=models.NOTIFICATION_CHOICES, widget=forms.RadioSelect(attrs={'class': "radio-inline"}))
    notification_method = forms.ChoiceField(choices=models.NOTIFICATION_CHOICES)
    notification_email = forms.EmailField(required=False, help_text='E-mail donde desea recibir las alertas')
    notification_url = forms.URLField(required=False, help_text='Por ejemplo: http://myexample.org/borme_notifications.php')
