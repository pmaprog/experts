from flask import abort, jsonify

from . import app
from .restful_api import make_400, unauthorized, route_not_found, method_not_allowed
from .exceptions import JSONBadRequest, QuestionNotFound

app.register_error_handler(401, unauthorized)
app.register_error_handler(404, route_not_found)
app.register_error_handler(405, method_not_allowed)

app.register_error_handler(QuestionNotFound, route_not_found)


@app.errorhandler(Exception)
def handle_error(error):
    return make_400(text=str(error))


# @app.errorhandler(JSONBadRequest)
# def handle_json_error(error):
#     return jsonify('123')
#     pass
