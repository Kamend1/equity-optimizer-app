from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from EquityOptimizerApp import settings
from EquityOptimizerApp.common.forms import ContactForm


def landing(request):
    # Redirect logged-in users to the home page
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'common/landing.html')


# Create your views here.
@login_required
def home(request):
    return render(request, 'common/home.html')


def about(request):
    return render(request, 'common/about.html')


@login_required
def contact(request):

    if request.method == 'POST':
        form = ContactForm(request.POST, user=request.user)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Compose the email content
            subject = f"New Contact Form Submission from {name}"
            email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

            try:
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,  # Sender's email address (configured in settings.py)
                    [settings.CONTACT_EMAIL],  # Recipient's email address (configured in settings.py)
                    fail_silently=False,
                )

            except Exception as e:
                print("Error sending email:", e)

            return redirect('contact_success')  # Replace with your success URL

    else:
        form = ContactForm(user=request.user)

    return render(request, 'common/contact.html', {'form': form})


@login_required
def contact_success(request):
    return render(request, 'common/contact_success.html')