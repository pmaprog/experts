from flask import Blueprint
from flask_login import login_required, current_user

from . import *
from exproj import validation
from exproj.logic import users as users_logic, posts as posts_logic
from exproj.util import get_post_class
from exproj.validation import schemas

bp = Blueprint('users', __name__, url_prefix='/user')


@bp.route('/all')
def get_users():
    users = users_logic.get_many()
    return jsonify(users)


@bp.route('/<int:u_id>')
def get_user(u_id):
    u = users_logic.get(u_id)
    return jsonify(u)


@bp.route('/<int:u_id>', methods=['PUT'])
@login_required
def update_user(u_id):
    data = get_json()
    schemas.user_update.validate(data)
    if 'tags' in data.keys():
        validation.validate_tags(data['tags'])
    if 'interests' in data.keys():
        validation.validate_tags(data['interests'])
    users_logic.update(u_id, data)
    return make_ok(f'User with id #{u_id} has been updated')


@bp.route('/<int:u_id>/questions')
@bp.route('/<int:u_id>/articles')
@bp.route('/<int:u_id>/comments')
def get_user_posts(u_id):
    PostClass = get_post_class(request.path)

    closed = request.args.get('closed')

    posts = posts_logic.get_many(PostClass, u_id, closed)
    return jsonify(posts)
