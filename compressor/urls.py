"""
URL configuration for compressor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # Include function is imported here
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('iamadmin/', admin.site.urls),  # Admin URLs
    path('', include('apps.accounts.urls')),  # Include app-specific URLs
    path('', include('apps.compressor_app.urls')),  # Include app-specific URLs
    path('', include('apps.core.urls')),  # Include app-specific URLs
    path('', include('apps.pdftodocs.urls')),  # Include app-specific URLs
    path('', include('apps.ocr.urls')),  # Include app-specific URLs
    path('', include('apps.pdfsplit.urls')),  # Include app-specific URLs
    path('', include('apps.mergepdf.urls')),  # Include app-specific URLs
    path('', include('apps.video_compression.urls')),  # Include app-specific URLs
    path('', include('apps.imagestopdf.urls')),  # Include app-specific URLs
    path('', include('apps.pdftoimages.urls')),  # Include app-specific URLs
    path('', include('apps.pdftoword.urls')),  # Include app-specific URLs
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

