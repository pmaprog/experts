from flask import abort, jsonify

from .restful_api import make_400
from .exceptions import Error, QuestionNotFound
from . import app


@app.errorhandler(Error)
def handle_error(error):
    return make_400(text=str(error))


@app.errorhandler(QuestionNotFound)
def handle_question_not_found(error):
    # abort(404) does not work
    return jsonify({'error': 'question not found'}), 404
