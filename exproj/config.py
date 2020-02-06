import os


def _get_db_connection_string():
    db_connection_string = os.getenv('DB_CONNECTION_STRING')
    if db_connection_string:
        return db_connection_string
    return 'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'.format(**os.environ)


CSRF_ENABLED = False if os.getenv('DISABLE_CSRF') else True
SECRET_KEY = os.getenv('SECRET_KEY', 'Top Secret Key, do not use in production!!!')
HOST = os.getenv('HOST_ADDR', '0.0.0.0')
PORT = int(os.getenv('PORT', '8080'))
DB_CONNECTION_STRING = _get_db_connection_string()
RUNTIME_FOLDER = os.path.dirname(os.path.abspath(__file__))
SCPITS_FOLDER = os.getenv('SCRIPT_FOLDER', '{}/evproj/scripts'.format(RUNTIME_FOLDER))

DEFAULT_USER_STATUS = os.getenv('DEFAULT_USER_STATUS')
SMTP_HOST = os.getenv('SMTP_HOST')
MAIL_LOGIN = os.getenv('MAIL_LOGIN')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
SITE_ADDR = os.getenv('SITE_ADDR')
