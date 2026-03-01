from pathlib import Path
import os
from dotenv import load_dotenv
import cloudinary
import dj_database_url

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure = True
)


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-l1@llene&*armz141=d29_+c6k*2-l36#!wijnjyw*0*(341+q'


DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


JAZZMIN_SETTINGS = {
    "site_title": "Teriaq",
    "site_header": "ترياق",
    "site_brand": "ترياق",
    "site_logo": "books/img/teriaq.png",
    "login_logo": "books/img/teriaq.png",

    # Only show your apps
    "show_apps": [
        "accounts",
        "clincs",
        "doctors",
        "labs",
        "hospitals",
        "specialists",
    ],
    
    "icons": {
        "accounts.user": "fas fa-user",             # user icon
        "clincs.Clincs": "fas fa-clinic-medical",     # clinic icon
        "doctors.Doctors": "fas fa-user-doctor",       # doctor icon
        "labs.Labs": "fas fa-vials",                # lab icon
        "hospitals.Hospital": "fas fa-hospital",        # hospital icon
        "specialists.Specialist": "fas fa-stethoscope",   # stethoscope icon
    },

    "welcome_sign": "رعايتك الصحية… أسهل وأسرع",
    "copyright": "© 2025 Teriaq. All rights reserved.",

    "user_avatar": None,
    "show_sidebar": True,
    "navigation_expanded": True,
    "custom_css": "css/admin.css",
    "use_google_fonts_cdn": True,
}


JAZZMIN_UI_TWEAKS = {
    "theme": "default", 
    "dark_mode_theme": None,
    "accent": "accent-info",
    "sidebar": "sidebar-dark-info",
    "sidebar_fixed": True,
    "navbar_fixed": True,
    "footer_fixed": False,
    "layout_boxed": False,
    "button_classes": {
        "primary": "btn-info",           
        "secondary": "btn-warning", 
        "info": "btn-warning",              
        "warning": "btn-warning",        
        "success": "btn-info",          
        "danger": "btn-danger",
    },
}


AUTH_USER_MODEL = 'accounts.User'


INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'rest_framework.authtoken',
    'cloudinary',
    "corsheaders",
    
    # apps
    "ASER",
    "accounts",
    "clincs",
    "doctors",
    "labs",
    "hospitals",
    "specialists",
    "appointments"
    
]




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.CookieTokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # أو رابط الفرونت الحقيقي
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]

if DEBUG:
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

else:
    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    

ROOT_URLCONF = 'ASER.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ASER.wsgi.application'



if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
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


LANGUAGE_CODE = 'ar'

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # If you have a global static folder

# This helps WhiteNoise find the files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

