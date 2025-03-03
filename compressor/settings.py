"""
Django settings for compressor project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from dotenv import load_dotenv
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-secret-key')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allowed Hosts
if ENVIRONMENT == 'production' and not DEBUG:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS_PROD', '').split(',')
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS_DEV', '').split(',')

# Example Output
print(f"Seceret Key: {SECRET_KEY}")
print(f"Environment: {ENVIRONMENT}")
print(f"Debug: {DEBUG}")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")

# Application definition

INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #CUSTOM APPS
    'apps.compressor_app',
    'apps.pdftodocs',
    'apps.accounts',
    'apps.core',
    'apps.ocr',
    'apps.pdfsplit',
    'apps.mergepdf',

    #THIRD PARTY
    'corsheaders',
    'simple_history',
    'import_export',
    'drf_yasg',

]

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add this line
    'simple_history.middleware.HistoryRequestMiddleware',
    'apps.accounts.middleware.RedirectLoginMiddleware',

]

ROOT_URLCONF = 'compressor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'compressor.wsgi.application'

from import_export.formats.base_formats import CSV, XLSX
IMPORT_FORMATS = [CSV, XLSX]
EXPORT_FORMATS = [XLSX]

AUTH_USER_MODEL = 'accounts.UserAccount' 
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Database Configuration
if ENVIRONMENT == 'production' and not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME_PROD'),
            'USER': os.getenv('DB_USER_PROD'),
            'PASSWORD': os.getenv('DB_PASSWORD_PROD'),
            'HOST': os.getenv('DB_HOST_PROD'),
            'PORT': os.getenv('DB_PORT_PROD'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME_DEV'),
            'USER': 'admin',
            'PASSWORD': os.getenv('DB_PASSWORD_DEV'),
            'HOST': os.getenv('DB_HOST_DEV'),
            'PORT': os.getenv('DB_PORT_DEV'),
        }
    }

# Example Output
print(f"Database Config: {DATABASES['default']}")


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
if ENVIRONMENT == 'production':
    STATIC_URL = os.getenv('STATIC_URL_PROD', '/static/')
    STATIC_ROOT = os.getenv('STATIC_ROOT_PROD', '/app/staticfiles')
    STATICFILES_DIRS = [
        os.getenv('STATIC_DIR_PROD', '/app/static')
    ]
else:
    STATIC_URL = os.getenv('STATIC_URL_DEV', '/static/')
    STATIC_ROOT = os.getenv('STATIC_ROOT_DEV', os.path.join(BASE_DIR, 'staticfiles'))
    STATICFILES_DIRS = [
        os.getenv('STATIC_DIR_DEV', os.path.join(BASE_DIR, 'static'))
    ]

# Media files (Uploaded files)
if ENVIRONMENT == 'production':
    MEDIA_URL = os.getenv('MEDIA_URL_PROD', '/media/')
    MEDIA_ROOT = os.getenv('MEDIA_ROOT_PROD', '/app/media')
else:
    MEDIA_URL = os.getenv('MEDIA_URL_DEV', '/media/')
    MEDIA_ROOT = os.getenv('MEDIA_ROOT_DEV', os.path.join(BASE_DIR, 'media/'))



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your-email@example.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your-email-password')

# Session settings
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 15860))  # Example: 15860 seconds (4 hours)

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB in bytes

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = True  # Allow all domains (use with caution)

# OR allow specific origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://0.0.0.0:8001",
    "http://192.168.29.8",
    "http://uatnms.sanimabank.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
}


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'apps.accounts.views.CustomBackend',  
]

# Redirect URLs
LOGIN_REDIRECT_URL = '/'  
LOGOUT_REDIRECT_URL = '/' 

# Optional: Set the login URL
LOGIN_URL = '/'  

CSRF_TRUSTED_ORIGINS = [
    'http://0.0.0.0:8001',  # Allow local testing
    'https://shekhardhakal.com.np',  # Production domain
    'https://www.shekhardhakal.com.np'
]
