from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from apps.accounts.models import UserAccount



def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('login')
        password = request.POST.get('password')
        print(email)
        # Check if email or password is empty
        if not email or not password:
            messages.error(request, "Email and password cannot be empty.")
            return redirect('/')  # Redirect back to the login page

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')  # Redirect to the dashboard on successful login
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('/') 