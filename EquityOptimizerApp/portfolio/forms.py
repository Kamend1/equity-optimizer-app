from django import forms
from EquityOptimizerApp.portfolio.models import Portfolio


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'public': forms.CheckboxInput(attrs={'class': 'form-check-input'})  # Corrected line
        }
        labels = {
            'name': 'Portfolio Name',
            'description': 'Portfolio Description',
            'public': 'Make Portfolio Public'
        }


class PortfolioEditForm(PortfolioForm):
    pass

