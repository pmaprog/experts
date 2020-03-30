from flask import abort


def _slice(query, offset, limit):
    try:
        offset = int(offset)
        limit = int(limit)
    except:
        abort(422, 'query parameters'
                   ' `offset` and `limit` should be numbers')

    if offset < 0 or limit < 1:
        abort(422, 'query parameters'
                   ' `offset` or `limit` has wrong values')

    return query.slice(offset, offset + limit)
