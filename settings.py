MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',  # make sure this is included
]

TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'store.context_processors.site_number',
            ],
        },
    },
] 