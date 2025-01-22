from django.urls import path
from apps.accounts.views import custom_login_view

urlpatterns = [
    path('account/login/', custom_login_view, name='custom_login'),
]