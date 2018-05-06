from django import forms
from django.utils.translation import ugettext_lazy as _

CHOICES = (('all', 'Todos'), ('company', 'Empresas'), ('person', 'Personas'),)


class LBSearchForm(forms.Form):
    q = forms.CharField(label='Nombre', max_length=100)
    type = forms.ChoiceField(choices=CHOICES, required=False, label=_('Tipo'),
                             widget=forms.RadioSelect)
    page = forms.IntegerField(min_value=1)
