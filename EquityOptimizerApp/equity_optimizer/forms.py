from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from ..user_stock_lists.models import FavoriteStockList


class BaseDataRangeForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if (start_date and end_date) and start_date >= end_date:
            self.add_error('end_date', "End date cannot be start date or earlier than start date.")

        min_date = date(2010, 1, 1)
        if start_date and start_date < min_date:
            self.add_error('start_date', "Start date cannot be before January 1, 2010.")
        if end_date and end_date < min_date:
            self.add_error('end_date', "End date cannot be before January 1, 2010.")

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


        if user is not None:
            self.fields['favorite_list'].queryset = FavoriteStockList.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()

        risk_free_rate = cleaned_data.get('risk_free_rate')
        if risk_free_rate is not None:
            cleaned_data['risk_free_rate'] = risk_free_rate / 100

        return cleaned_data
