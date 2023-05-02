"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY_DEFAULT = 'django-insecure-3pdl)^a8o6#bft2!5$abk4+8eq=(xbc$xow$-c3+8xw=cr%u%o'
SECRET_KEY = SECRET_KEY_DEFAULT
# use SECRET_KEY value imported from secret.py
try:
    # import SECRET_KEY custom value
    import app.secret as secret
    SECRET_KEY = secret.SECRET_KEY
    print("SECRET_KEY imported successfully from secret.py")
except Exception as e:
    print("WARNING: SECRET.PY FILE NOT FOUND, USING INSECURE KEY")
    print(repr(e))
    print("Below I will generate a key you can use, copy it and put it on secret.py in the training-ui-files directory")
    # importing the function from utils
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())

if SECRET_KEY in ("CHANGE ME PLEASE", SECRET_KEY_DEFAULT):
    print("CHANGE SECRET KEY VALUE ON app/app/secret.py !!!")
    

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False # changed from True


BEACON_IP_ADDR = "192.92.147.84"
#BEACON_DOMAINS = ["beacon-pt","gdi-tp-1.vps.tecnico.ulisboa.pt","beacon.biodata.pt", "beacon-test.biodata.pt"]
BEACON_DOMAINS = ["beacon.biodata.pt", "beacon-test.biodata.pt"]
#ALLOWED_HOSTS = ["localhost", BEACON_IP_ADDR]
ALLOWED_HOSTS = ["localhost"]
ALLOWED_HOSTS += BEACON_DOMAINS
#ALLOWED_HOSTS = ["localhost", "beacon-pt"]



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'beacon',
    'mathfilters'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# solution (inefficient) to static files not loading
import os
if DEBUG:
    STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static') ]    
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'beacon/static')


MEDIA_URL = 'media/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allowed mimetypes
import mimetypes

mimetypes.add_type("text/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)
