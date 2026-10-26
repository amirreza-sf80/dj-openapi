from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJ_DIR = BASE_DIR.parent / "dj_openapi"

SECRET_KEY = "django_tests_secret_key"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "dj_openapi",
]

USE_TZ = False

ROOT_URLCONF = "tests.conf.urls"
DEBUG = True
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [str(PROJ_DIR / "static")]
STATIC_ROOT = PROJ_DIR / "staticfiles"
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
INTERNAL_IPS = ("127.0.0.1",)

DJANGO_OPENAPI_SCHEMA_HANDLER = "dj_openapi.attrs.schema_builder.SchemaBuilder"
DJANGO_OPENAPI_YAML_SERIALIZER = "pyyaml"
