from flask import jsonify, request, abort


def make_ok(description=None, **attrs):
    body = dict(**attrs if attrs else {})

    if description:
        if not isinstance(description, str) and not attrs:
            body = description
        else:
            body['description'] = description

    return jsonify(body)


def get_json():
    data = request.get_json()
    if data is None:
        abort(415, 'Expected json')
    return data
