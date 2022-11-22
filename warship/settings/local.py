from .base import *  # NOSONAR


# Debug
# https://docs.djangoproject.com/en/4.1/ref/settings/#debug

DEBUG = True

# Secret key
# https://docs.djangoproject.com/en/4.1/ref/settings/#secret-key

SECRET_KEY = env.str("SECRET_KEY", default="!!!SET DJANGO_SECRET_KEY!!!")

# Allowed hosts
# https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}
