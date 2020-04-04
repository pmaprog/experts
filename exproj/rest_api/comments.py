from flask import Blueprint

from . import *
from exproj.logic import comments as comments_logic

bp = Blueprint('comments', __name__, url_prefix='/comment')


@bp.route('/<int:c_id>')
def get_comment(c_id):
    comment = comments_logic.get(c_id)
    return jsonify(comment)


@bp.route('/<int:c_id>', methods=['PUT'])
def update_comment(c_id):
    text = request.args.get('text')
    comments_logic.update(c_id, text)
    return make_ok(f'Successfully updated comment #{c_id} text')


@bp.route('/<int:c_id>', methods=['DELETE'])
def delete_comment(c_id):
    comments_logic.delete(c_id)
    return make_ok(f'Comment #{c_id} has been deleted')
