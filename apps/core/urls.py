from django.urls import path
from apps.core.views import DashboardView, FileCompressLogList

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/compress/logs/', FileCompressLogList.as_view(), name='filecompresslog_list'),
]
