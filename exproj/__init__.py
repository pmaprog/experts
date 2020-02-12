import logging

from flask import Flask, request
from flask_login import LoginManager
from gevent.pywsgi import WSGIServer
from gevent import monkey

from . import config, auth
from .exceptions import Error, QuestionNotFound, NotJsonError
from .restful_api import users, questions, make_400


logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    level=logging.INFO)


app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=config.CSRF_ENABLED,
    SECRET_KEY=config.SECRET_KEY,
)

app.register_blueprint(users.bp)
app.register_blueprint(questions.bp)

app.register_error_handler(401, restful_api.unauthorized)
app.register_error_handler(404, restful_api.route_not_found)
app.register_error_handler(405, restful_api.method_not_allowed)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(auth.user_loader)

# todo: change it to new implementation of Request.on_json_loading_failed(e)
@app.before_request
def before_request():
    try:
        if not request.get_json():
            raise NotJsonError
    except Exception as e:
        return make_400(text="Failed to parse JSON!")


from . import errors


def run_debug():
    logging.info('Started server in debug mode')
    app.run(host=config.HOST, port=config.PORT, debug=True)


def run():
    monkey.patch_all(ssl=False)
    http_server = WSGIServer((config.HOST, config.PORT), app)
    logging.info('Started server')
    http_server.serve_forever()
