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

