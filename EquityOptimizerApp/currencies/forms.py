from django import forms
from .models import Currency


class CurrencyBaseForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol',]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. USD'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. US Dollar'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. $'}),
        }

        labels = {
            'code': "Currency Code:",
            'name': "Currency Name:",
            'symbol': "Currency Symbol:",
        }


class CurrencyCreateForm(CurrencyBaseForm):
    pass


class CurrencyEditForm(CurrencyBaseForm):
    pass
