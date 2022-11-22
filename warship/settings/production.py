from .base import *  # NOSONAR


# Secret key
# https://docs.djangoproject.com/en/4.1/ref/settings/#secret-key

SECRET_KEY = env.str("SECRET_KEY")

# Allowed hosts
# https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRESQL_ADDON_DB"),
        "USER": os.getenv("POSTGRESQL_ADDON_USER"),
        "PASSWORD": os.getenv("POSTGRESQL_ADDON_PASSWORD"),
        "HOST": os.getenv("POSTGRESQL_ADDON_HOST"),
        "PORT": os.getenv("POSTGRESQL_ADDON_PORT"),
    }
}

# Static root
# https://docs.djangoproject.com/en/4.1/ref/settings/#static-root

STATIC_ROOT = 'static/'

# Media root
# https://docs.djangoproject.com/en/4.1/ref/settings/#media-root

MEDIA_ROOT = 'media/'
