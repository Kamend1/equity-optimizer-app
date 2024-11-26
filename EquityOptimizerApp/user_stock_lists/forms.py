from django import forms
from .models import FavoriteStockList


class FavoriteStockListForm(forms.ModelForm):
    class Meta:
        model = FavoriteStockList
        fields = ['name', 'description']

        labels = {
            'name': 'List Name',
            'description': 'Description',
        }

        help_texts = {
            'name': 'Enter a unique name for your favorite stock list.',
            'description': 'Provide a brief description of this stock list (optional).',
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., My Tech Stocks'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'E.g., This list includes my favorite technology stocks.',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.stocks = kwargs.pop('stocks', [])
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.stocks:
            raise forms.ValidationError("You must select at least 5 stocks.")
        if len(self.stocks) < 5:
            raise forms.ValidationError("A favorite stock list must contain at least 5 stocks.")
        if len(self.stocks) > 50:
            raise forms.ValidationError("A favorite stock list cannot contain more than 50 stocks.")
        return cleaned_data
