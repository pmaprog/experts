from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from . import *
from ..util import get_post_class
from .. import posts_logic, comments_logic

bp = Blueprint('comments', __name__, url_prefix='/comment')


@bp.route('/<int:c_id>')
def get(c_id):
    comment = comments_logic.get(c_id)
    return make_ok(comment)


@bp.route('/<int:c_id>', methods=['PUT'])
def update(c_id):
    return jsonify(description='in development'), 405


@bp.route('/<int:c_id>', methods=['DELETE'])
def delete(c_id):
    comments_logic.delete(c_id)
    return make_ok(f'Comment #{c_id} has been deleted')
