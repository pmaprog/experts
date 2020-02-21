import sys
import logging

from flask import Flask, Request, _request_ctx_stack
from flask_login import LoginManager
from gevent.pywsgi import WSGIServer
from gevent import monkey

logger = logging.getLogger('exproj')
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s'
)
console_output_handler = logging.StreamHandler(sys.stderr)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)
logger.setLevel(logging.INFO)

from . import config, auth
from .exceptions import JSONBadRequest
from .restful_api import users, questions

def on_json_loading_failed(self, e):
    ctx = _request_ctx_stack.top
    if ctx is not None and ctx.app.config.get('DEBUG', False):
        raise JSONBadRequest('Failed to decode JSON object: {0}'.format(e))
    raise JSONBadRequest()

Request.on_json_loading_failed = on_json_loading_failed

app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=config.CSRF_ENABLED,
    SECRET_KEY=config.SECRET_KEY,
)

app.register_blueprint(users.bp)
app.register_blueprint(questions.bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(auth.user_loader)

from . import errors


def run_debug():
    logger.info('Started server in debug mode')
    app.run(host=config.HOST, port=config.PORT, debug=True)


def run():
    monkey.patch_all(ssl=False)
    http_server = WSGIServer((config.HOST, config.PORT), app)
    logger.info('Started server')
    http_server.serve_forever()
