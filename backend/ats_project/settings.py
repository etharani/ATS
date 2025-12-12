# backend/ats_project/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-key'

# DEV: set to False in production
DEBUG = True

ALLOWED_HOSTS = ['*']

# -------------------------
# Installed apps
# -------------------------
INSTALLED_APPS = [
    # Django contrib apps (required for auth/permissions/contenttypes/sessions)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # Your app
    'ats_app',
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'ats_project.urls'

# -------------------------
# Templates (so Django can serve index.html from frontend_build or public)
# -------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Look in these places for index.html (dev public, Vite dist, or copied build)
        'DIRS': [
            BASE_DIR / 'frontend' / 'public',   # dev public/index.html if present
            BASE_DIR / 'frontend' / 'dist',     # vite production output (optional)
            BASE_DIR / 'frontend_build',        # where you might copy dist/
        ],
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

WSGI_APPLICATION = 'ats_project.wsgi.application'

# -------------------------
# Database (SQLite dev)
# -------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------------
# Static files
# -------------------------
STATIC_URL = '/static/'

# Where Django will look for static files in dev - add frontend build/output folders here
STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'public',   # optional dev public assets
    BASE_DIR / 'frontend_build',        # recommended place to copy production build
    BASE_DIR / 'frontend' / 'dist',     # vite production output (if you don't copy)
]

# In production you may set STATIC_ROOT and run collectstatic
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# -------------------------
# CORS (dev only)
# -------------------------
CORS_ALLOW_ALL_ORIGINS = True

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -------------------------
# Other recommended dev settings
# -------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


