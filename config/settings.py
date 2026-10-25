"""
Django settings for the unified sistema_escolar project.

Fusiona los proyectos ALTAS_BAJAS, Calificaciones-con-firma, Gestion_Horarios,
billetera y registro_de_empresas en un solo sitio Django.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Permite definir variables en un archivo .env local sin depender de que el
# proceso que lanza Django (shell, systemd, Podman) ya las tenga exportadas.
load_dotenv(BASE_DIR / '.env')

# El modo DEBUG queda deshabilitado por defecto: es la opción segura si alguien
# olvida definir la variable de entorno al desplegar.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

if DEBUG:
    # Únicamente en desarrollo se acepta una clave por defecto, para que el
    # proyecto pueda ejecutarse localmente sin configuración adicional.
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-solo-para-desarrollo-local')
else:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
    if not SECRET_KEY:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY es obligatoria cuando DJANGO_DEBUG no está activo.'
        )

ALLOWED_HOSTS = [h for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h]

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        'DJANGO_ALLOWED_HOSTS es obligatoria cuando DJANGO_DEBUG no está activo.'
    )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alumnos_maestros',
    'calificaciones',
    'horarios',
    'empresas',
    'billetera',

    'usuarios',
    'libros',
    'prestamos',
]

# NOTA: la carpeta firmar-documentos/core existe en el repositorio pero nunca
# se integró a este proyecto (no está en INSTALLED_APPS ni en config/urls.py).
# Se deja fuera intencionalmente hasta decidir si se fusiona con
# `calificaciones` (que ya genera actas en PDF) o se retira del repositorio.

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuarios.Miserable_Little_Pile_Of_Secrets.Alucard_Senses_Blood',
            ],
            # Insignias, íconos y campos de formulario comunes, sin {% load %} en cada plantilla.
            'builtins': ['usuarios.templatetags.Marble_Gallery'],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

if os.environ.get('POSTGRES_DB'):
    # Despliegue real (ver docker-compose.yml): la app y la base de datos
    # viven en contenedores separados y se comunican por la red interna.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['POSTGRES_DB'],
            'USER': os.environ.get('POSTGRES_USER', 'sistema_escolar'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            # Reutiliza conexiones entre requests en vez de abrir una nueva
            # cada vez; con Postgres en otro contenedor ese costo es real.
            'CONN_MAX_AGE': 60,
        }
    }
else:
    # Sin POSTGRES_DB (ej. `manage.py runserver` local sin Podman), SQLite
    # evita depender de un servidor de base de datos aparte.
    DATA_DIR = Path(os.environ.get('SQLITE_DATA_DIR', BASE_DIR / 'data'))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DATA_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

if os.environ.get('REDIS_HOST'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': f"redis://{os.environ['REDIS_HOST']}:{os.environ.get('REDIS_PORT', '6379')}/1",
        }
    }
else:
    # Sin Redis, cache en memoria del propio proceso: sirve para desarrollo
    # local, pero no se comparte entre workers de gunicorn (ver docker-compose.yml).
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

# La base de datos sigue siendo la fuente de verdad de las sesiones; la cache
# solo evita pegarle a la base en cada request. Si Redis se reinicia, nadie
# pierde la sesión (a diferencia de usar la cache como único backend).
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Destino de `collectstatic` para servir estáticos en producción (ver Dockerfile).
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'Cerberus_Gate'
LOGIN_REDIRECT_URL = 'Greta'
LOGOUT_REDIRECT_URL = 'Cerberus_Gate'

CSRF_FAILURE_VIEW = 'config.Draculas_Castle.Die_Monster'

# Correo: lo usa la firma de actas para enviar el código de verificación.
# Sin configuración, los correos se escriben en la salida estándar (los logs
# del contenedor); para enviarlos de verdad basta con definir EMAIL_HOST.
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Sistema Escolar <no-responder@localhost>')

# Bloqueo de inicio de sesión por fuerza bruta (ver usuarios.Beginning.Cerberus).
LOGIN_MAX_INTENTOS = 5
LOGIN_BLOQUEO_SEG = 15 * 60

if not DEBUG:
    # Endurecimiento aplicado solo fuera de desarrollo: en local rompería el
    # flujo normal (HTTP plano, sin certificados).
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 días
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Necesario si Podman queda detrás de un proxy (Caddy/Nginx) que termina TLS.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Nginx sirve /static/ con "Cache-Control: immutable" por 30 días. Sin un
    # hash en el nombre del archivo, un cambio de CSS no llegaba a quien ya
    # había visitado el sitio hasta un mes después. collectstatic genera
    # design-system.<hash>.css y {% static %} apunta a la versión vigente.
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'},
    }

# Logging mínimo a stdout: en contenedores el runtime (Podman/journald) ya se
# encarga de recolectar y rotar los logs, así que no gestionamos archivos acá.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
