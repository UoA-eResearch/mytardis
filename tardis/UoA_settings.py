# pylint: disable=wildcard-import,unused-wildcard-import,W0123
import json
from os import environ as env
from datetime import timedelta

from keystoneauth1.identity import v3
from keystoneauth1 import session
from barbicanclient import client


from .default_settings import *


BARBICAN_RABBIT_URL='https://key-manager.rc.nectar.org.au:9311/v1/secrets/79036d1a-9aa9-437f-b9d5-21a5f215cd37'
#BARBICAN_LDAP_URL='https://key-manager.rc.nectar.org.au:9311/v1/secrets/a54d4510-f2b4-49a6-962e-b1d3eec65e5b'
BARBICAN_LDAP_URL='https://key-manager.rc.nectar.org.au:9311/v1/secrets/bc87b109-a7f2-4926-a6db-64e6226ac141'
BARBICAN_POSTGRES_URL='https://key-manager.rc.nectar.org.au:9311/v1/secrets/e2391e45-9621-49d0-b0d1-a54c53a3c682'
BARBICAN_AWS_URL='https://key-manager.rc.nectar.org.au:9311/v1/secrets/e02df33f-24f3-4cc5-a21c-533b0f3433ab'
BARBICAN_DJANGO_KEY='https://key-manager.rc.nectar.org.au:9311/v1/secrets/a0937194-496c-49fa-8be3-221437f93670'
BARBICAN_EMAIL_HOST='https://key-manager.rc.nectar.org.au:9311/v1/secrets/f2fa31c4-9c72-45ce-8ae6-17c92cced1ac'
BARBICAN_SERVER_EMAIL='https://key-manager.rc.nectar.org.au:9311/v1/secrets/2c25295f-9945-47df-8a64-eb465de825ed'
BARBICAN_ADMIN_EMAILS='https://key-manager.rc.nectar.org.au:9311/v1/secrets/486f2f61-ee60-4d68-a773-10a60ae64708'
BARBICAN_ALLOWED_HOSTS='https://key-manager.rc.nectar.org.au:9311/v1/secrets/9dc90d2b-3619-4b90-8719-f03f64d0c8db'
BARBICAN_ELASTICSEARCH_HOST='https://key-manager.rc.nectar.org.au:9311/v1/secrets/057e0cc7-5b81-47e2-9131-266d4fc062a7'
BARBICAN_PGDB_HOST='https://key-manager.rc.nectar.org.au:9311/v1/secrets/ecd779d0-61b0-4120-9346-921c7ad1086a'
BARBICAN_PGDB_PORT='https://key-manager.rc.nectar.org.au:9311/v1/secrets/ed75ff1a-4dc2-4f15-b6af-80fcf1f446f9'

application_credential = v3.ApplicationCredentialMethod(application_credential_id=env.get('OS_APPLICATION_CREDENTIAL_ID'),
                                                        application_credential_secret=env.get('OS_APPLICATION_CREDENTIAL_SECRET'))


auth = v3.Auth(auth_url=env.get('OS_AUTH_URL'),
               auth_methods=[application_credential])
sess = session.Session(auth=auth)
barbican = client.Client(session=sess)
django_secret = barbican.secrets.get(BARBICAN_DJANGO_KEY)
pgdb_secret = barbican.secrets.get(BARBICAN_POSTGRES_URL)
ldap_secret = barbican.secrets.get(BARBICAN_LDAP_URL)
ldap_dict = json.loads(ldap_secret.payload)
aws_secret = barbican.secrets.get(BARBICAN_AWS_URL)
aws_dict = json.loads(aws_secret.payload)
rabbit_secret = barbican.secrets.get(BARBICAN_RABBIT_URL)
email_host = barbican.secrets.get(BARBICAN_EMAIL_HOST)
server_email = barbican.secrets.get(BARBICAN_SERVER_EMAIL)
admin_emails = barbican.secrets.get(BARBICAN_ADMIN_EMAILS)
allowed_hosts = barbican.secrets.get(BARBICAN_ALLOWED_HOSTS)
elasticsearch_host = barbican.secrets.get(BARBICAN_ELASTICSEARCH_HOST)
pgdb_host = barbican.secrets.get(BARBICAN_PGDB_HOST)
pgdb_port = barbican.secrets.get(BARBICAN_PGDB_PORT)

SECRET_KEY = django_secret.payload
DEBUG = True
SITE_TITLE = 'MyTardis Development Version - Tardis 1'
DEFAULT_INSTITUTION = 'University of Auckland'
TIME_ZONE = 'Pacific/Auckland'
EMAIL_HOST = email_host.payload
SERVER_EMAIL = server_email.payload
ADMINS = eval(admin_emails.payload.decode('UTF-8'))
#Restricting Posts 'HOST:' variable to reference local hosts
#Without this, cross site hacks can be injected into queries.
ALLOWED_HOSTS = eval(allowed_hosts.payload.decode('UTF-8'))
# Use the built-in SQLite database for testing.
# The database needs to be named something other than "tardis" to avoid
# a conflict with a directory of the same name.
#DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
#DATABASES['default']['NAME'] = 'tardis_db'
#
DATABASES = {
'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'mytardis_db',
    'USER': 'mytardis',
    'PASSWORD': pgdb_secret.payload,
    'HOST': pgdb_host.payload.decode('UTF-8'),
    'PORT': pgdb_port.payload.decode('UTF-8'),
}
}

AUTH_PROVIDERS = (
('localdb', 'Local DB', 'tardis.tardis_portal.auth.localdb_auth.DjangoAuthBackend'),
('ldap', 'LDAP', 'tardis.tardis_portal.auth.ldap_auth.ldap_auth'),
)
# LDAP configuration
LDAP_USE_TLS = ldap_dict['LDAP_USE_TLS']
LDAP_URL = ldap_dict['LDAP_URL']

LDAP_USER_LOGIN_ATTR = ldap_dict['LDAP_USER_LOGIN_ATTR']
LDAP_USER_ATTR_MAP = ldap_dict['LDAP_USER_ATTR_MAP']
LDAP_GROUP_ID_ATTR = ldap_dict['LDAP_GROUP_ID_ATTR']
LDAP_GROUP_ATTR_MAP = ldap_dict['LDAP_GROUP_ATTR_MAP']
LDAP_ADMIN_USER = ldap_dict['LDAP_ADMIN_USER']
LDAP_ADMIN_PASSWORD = ldap_dict['LDAP_ADMIN_PASSWORD']
LDAP_BASE = ldap_dict['LDAP_BASE']
LDAP_USER_BASE = ldap_dict['LDAP_USER_BASE']
LDAP_GROUP_BASE = ldap_dict['LDAP_GROUP_BASE']
LDAP_METHOD = ldap_dict['LDAP_METHOD']

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_DOWNLOAD = 's3'
DEFAULT_STORAGE_BASE_DIR = 'tardis'

INSTALLED_APPS += (
'storages',
'django_elasticsearch_dsl',
'tardis.apps.search',
)

ELASTICSEARCH_DSL = {
'default': {
    'hosts': elasticsearch_host.payload.decode('UTF-8')
    },
}
ELASTICSEARCH_DSL_AUTOSYNC = False
ELASTICSEARCH_DSL_INDEX_SETTINGS = {
'number_of_shards': 10
}

AWS_S3_ACCESS_KEY_ID = aws_dict['AWS_S3_ACCESS_KEY_ID']
AWS_S3_SECRET_ACCESS_KEY = aws_dict['AWS_S3_SECRET_ACCESS_KEY']
AWS_SESSION_TOKEN = aws_dict['AWS_SESSION_TOKEN']
AWS_AUTO_CREATE_BUCKET = aws_dict['AWS_AUTO_CREATE_BUCKET']
AWS_DEFAULT_ACL = aws_dict['AWS_DEFAULT_ACL']
AWS_BUCKET_ACL = aws_dict['AWS_BUCKET_ACL']
AWS_S3_REGION_NAME = aws_dict['AWS_S3_REGION_NAME']
AWS_S3_URL_PROTOCOL = aws_dict['AWS_S3_URL_PROTOCOL']
AWS_S3_HOST = aws_dict['AWS_S3_HOST']
AWS_S3_PORT = aws_dict['AWS_S3_PORT']
AWS_S3_ENDPOINT_URL = aws_dict['AWS_S3_ENDPOINT_URL']
AWS_S3_USE_SSL = aws_dict['AWS_S3_USE_SSL']
AWS_S3_VERIFY = aws_dict['AWS_S3_VERIFY']
#512M The maximum amount of memory (in bytes) a file can take up before being rolled over into a temporary file on disk.
AWS_S3_MAX_MEMORY_SIZE = aws_dict['AWS_S3_MAX_MEMORY_SIZE']
#Overflow directory
FILE_UPLOAD_TEMP_DIR = path.abspath(path.join(path.dirname(__file__), '../var/s3_tmp_store/')).replace('\\', '/')

#CELERY_RESULT_BACKEND = 'amqp'
CELERY_RESULT_BACKEND = 'rpc'
# TODO UPDATE THIS

BROKER_URL = rabbit_secret.payload.decode('UTF-8')
CELERYBEAT_SCHEDULE = {
    "verify-files": {
        "task": "tardis_portal.verify_dfos",
        "schedule": timedelta(seconds=300)
    }
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 2147483648

DEFAULT_PERMISSIONS = ['add_experiment',
                  'change_experiment',
                  'add_dataset',
                  'change_dataset',
                  'add_datafile',
                  'change_objectacl',
                  'change_group']


LOGGING = {
'version': 1,
'disable_existing_loggers': False,
'handlers': {
    'file': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': '/home/mytardis/mytardis/debug.log',
    },
},
'loggers': {
    'django': {
        'handlers': ['file'],
        'level': 'DEBUG',
        'propagate': True,
    },
},
}
