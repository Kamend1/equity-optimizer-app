from django import forms


class ContactForm(forms.Form):

    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Name'
    }))

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Email'
    }))

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message',
            'style': 'min-height: 150px; resize: vertical;'
        }),
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user instance if provided
        super().__init__(*args, **kwargs)

        # Correctly populate the email field if a user is authenticated
        if user and user.is_authenticated:
            self.fields['email'].initial = user.email
