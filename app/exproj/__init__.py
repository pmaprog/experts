import logging

from flask import Flask
from flask_login import LoginManager
from gevent.pywsgi import WSGIServer
from gevent import monkey

from exproj import config, auth


logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    level=logging.INFO)


app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=config.CSRF_ENABLED,
    SECRET_KEY=config.SECRET_KEY,
    TEMPLATES_AUTO_RELOAD=True,
)

# app.register_error_handler(404, views.page_not_found)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.user_loader(auth.user_loader)
# login_manager.login_view = 'general.login'


def run_debug():
    logging.info('Started server in debug mode')
    app.run(host=config.HOST, port=config.PORT, debug=True)


def run():
    monkey.patch_all(ssl=False)
    http_server = WSGIServer((config.HOST, config.PORT), app)
    logging.info('Started server')
    http_server.serve_forever()


from . import routes
