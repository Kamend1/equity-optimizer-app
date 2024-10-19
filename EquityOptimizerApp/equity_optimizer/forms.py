from django import forms
from django.core.exceptions import ValidationError
from .models import Stock


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
    num_stocks = forms.IntegerField(
        label='Number of Stocks',
        min_value=5,
        required=True
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

    def __init__(self, *args, **kwargs):
        # Extract the max value from kwargs, default to 50 if not provided
        max_num_stocks = kwargs.pop('max_num_stocks', 50)

        super().__init__(*args, **kwargs)

        # Determine the number of stocks in the database
        num_stocks_in_db = Stock.objects.count()

        # Set the maximum value for num_stocks field
        num_stocks_max_value = min(max_num_stocks, num_stocks_in_db)
        self.fields['num_stocks'].max_value = num_stocks_max_value

    def clean_num_stocks(self):
        num_stocks = self.cleaned_data.get('num_stocks')
        num_stocks_max_value = self.fields['num_stocks'].max_value

        if num_stocks and num_stocks > num_stocks_max_value:
            raise forms.ValidationError(
                f"Number of stocks cannot exceed {num_stocks_max_value}. Currently available: {num_stocks_max_value}."
            )
        return num_stocks

    def clean(self):
        cleaned_data = super().clean()

        # Convert risk-free rate percentage to decimal
        risk_free_rate = cleaned_data.get('risk_free_rate')
        if risk_free_rate is not None:
            cleaned_data['risk_free_rate'] = risk_free_rate / 100

        return cleaned_data


class StockSelectionForm(forms.Form):
    def __init__(self, num_stocks=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if num_stocks and isinstance(num_stocks, int) and num_stocks > 0:
            for i in range(num_stocks):
                self.fields[f'stock_{i}'] = forms.ModelChoiceField(
                    queryset=Stock.objects.all().order_by('ticker'),
                    label=f'Stock {i + 1}',
                    required=True,
                )
        else:
            raise ValueError("num_stocks must be a positive integer.")

    def clean(self):
        cleaned_data = super().clean()
        selected_stocks = []
        duplicate_errors = {}

        # Iterate over the cleaned_data items and collect duplicates
        for key, value in cleaned_data.items():
            if key.startswith('stock_'):
                if value in selected_stocks:
                    # Collect the duplicate error for later processing
                    duplicate_errors[key] = "This stock has already been selected."
                else:
                    selected_stocks.append(value)

        # Add errors to the respective fields
        for key, error in duplicate_errors.items():
            self.add_error(key, error)

        # Global validation error if any duplicates were found
        if duplicate_errors:
            raise ValidationError("Each stock must be unique.")

        return cleaned_data
