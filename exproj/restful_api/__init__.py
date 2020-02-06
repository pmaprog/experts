from flask import jsonify, make_response
import logging


def make_400(text='Invalid request'):
    logging.exception('400 - [{}]'.format(text))
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
    logging.warning('401 - [{}]'.format(e))
    return jsonify(error="Unauthorized"), 401


def route_not_found(e):
    logging.warning('404 - [{}]'.format(e))
    return jsonify(error="Unknown route!"), 404


def method_not_allowed(e):
    logging.warning('405 - [{}]'.format(e))
    return jsonify(error="Wrong route method!"), 405
