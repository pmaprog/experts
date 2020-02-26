from flask import jsonify, request, abort


def make_ok(message=None, **attrs):
    body = dict(**attrs if attrs else {})

    if message:
        body['message'] = message

    return jsonify(body)


def get_json():
    data = request.get_json()
    if data is None:
        abort(415, 'Expected json')
    return data
