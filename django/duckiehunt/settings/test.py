"""
Django settings for running tests without Docker or external services.
Uses SQLite in-memory, disables Flickr/reCAPTCHA/SendGrid.
"""
import os

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'test-secret-key-not-for-production'

INSTALLED_APPS = [
    'duck.apps.DuckConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'django_recaptcha',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'duckiehunt.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'duck.context_processors.google_maps_api_key',
            ],
        },
    },
]

WSGI_APPLICATION = 'duckiehunt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
UPLOAD_PATH = '/tmp/duckiehunt-test-uploads/'

ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
)

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'mark'

# Disable reCAPTCHA in tests
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')

# Flickr - not initialized, marker tests should mock this
FLICKR_API_KEY = 'test-key'
FLICKR_API_SECRET = 'test-secret'
FLICKR_PHOTO_IS_PUBLIC = '0'

# Social auth
SOCIAL_AUTH_FACEBOOK_KEY = 'test'
SOCIAL_AUTH_FACEBOOK_SECRET = 'test'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'test'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'test'
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

# Email - use console backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_FROM = 'test@duckiehunt.com'
EMAIL_TO = ['test@example.com']

BASE_URL = 'http://localhost'

GOOGLE_MAPS_API_KEY = 'test-maps-key'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
