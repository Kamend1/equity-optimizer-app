from django import forms
from django.core.exceptions import ValidationError
from .models import Stock
from ..user_stock_lists.models import FavoriteStockList


class BaseDataRangeForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()

        # Additional cleaning logic can go here if needed

        return cleaned_data


class DateRangeForm(BaseDataRangeForm):
    pass


class InitialForm(forms.Form):
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        label='End Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    risk_free_rate = forms.DecimalField(
        label='Risk-Free Rate (%)',
        max_digits=5,
        decimal_places=2,
        required=True,
        help_text='Enter risk-free rate as a percentage (e.g., 3.4 for 3.4%)',
    )
    initial_investment = forms.DecimalField(
        label='Initial Investment ($)',
        max_digits=12,
        decimal_places=2,
        required=True
    )
    sim_runs = forms.IntegerField(
        label='Number of Simulation Runs',
        min_value=1,
        max_value=20000,
        required=True
    )
    favorite_list = forms.ModelChoiceField(
        queryset=None,
        label='Select Favorite Stock List',
        required=True,
        help_text='Choose an existing favorite stock list for the simulation.'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Limit the favorite_list choices to the current user's stock lists
        if user is not None:
            self.fields['favorite_list'].queryset = FavoriteStockList.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()

        # Convert risk-free rate percentage to decimal
        risk_free_rate = cleaned_data.get('risk_free_rate')
        if risk_free_rate is not None:
            cleaned_data['risk_free_rate'] = risk_free_rate / 100

        return cleaned_data
