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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError("Password must contain at least one letter.")
        return password2


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        error_messages={
            'required': _("Username is required."),
            'max_length': _("Username cannot exceed 150 characters."),
        },
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        error_messages={
            'required': _("Password is required."),
        },
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = self.get_user()
            if not user:
                raise forms.ValidationError(_("Invalid username or password."))
            if not user.is_active:
                raise forms.ValidationError(_("This account is inactive."))
        return cleaned_data


class BaseProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    profile_image = forms.URLField(required=False)
    profile_link = forms.URLField(required=False)
    age = forms.IntegerField(required=False)
    investor_level = forms.ChoiceField(
        choices=InvestorLevelChoices.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
    )
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), required=False)

    class Meta:
        model = Profile
        fields = ['profile_image', 'profile_link', 'age', 'investor_level', 'bio']

        help_texts = {
            'profile_image': 'Enter a link to an image you would like to have for your profile',
            'profile_link': 'Enter a link to your LinkedIn profile or other suitable link',
            'investor_level': 'Select your investor level as defined according to MiFID standards',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs['class'] = 'form-control'

        if user:
            self.fields['username'].initial = user.username or ''
            self.fields['first_name'].initial = user.first_name or ''
            self.fields['last_name'].initial = user.last_name or ''
            self.fields['email'].initial = user.email or ''

        profile = kwargs.get('instance')
        if profile:
            self.fields['profile_image'].initial = profile.profile_image or ''
            self.fields['profile_link'].initial = profile.profile_link or ''
            self.fields['age'].initial = profile.age or ''
            self.fields['investor_level'].initial = profile.investor_level or ''
            self.fields['bio'].initial = profile.bio or ''


class ProfileEditForm(BaseProfileForm):
    pass