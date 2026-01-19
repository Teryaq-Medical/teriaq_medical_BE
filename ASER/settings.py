from pathlib import Path
import os
from dotenv import load_dotenv
import cloudinary

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

ALLOWED_HOSTS = ["http://127.0.0.1:8000",".vercel.app", ".now.sh"]


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
    
    # apps
    "accounts",
    "clincs",
    "doctors",
    "labs",
    "hospitals",
    "specialists"
    
]




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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



if not DEBUG :
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('NAME'),
            'USER': os.getenv('USER'),
            'PASSWORD': os.getenv('PASSWORD'),
            'HOST': os.getenv('HOST'),
            'PORT': os.getenv('PORT'),
        }
    }
else :
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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


LANGUAGE_CODE = 'ar'

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/static/"

# Collect everything into your "static" folder
STATIC_ROOT = os.path.join(BASE_DIR, "static")


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

