from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import FormView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
                                       PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView)

from EquityOptimizerApp.accounts.forms import CustomUserCreationForm, ProfileEditForm
from EquityOptimizerApp.accounts.models import Profile
from EquityOptimizerApp.mixins import ObjectOwnershipRequiredMixin


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user instance
            login(request, user)  # Log the user in after successful registration
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')  # Redirect to the desired page, e.g., 'home'
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


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


class ProfileEditView(LoginRequiredMixin, ObjectOwnershipRequiredMixin, UpdateView):
    model = Profile
    template_name = 'registration/profile_edit.html'
    form_class = ProfileEditForm

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

    def get_success_url(self):
        return reverse_lazy('profile_details', kwargs={'pk': self.object.pk})


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


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'registration/custom_password_change_done.html'


class ProfileDeleteView(LoginRequiredMixin, ObjectOwnershipRequiredMixin, DeleteView):
    model = Profile
    template_name = 'registration/profile_confirm_delete.html'
    success_url = reverse_lazy('register')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user

        profile.delete()
        user.delete()

        messages.success(request, "Your profile and account have been deleted successfully.")

        return super().delete(request, *args, **kwargs)
