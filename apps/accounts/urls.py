from django.urls import path
from apps.accounts.views import CustomLoginView,logout_view

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

]