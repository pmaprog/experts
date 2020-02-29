from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from . import *
from ..util import get_post_class
from .. import posts_logic

bp = Blueprint('questions', __name__)


@bp.route('/questions')
@bp.route('/articles')
def get_posts():
    args = request.args
    offset = args.get('offset')
    limit = args.get('limit')
    PostClass = get_post_class(request.path)
    post_type = request.path[1:]
    posts = posts_logic.get_many(PostClass, offset, limit)
    return make_ok(**{post_type: posts})


@bp.route('/question', methods=['POST'])
@bp.route('/article', methods=['POST'])
@login_required
def create_post():
    PostClass = get_post_class(request.path)
    data = get_json()
    p_id = posts_logic.create(PostClass, current_user.id, data)
    return make_ok(f'{PostClass.name} #{p_id} successfully created'), 201


@bp.route('/question/<int:p_id>')
@bp.route('/article/<int:p_id>')
def get_post(p_id):
    PostClass = get_post_class(request.path)
    post = posts_logic.get(PostClass, p_id)
    return make_ok(post)


@bp.route('/question/<int:p_id>', methods=['DELETE'])
@bp.route('/article/<int:p_id>', methods=['DELETE'])
@login_required
def delete_post(p_id):
    PostClass = get_post_class(request.path)
    posts_logic.delete(p_id)
    return make_ok(f'{PostClass.name} #{p_id} has been deleted')


@bp.route('/question/<int:p_id>', methods=['PUT'])
@bp.route('/article/<int:p_id>', methods=['PUT'])
@login_required
def update_post(p_id):
    PostClass = get_post_class(request.path)
    data = get_json()
    updated_question = posts_logic.update(p_id, data)
    return make_ok(f'{PostClass.name} #{p_id} has been updated', question=updated_question)


# todo
@bp.route('/question/<int:p_id>/increase-views')
@bp.route('/article/<int:p_id>/increase-views')
def increase_post_views(p_id):
    PostClass = get_post_class(request.path)
    posts_logic.increase_views(PostClass, p_id)
    return make_ok(f'Successfully increased {PostClass.name.lower()}\'s #{p_id} views')


@bp.route('/question/<int:p_id>/toggle-upvote')
@bp.route('/question/<int:p_id>/toggle-downvote')
@bp.route('/article/<int:p_id>/toggle-upvote')
@bp.route('/article/<int:p_id>/toggle-downvote')
@login_required
def vote_post(p_id):
    PostClass = get_post_class(request.path)
    action = 'up' if request.path[request.path.rfind('/') + 1:] == 'toggle-upvote' else 'down'
    status = posts_logic.toggle_vote(PostClass, current_user.id, p_id, action)
    if status == 'deleted':
        message = f'Successfully deleted vote for {PostClass.name.lower()} #{p_id}'
    else:
        message = f'Successfully {action}voted {PostClass.name.lower()} #{p_id}'
    return make_ok(message)


@bp.route('/question/<int:p_id>/comments')
@bp.route('/article/<int:p_id>/comments')
def get_post_comments(p_id):
    PostClass = get_post_class(request.path)
    comments = posts_logic.get_post_comments(PostClass, p_id)
    return make_ok(comments=comments)


@bp.route('/question/<int:p_id>/comment', methods=['POST'])
@bp.route('/article/<int:p_id>/comment', methods=['POST'])
def create_comment(p_id):
    PostClass = get_post_class(request.path)
    data = get_json()
    text = data['text']
    comment = posts_logic.create_comment(PostClass, current_user.id, p_id, text)
    return make_ok(f'Comment for the {PostClass.name.lower()} #{p_id} has been created', comment=comment), 201
