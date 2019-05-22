from .settings import *  # noqa

DATABASE_URL = "sqlite://openprecincts.db"
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}

# disable whitenoise so we don't have to collectstatic for tests
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
MIDDLEWARE_REMOVE = ["whitenoise.middleware.WhiteNoiseMiddleware"]
MIDDLEWARE = [m for m in MIDDLEWARE if m not in MIDDLEWARE_REMOVE]  # noqa
