from flask import Blueprint, abort, request, jsonify, send_from_directory, send_file
from flask_login import login_required, current_user

from . import get_json, make_ok
from exproj import validation, config
from exproj.logic import users as users_logic, posts as posts_logic
from exproj.util import get_post_class
from exproj.validation import schemas

bp = Blueprint('users', __name__, url_prefix='/user')


@bp.route('/all')
def get_users():
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    users = users_logic.get_many(offset, limit)
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


@bp.route('/<int:u_id>/avatar')
def get_avatar(u_id):
    path = users_logic.get_avatar(u_id)
    return send_file('../' + path, as_attachment=True)

@bp.route('/<int:u_id>/avatar', methods=['PUT'])
@login_required
def update_avatar(u_id):
    if current_user.id != u_id or not current_user.has_access('moderator'):
        abort(403, 'You cant update avatar')

    file = request.files['file']

    users_logic.update_avatar(u_id, file)
    return make_ok('Avatar has been successfully updated')


@bp.route('/<int:u_id>/avatar', methods=['DELETE'])
@login_required
def delete_avatar(u_id):
    if current_user.id != u_id or not current_user.has_access('moderator'):
        abort(403, 'You cant delete avatar')

    users_logic.delete_avatar(u_id)
    return make_ok('Avatar has been successfully deleted')


@bp.route('/<int:u_id>/questions')
@bp.route('/<int:u_id>/articles')
@bp.route('/<int:u_id>/comments')
def get_user_posts(u_id):
    PostClass = get_post_class(request.path)

    closed = request.args.get('closed')
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    posts = posts_logic.get_many(PostClass, u_id, closed,
                                 offset=offset, limit=limit)
    return jsonify(posts)
