from flask import jsonify

from .. import logger


def make_ok(code=200, message=None, **attrs):
    body = dict(**attrs if attrs else {})

    if message:
        body['message'] = message

    return jsonify(body), code
