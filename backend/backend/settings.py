import os
import environ
from pathlib import Path

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

# Especifique hosts permitidos em produção
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'djoser',
    'drf_yasg',
    'django_filters',
    'django_cleanup.apps.CleanupConfig',
    # Verifique se essas apps são usadas; remova se não forem necessárias
    'django_cpf_cnpj',
    'django_extensions',
    'import_export',
    'treebeard',
    'simple_history',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.address',
    'apps.permission',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': env.str("BACKEND_DB_ENGINE", default="django.db.backends.postgresql"),
        'NAME': env.str("BACKEND_DB_NAME"),
        'USER': env.str("BACKEND_DB_USER"),
        'PASSWORD': env.str("BACKEND_DB_PASSWORD"),
        'HOST': env.str("BACKEND_DB_HOST", default="localhost"),
        'PORT': env.int("BACKEND_DB_PORT", default=5432),
    }
}

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

# Configurações de internacionalização para Brasil
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DECIMAL_SEPARATOR = ','

# Configurações de arquivos estáticos e de mídia
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(env.str("BACKEND_DATA_STORAGE", default=BASE_DIR), 'media')

# Configurações de CORS
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[env.str("BACKEND_DOMAIN", default="http://localhost:3000")])
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)

# Configurações de cache (remova se não for usado)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{env.str("BACKEND_REDIS_HOST", default="localhost")}:{env.str("BACKEND_REDIS_PORT", default="6379")}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Configurações do Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissions',
    ],
}

# Configurações do Swagger
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
}

# Modelo de usuário personalizado
AUTH_USER_MODEL = 'accounts.User'

# Configurações do Djoser
DJOSER = {
    'USER_ID_FIELD': 'uuid',
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': False,
}