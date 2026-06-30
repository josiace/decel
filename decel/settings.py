from pathlib import Path
import os
import sqlite3
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# CORE SECURITY
# =========================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost://8000,127.0.0.1:8000,decel-sn4v.onrender.com,*'
).split(',')

# =========================
# APPS
# =========================
INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # apps
    'accounts',
    'payments',
    'exams',
    'learning',
    'gamification',
    'skills',
    'recommendations',
    'community',
    'contributor',
    'analytics',
    'api',
]

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'accounts.middleware.VisitorTrackingMiddleware',
]

ROOT_URLCONF = 'decel.urls'

# =========================
# TEMPLATES
# =========================
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
                'decel.context_processors.seo',
            ],
        },
    },
]

if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

WSGI_APPLICATION = 'decel.wsgi.application'

# =========================
# DATABASE (Render safe)
# =========================
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

# =========================
# PASSWORD VALIDATION
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================
# I18N
# =========================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =========================
# STATIC FILES (IMPORTANT FIX)
# =========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
# =========================
# MEDIA (Supabase Storage with robust backend)
# =========================
# Supabase Storage for production
if not DEBUG:
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_BUCKET = 'decel-media'
    DEFAULT_FILE_STORAGE = 'decel.storage.SupabaseStorage'
    MEDIA_URL = f'{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/'

# Fallback to local storage for development
if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# =========================
# CACHE
# =========================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =========================
# DEFAULT PRIMARY KEY
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# STRIPE
# =========================
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

STRIPE_PRICE_CREATOR_PRO = os.environ.get('STRIPE_PRICE_CREATOR_PRO', '')
STRIPE_PRICE_ACADEMY = os.environ.get('STRIPE_PRICE_ACADEMY', '')

# =========================
# AUTH
# =========================
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# =========================
# REST FRAMEWORK
# =========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# =========================
# CORS
# =========================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]

CORS_ALLOW_CREDENTIALS = True

# =========================
# SEO
# =========================
SITE_URL = config('SITE_URL', default='https://decel-sn4v.onrender.com')
SITE_NAME = 'DECEL'
SITE_TAGLINE = 'Apprentissage adaptatif intelligent'
SITE_DESCRIPTION = (
    'DECEL est une plateforme EdTech d\'apprentissage adaptatif : examens QCM stricts, '
    'suivi des compétences par matière, recommandations personnalisées, cours, TD et '
    'monnaie DC. Idéal pour lycée, université et préparation aux examens en Afrique francophone.'
)
SITE_KEYWORDS = (
    'DECEL, apprentissage adaptatif, EdTech, examens QCM, e-learning, '
    'compétences, révisions, cours en ligne, TD, Afrique francophone, '
    'Mali, préparation examens, intelligence artificielle éducation, gamification'
)
SITE_LOCALE = 'fr_FR'
SITE_LANGUAGE = 'fr'
SITE_TWITTER_HANDLE = config('SITE_TWITTER_HANDLE', default='')

# =========================
# PRODUCTION SEO & SECURITY
# =========================
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# =========================
# JAZZMIN
# =========================
JAZZMIN_SETTINGS = {
    'site_title': 'DECEL Administration',
    'site_header': 'DECEL Administration',
    'site_brand': 'DECEL',
    'welcome_sign': "Bienvenue sur DECEL",
    'copyright': 'DECEL',
    'navigation': [],
    'icons': {},
    'show_ui': {
        'top_menu': True,
        'footer': True,
        'navigation_expander': True,
    },
}