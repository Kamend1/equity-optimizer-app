from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView

from EquityOptimizerApp.register.forms import CustomUserCreationForm, ProfileEditForm
from EquityOptimizerApp.register.models import Profile


# Create your views here.
class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')  # Redirect to 'home' after successful registration

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        return super().form_valid(form)


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'registration/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # Fetch the profile of the current logged-in user
        return self.request.user.profile_set

    def get_context_data(self, **kwargs):
        # Add the user's details to the context as well
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = Profile
    template_name = 'registration/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('profile_detail')

    def get_object(self, queryset=None):
        # Get the Profile object for the currently logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        # Update User data as well (e.g., username, email, etc.)
        user = self.request.user
        user.username = form.cleaned_data['username']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()

        profile = form.save(commit=False)
        profile.user = user
        profile.save()

        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/custom_password_reset.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/custom_password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/custom_password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/custom_password_reset_complete.html'


# Custom Password Change
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/custom_password_change.html'
    success_url = reverse_lazy('password_change_done')


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/custom_password_change_done.html'
