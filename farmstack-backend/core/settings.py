from dotenv import load_dotenv
load_dotenv()
import collections
import json
import os
from datetime import timedelta
from pathlib import Path

collections.Callable = collections.abc.Callable
from corsheaders.defaults import default_headers
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-3^tn^3x$=(dx(whzib2t_y^0()c*bv6i_!7ft*w4_-4n#7rs$v"
DEBUG = True
ALLOWED_HOSTS = ["*"]

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = [
    "--cover-html",
    "--cover-package=datahub,accounts,core, participants",
]

INSTALLED_APPS = [
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "debug_toolbar",
    "drf_yasg",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_nose",
    "django_filters",
    "django_celery_beat",
    "accounts",
    "datahub",
    "participant",
    "microsite",
    "connectors",
    "django_apscheduler",
    "ai"
]

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
NOSE_ARGS = [
    "--with-coverage",
    "--cover-package=datahub,participant",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "test"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "OPTIONS": {
            "client_encoding": "UTF8",
        },
    },
    "vector_db":{
        "NAME":"QDRANT",
        "HOST":os.environ.get("QDRANT_HOST", "localhost"),
        "PORT_GRPC":os.environ.get("QDRANT_PORT_GRPC", "5439"),
        "PORT_HTTP":os.environ.get("QDRANT_PORT_HTTP", "5438"),
        "GRPC_CONNECT":os.environ.get("GRPC_CONNECT", True),
        "COLLECTION_NAME":os.environ.get("VECTOR_DB_COLLECTION_NAME", "NEW_GLOBAL_ALL"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "static/"

if os.environ.get("STORAGE", "s3") == "s3":
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID",'')
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY",'')
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME",'')
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME",'')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    MEDIA_URL = "media/"

MEDIA_ROOT = MEDIA_URL

PROTECTED_MEDIA_ROOT = os.path.join(BASE_DIR, 'protected')
PROTECTED_MEDIA_URL = "protected/"
SUPPORT_TICKET_V2 = "support_ticket/"
SUPPORT_RESOLUTIONS = "support_resolutions/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "media/"),
]

# Create static directory if not exists
STATIC_PATH = os.path.join(BASE_DIR, STATIC_URL)
if not os.path.exists(STATIC_PATH):
    os.makedirs(STATIC_PATH)

DOCUMENTS_ROOT = os.path.join(BASE_DIR, "media/documents/")
DOCUMENTS_URL = "media/documents/"
if not os.path.exists(DOCUMENTS_ROOT):
    os.makedirs(DOCUMENTS_ROOT)

THEME_ROOT = os.path.join(BASE_DIR, "media/theme/")
THEME_URL = "media/theme/"
# if not os.path.exists(THEME_ROOT): os.makedirs(THEME_ROOT)

PROFILE_PICTURES_PATH = os.path.join(BASE_DIR, "media/users")
PROFILE_PICTURES_URL = "users/profile_pictures/"
ORGANIZATION_IMAGES_URL = "organizations/logos/"
ISSUE_ATTACHEMENT_URL = "users/tickets/"
SOLUCTION_ATTACHEMENT_URL = "users/tickets/soluctions/"
SAMPLE_DATASETS_URL = "users/datasets/sample_data/"
CONNECTORS_CERTIFICATE_URL = "users/connectors/certificates/"
TEMP_DATASET_PATH = os.path.join(BASE_DIR, "media/temp/datasets/")
TEMP_DATASET_URL = "temp/datasets/"
TEMP_STANDARDISED_PATH = os.path.join(BASE_DIR, "media/temp/standardised/")
TEMP_STANDARDISED_DIR = "temp/standardised/"

DATASET_FILES_PATH = os.path.join(PROTECTED_MEDIA_ROOT, "datasets/")
DATASET_FILES_URL = os.path.join(PROTECTED_MEDIA_URL, "datasets/")
POLICY_FILES_PATH = os.path.join(BASE_DIR, "media/policy/")
POLICY_FILES_URL = os.path.join(MEDIA_URL, "policy/")
TEMP_CONNECTOR_PATH = os.path.join(BASE_DIR, "media/temp/connectors/")
TEMP_CONNECTOR_URL = os.path.join(MEDIA_URL, "temp/connectors/")
CONNECTOR_FILES_PATH = os.path.join(BASE_DIR, "media/connectors/")
CONNECTOR_FILES_URL = os.path.join(MEDIA_URL, "connectors/")
STANDARDISED_FILES_PATH = os.path.join(PROTECTED_MEDIA_ROOT, "standardised/")
STANDARDISED_FILES_URL = os.path.join(PROTECTED_MEDIA_URL, "standardised/")

RESOLUTIONS_ATTACHMENT_PATH = os.path.join(BASE_DIR, SUPPORT_RESOLUTIONS, "resolutions/")
RESOLUTIONS_ATTACHMENT_URL = os.path.join(SUPPORT_RESOLUTIONS, "resolutions/")
SUPPORT_TICKET_FILES_PATH = os.path.join(BASE_DIR, SUPPORT_TICKET_V2, "support/")
SUPPORT_TICKET_FILES_URL = os.path.join(SUPPORT_TICKET_V2, "support/")
RESOURCES_PATH = os.path.join(BASE_DIR, "media/users/resources/")
RESOURCES_URL = "users/resources/"
RESOURCES_AUDIOS_PATH = os.path.join(BASE_DIR, "media/users/resources/audios/")
RESOURCES_AUDIOS = os.path.join(MEDIA_URL, "users/resources/audios/")

# Create all required local directories
for path in [
    TEMP_STANDARDISED_PATH,
    STANDARDISED_FILES_PATH,
    TEMP_CONNECTOR_PATH,
    CONNECTOR_FILES_PATH,
    RESOURCES_PATH,
    RESOURCES_AUDIOS_PATH,
    PROFILE_PICTURES_PATH,
    POLICY_FILES_PATH,
    DATASET_FILES_PATH,
    SUPPORT_TICKET_FILES_PATH,
    RESOLUTIONS_ATTACHMENT_PATH,
]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# Template Files
SINGLE_PULL_PROVIDER_TEMPLATE_XML = os.path.join(
    BASE_DIR, "utils/templates/single-pull-based/provider_xml_template.json"
)
SINGLE_PULL_PROVIDER_TEMPLATE_YAML = os.path.join(
    BASE_DIR, "utils/templates/single-pull-based/provider_yaml_template.json"
)
SINGLE_PULL_CONSUMER_TEMPLATE_XML = os.path.join(
    BASE_DIR, "utils/templates/single-pull-based/consumer_xml_template.json"
)
SINGLE_PULL_CONSUMER_TEMPLATE_YAML = os.path.join(
    BASE_DIR, "utils/templates/single-pull-based/consumer_yaml_template.json"
)
EVENT_BASED_PULL_PROVIDER_TEMPLATE_XML = os.path.join(
    BASE_DIR, "utils/templates/event-pull-based/provider_xml_template.json"
)
EVENT_BASED_PULL_PROVIDER_TEMPLATE_YAML = os.path.join(
    BASE_DIR, "utils/templates/event-pull-based/provider_yaml_template.json"
)
EVENT_BASED_PULL_CONSUMER_TEMPLATE_XML = os.path.join(
    BASE_DIR, "utils/templates/event-pull-based/consumer_xml_template.json"
)
EVENT_BASED_PULL_CONSUMER_TEMPLATE_YAML = os.path.join(
    BASE_DIR, "utils/templates/event-pull-based/consumer_yaml_template.json"
)

CONNECTOR_CONFIGS = os.path.join(BASE_DIR, "connector_configs/")
CONNECTOR_STATICS = os.path.join(CONNECTOR_CONFIGS, "static_configs/")
CONNECTOR_TEMPLATE_STATICS = os.path.join(CONNECTOR_CONFIGS, "static_template_configs/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "send_grid_key")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "email_host_user")
USE_X_FORWARDED_HOST = True

OTP_DURATION = 900
OTP_LIMIT = 3
USER_SUSPENSION_DURATION = 300

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "django_cache/"),
    }
}

FIXTURE_DIRS = ["fixtures"]

SPECTACULAR_SETTINGS = {
    "TITLE": "Datahub API",
    "DESCRIPTION": "API for datahub",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "formatters": {
        "Simple_Format": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "with_datetime": {
            "format": "[%(asctime)s] [%(levelname)-s] %(lineno)-4s%(name)-15s %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "./logs/log_file.log",
            "formatter": "with_datetime",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "with_datetime",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate":False
        },
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ['Set-Cookie']
INTERNAL_IPS = "*"

FILE_UPLOAD_MAX_SIZE = 2
FILE_TYPES_ALLOWED = ["pdf", "doc", "docx"]
IMAGE_TYPES_ALLOWED = ["jpg", "jpeg", "png"]
TEMP_FILE_PATH = os.path.join(BASE_DIR, "tmp/datahub/")
CSS_FILE_NAME = "override.css"

CSS_ROOT = os.path.join(BASE_DIR, "media/theme/css/")
CSS_URL = "media/theme/css/"
if not os.path.exists(CSS_ROOT):
    os.makedirs(CSS_ROOT)
if not os.path.exists(TEMP_FILE_PATH):
    os.makedirs(TEMP_FILE_PATH)
if not os.path.exists("logs"):
    os.makedirs("logs")

SAGUBAGU_API_KEY = os.environ.get("SAGUBAGU_API_KEY",'')
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY",'')
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY",'')
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL",'')
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024 # 25 Mb limit
CELERY_BROKER_URL = f'redis://{os.environ.get("REDIS_SERVICE", "loaclhost")}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{os.environ.get("REDIS_SERVICE", "loaclhost")}:6379/0'

SMTP_SERVER = os.environ.get("SMTP_SERVER",'')
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER",'')
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD",'')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {
    'fetch_dataset_for_all_files': {
        'task': 'core.utils.fetch_data_for_all_datasets',
        'schedule': crontab(minute=0, hour=0),
    },
}