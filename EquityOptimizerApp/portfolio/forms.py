from django import forms
from EquityOptimizerApp.portfolio.models import Portfolio


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter portfolio name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter portfolio description'}),
            'public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',  # Bootstrap class for checkboxes
                'style': 'margin-left: 0.5em; margin-top: 0.3em;'  # Additional spacing
            })
        }
        labels = {
            'name': 'Portfolio Name',
            'description': 'Portfolio Description',
            'public': 'Make Portfolio Public'
        }


class PortfolioEditForm(PortfolioForm):
    pass

