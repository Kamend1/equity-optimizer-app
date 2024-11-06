from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView

from EquityOptimizerApp.register.forms import CustomUserCreationForm


# Create your views here.
class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')  # Redirect to 'home' after successful registration

    def form_valid(self, form):
        # Save the user and log them in
        user = form.save()
        login(self.request, user)
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
