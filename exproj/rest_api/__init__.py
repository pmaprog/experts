import functools
from flask import jsonify, request, abort
from flask_login import current_user


def access_required(role):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_access(role):
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator


def make_ok(description: str):
    return jsonify({
        'description': description
    })


def get_json():
    data = request.get_json()
    if data is None:
        abort(415, 'Expected json')
    return data
