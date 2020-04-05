import os
from os.path import join
from types import SimpleNamespace
from dotenv import load_dotenv

load_dotenv()


def _get_db_connection_string():
    db_connection_string = os.getenv('DB_CONNECTION_STRING')
    if db_connection_string:
        return db_connection_string
    return 'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'.format(**os.environ)


def _get_number(env):
    return int(os.getenv(env))


CSRF_ENABLED = False if os.getenv('DISABLE_CSRF') else True
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
HOST = os.getenv('HOST_ADDR', '0.0.0.0')
PORT = int(os.getenv('PORT', '8080'))
DB_CONNECTION_STRING = _get_db_connection_string()
# RUNTIME_FOLDER = os.path.dirname(os.path.abspath(__file__))
# SCRIPTS_FOLDER = os.getenv('SCRIPT_FOLDER',
#                            '{}/evproj/scripts'.format(RUNTIME_FOLDER))

DEFAULT_USER_STATUS = os.getenv('DEFAULT_USER_STATUS')
SUPER_ADMIN_MAIL = os.getenv('SUPER_ADMIN_MAIL')
SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD')

SMTP_HOST = os.getenv('SMTP_HOST')
MAIL_LOGIN = os.getenv('MAIL_LOGIN')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
SITE_ADDR = os.getenv('SITE_ADDR')

MAX_FILE_SIZE = _get_number('MAX_FILE_SIZE') * 1024 * 1024

FILE_UPLOADS = SimpleNamespace()
FILE_UPLOADS.PARENT_DIRECTORY = os.getenv('FILE_UPLOADS_PARENT_DIRECTORY')
FILE_UPLOADS.TEMP_DIRECTORY = join(FILE_UPLOADS.PARENT_DIRECTORY, 'tmp')

FILE_UPLOADS.FILE_SETS = SimpleNamespace()
FILE_UPLOADS.FILE_SETS.AVATAR = SimpleNamespace()
avatars = FILE_UPLOADS.FILE_SETS.AVATAR
avatars.DIRECTORY = join(FILE_UPLOADS.PARENT_DIRECTORY, 'avatars')
avatars.MAX_SIZE = 8 * 1024 * 1024
avatars.ALLOWED_EXTENSIONS = ('jpg', 'png')
avatars.ALLOWED_MIME_TYPES = ('image/jpeg', 'image/jpg', 'image/png')

# reports = FILE_UPLOADS.FILE_SETS['REPORT']
# reports.FOLDER = 'reports'
# reports.ALLOWED_EXTENSIONS = ('doc', 'docx', 'ppt', 'pptx', 'pdf')
# reports.ALLOWED_MIME_TYPES = (
#                                 'application/msword',
#                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
#                                 'application/vnd.ms-powerpoint',
#                                 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
#                                 'application/pdf'
#                             )
# reports.MAX_SIZE = MAX_FILE_SIZE
