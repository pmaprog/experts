from flask import jsonify, request, abort


def make_ok(description: str):
    return jsonify({
        'description': description
    })


def get_json():
    data = request.get_json()
    if data is None:
        abort(415, 'Expected json')
    return data
