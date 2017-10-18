"""
Django settings for running tests for Resolwe package.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'secret'

DEBUG = True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'channels',
    'rest_framework',
    'guardian',
    'mathfilters',
    'versionfield',

    'resolwe',
    'resolwe.permissions',
    'resolwe.flow',
    'resolwe.toolkit',

    'resolwe_bio',

    'pipelines_template',
)

TEST_RUNNER = 'resolwe.test_helpers.test_runner.ResolweRunner'

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
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_ID = -1

# Check if PostgreSQL settings are set via environment variables
pgname = os.environ.get('PIPELINES_TEMPLATE_POSTGRESQL_NAME', 'example')
pguser = os.environ.get('PIPELINES_TEMPLATE_POSTGRESQL_USER', 'example')
pghost = os.environ.get('PIPELINES_TEMPLATE_POSTGRESQL_HOST', 'localhost')
pgport = int(os.environ.get('PIPELINES_TEMPLATE_POSTGRESQL_PORT', 55470))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': pgname,
        'USER': pguser,
        'HOST': pghost,
        'PORT': pgport,
    }
}

STATIC_URL = '/static/'

REDIS_CONNECTION = {
    'host': 'localhost',
    'port': int(os.environ.get('PIPELINES_TEMPLATE_REDIS_PORT', 57000)),
    'db': int(os.environ.get('PIPELINES_TEMPLATE_REDIS_DATABASE', 0)),
}

FLOW_EXECUTOR = {
    'NAME': 'resolwe.flow.executors.docker',
    # XXX: Change to a stable resolwe image when it will include all the required tools
    'CONTAINER_IMAGE': 'resolwe/base',
    'CONTAINER_NAME_PREFIX': 'example',
    'REDIS_CONNECTION': REDIS_CONNECTION,
    'DATA_DIR': os.path.join(PROJECT_ROOT, 'test_data'),
    'UPLOAD_DIR': os.path.join(PROJECT_ROOT, 'test_upload'),
    'RUNTIME_DIR': os.path.join(PROJECT_ROOT, 'test_runtime'),
}
# Set custom executor command if set via environment variable
if 'PIPELINES_TEMPLATE_DOCKER_COMMAND' in os.environ:
    FLOW_DOCKER_COMMAND = os.environ['PIPELINES_TEMPLATE_DOCKER_COMMAND']
FLOW_API = {
    'PERMISSIONS': 'resolwe.permissions.permissions',
}
FLOW_EXPRESSION_ENGINES = [
    {
        'ENGINE': 'resolwe.flow.expression_engines.jinja',
    },
]
FLOW_EXECUTION_ENGINES = [
    'resolwe.flow.execution_engines.bash',
    'resolwe.flow.execution_engines.workflow',
]

FLOW_MANAGER = {
    'NAME': 'resolwe.flow.managers.local',
    'REDIS_PREFIX': 'pipelines-template.manager',
    'REDIS_CONNECTION': REDIS_CONNECTION,
}

# NOTE: Since FLOW_EXECUTOR['DATA_DIR'] and FLOW_EXECUTOR['UPLOAD_DIR'] are
# shared among all containers they must use the shared SELinux label (z
# option). Each Data object's subdirectory under FLOW_EXECUTOR['DATA_DIR'] can
# use its unique SELinux label (Z option).
FLOW_DOCKER_MAPPINGS = [
    {'src': os.path.join(FLOW_EXECUTOR['DATA_DIR'], '{data_id}'),
     'dest': '/data',
     'mode': 'rw,Z'},
    {'src': FLOW_EXECUTOR['DATA_DIR'],
     'dest': '/data_all',
     'mode': 'ro,z'},
    {'src': FLOW_EXECUTOR['UPLOAD_DIR'],
     'dest': '/upload',
     'mode': 'rw,z'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'resolwe.permissions.filters.ResolwePermissionsFilter',
        'rest_framework_filters.backends.DjangoFilterBackend',
    ),
}

FLOW_PROCESSES_FINDERS = (
    'resolwe.flow.finders.FileSystemProcessesFinder',
    'resolwe.flow.finders.AppDirectoriesFinder',
)

# Channels.

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'ROUTING': 'tests.routing.channel_routing',
        'CONFIG': {
            'hosts': [(REDIS_CONNECTION['host'], REDIS_CONNECTION['port'])],
            'expiry': 3600,
        },
    },
}
