from django.contrib.auth import login, get_user_model, logout
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate
from apps.accounts.forms import LoginForm

User = get_user_model()


# Custom authentication backend to handle email or username
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Retrieve user by username or email
            user = User.objects.get(username=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None


class CustomLoginView(View):
    form_class = LoginForm
    template_name = 'public/index.html'

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to the dashboard
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard/')  # Redirect to dashboard
            else:
                messages.error(request, "Invalid username or password.")
                return render(request, self.template_name, {'form': form, 'login_failed': True})
        return render(request, self.template_name, {'form': form, 'login_failed': True})



def logout_view(request):
    """
    Handles user logout and redirects to the login page.
    """
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('/')  # Replace 'login' with your login page URL name