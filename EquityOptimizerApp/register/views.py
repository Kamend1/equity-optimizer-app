from django.shortcuts import render, redirect
from django.contrib.auth import login
from EquityOptimizerApp.register.forms import CustomUserCreationForm


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('home')  # Redirect to a success page or home
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form
    }

    return render(request, 'registration/register.html', context)
