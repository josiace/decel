"""
Django settings for DECEL project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-use-environment-variable')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # DECEL Apps
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

ROOT_URLCONF = 'decel.urls'

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

WSGI_APPLICATION = 'decel.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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
LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cache Configuration - Optimisé pour la performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Session Cache - Utilise le cache par défaut basé sur fichiers
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# Stripe — Paiements
# Remplacer par vos vraies clés via variables d'environnement
# ============================================================
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_YOUR_STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_YOUR_STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_YOUR_WEBHOOK_SECRET')

# Prix Stripe pour les abonnements créateurs
# Créer les prix dans Stripe Dashboard puis renseigner les IDs ici
STRIPE_PRICE_CREATOR_PRO = os.environ.get('STRIPE_PRICE_CREATOR_PRO', '')    # ex: price_xxx
STRIPE_PRICE_ACADEMY = os.environ.get('STRIPE_PRICE_ACADEMY', '')             # ex: price_xxx

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Jazzmin Settings
JAZZMIN_SETTINGS = {
    # title of the dashboard (window title)
    'site_title': 'DECEL Administration',

    # Title on the login screen
    'site_header': 'DECEL Administration',

    # Title on the brand (top left)
    'site_brand': 'DECEL',

    # Welcome message on the dashboard
    'welcome_sign': 'Bienvenue sur le panneau d\'administration DECEL',

    # Copyright on the footer
    'copyright': 'DECEL 2024',

    # Menu
    'navigation': [
        {'url': '/analytics/admin-dashboard/', 'label': '📊 Tableau de Bord Analytique', 'icon': 'fas fa-chart-line', 'model': 'analytics'},
        {'type': 'divider'},
        {'model': 'accounts.User', 'label': 'Utilisateurs'},
        {'model': 'accounts.Country', 'label': 'Pays'},
        {'model': 'accounts.Contributor', 'label': 'Contributeurs'},
        {'model': 'accounts.DCTransaction', 'label': 'Transactions DC'},
        {'type': 'divider'},
        {'app': 'exams', 'label': 'Examens'},
        {'app': 'learning', 'label': 'Apprentissage'},
        {'app': 'community', 'label': 'Communauté'},
        {'app': 'skills', 'label': 'Compétences'},
        {'app': 'gamification', 'label': 'Gamification'},
    ],

    # Icons for models
    'icons': {
        'accounts.User': 'fas fa-users',
        'accounts.Country': 'fas fa-globe',
        'accounts.Contributor': 'fas fa-user-tie',
        'accounts.DCTransaction': 'fas fa-coins',
        'exams.Exam': 'fas fa-file-alt',
        'exams.Question': 'fas fa-question-circle',
        'exams.Choice': 'fas fa-check-square',
        'exams.ExamSession': 'fas fa-clock',
        'exams.UserAnswer': 'fas fa-pen',
        'learning.Course': 'fas fa-book',
        'learning.TD': 'fas fa-tasks',
        'learning.ContentPurchase': 'fas fa-shopping-cart',
        'community.Content': 'fas fa-newspaper',
        'community.ModerationRule': 'fas fa-gavel',
        'community.ContentPurchase': 'fas fa-receipt',
        'skills.Subject': 'fas fa-graduation-cap',
        'skills.UserSkill': 'fas fa-chart-line',
        'gamification.Leaderboard': 'fas fa-trophy',
        'gamification.LeaderboardEntry': 'fas fa-list-ol',
        'gamification.XPLog': 'fas fa-star',
        'gamification.Badge': 'fas fa-medal',
        'gamification.UserBadge': 'fas fa-award',
    },

    # Show/hide UI elements
    'show_ui': {
        'top_menu': True,
        'footer': True,
        'navigation_expander': True,
    },

    # Theme
    'theme': {
        'dark': False,
        'sidebar': 'dark',
        'header': 'white',
    },
}
