from flask import jsonify, make_response

from .. import logger
from ..exceptions import QuestionNotFound


def make_400(text='Invalid request'):
    logger.exception('400 - [{}]'.format(text))
    body = jsonify(error=text)
    return make_response(body, 400)


def make_ok(description=None, params=None):
    body = {
        'status': 'ok',
    }
    if description:
        body['description'] = description
    if params:
        body['params'] = params
    return jsonify(body)


def unauthorized(e):
    logger.warning('401 - [{}]'.format(e))
    return jsonify(error="Unauthorized"), 401


def route_not_found(e):
    logger.warning('404 - [{}]'.format(e))
    error = 'Unknown route!'
    if isinstance(e, QuestionNotFound):
        error = f'Question with id {e.id} not found!'
    return jsonify(error=error), 404


def method_not_allowed(e):
    logger.warning('405 - [{}]'.format(e))
    return jsonify(error="Wrong route method!"), 405
