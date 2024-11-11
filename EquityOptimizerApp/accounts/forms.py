from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from EquityOptimizerApp.accounts.models import Profile, InvestorLevelChoices


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name:')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name:')
    email = forms.EmailField(required=True, label='Email:')
    terms_and_conditions = forms.BooleanField(required=True, label='I agree to the Terms and Conditions:')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Username:',
            'first_name': 'First Name:',
            'last_name': 'Last Name:',
            'email': 'Email:',
            'password1': "Password:",
            'password2': "Confirm Password:",
        }

    def clean_terms_and_conditions(self):
        terms = self.cleaned_data.get('terms_and_conditions')
        if not terms:
            raise forms.ValidationError("You must agree to the terms and conditions.")
        return terms


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }


class BaseProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    profile_image = forms.URLField(required=False)
    profile_link = forms.URLField(required=False)
    age = forms.IntegerField(required=False)
    investor_level = forms.ChoiceField(choices=InvestorLevelChoices.choices, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Profile
        fields = ['profile_image', 'profile_link', 'age', 'investor_level', 'bio']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user')
        super().__init__(*args, **kwargs)

        # Prepopulate the form with the User data
        if user:
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


class ProfileEditForm(BaseProfileForm):
    pass