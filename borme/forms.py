from django import forms

from haystack.forms import SearchForm, model_choices


class LBSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(LBSearchForm, self).__init__(*args, **kwargs)
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=_('Search In'), widget=forms.CheckboxSelectMultiple)

    def search(self):
        sqs = super(LBSearchForm, self).search()
        models = {'Person': [], 'Company': []}
        for model in self.get_models():
            models[model.__name__] = sqs.models(model)