from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import FormView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
                                       PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView)

from EquityOptimizerApp.accounts.forms import CustomUserCreationForm, ProfileEditForm
from EquityOptimizerApp.accounts.models import Profile


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


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'registration/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['user'] = profile.user
        return context


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    template_name = 'registration/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('profile_details')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
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

    def test_func(self):
        profile = self.get_object()
        return profile.user == self.request.user

    def handle_no_permission(self):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to edit this profile.")


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
class CustomPasswordChangeView(LoginRequiredMixin, UserPassesTestMixin, PasswordChangeView):
    template_name = 'registration/custom_password_change.html'
    success_url = reverse_lazy('password_change_done')

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to change this password.")


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'registration/custom_password_change_done.html'


class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Profile
    template_name = 'registration/profile_confirm_delete.html'
    success_url = reverse_lazy('register')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def test_func(self):
        profile = self.get_object()
        return profile.user == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to delete this profile.")
        raise PermissionDenied("You do not have permission to delete this profile.")

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user

        profile.delete()
        user.delete()

        messages.success(request, "Your profile and account have been deleted successfully.")

        return super().delete(request, *args, **kwargs)
