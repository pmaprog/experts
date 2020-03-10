from flask import Blueprint
from flask_login import current_user, login_required

from . import *
from ..util import get_post_class, routes
from .. import posts_logic

bp = Blueprint('posts', __name__)


@routes(bp, ['questions', 'articles'])
def get_posts():
    args = request.args
    offset = args.get('offset')
    limit = args.get('limit')
    closed = args.get('closed')
    PostClass = get_post_class(request.path)
    posts = posts_logic.get_many(PostClass, offset, limit, closed)
    return jsonify(posts)


@routes(bp, ['question', 'article'], methods=['POST'])
@login_required
def create_post():
    PostClass = get_post_class(request.path)
    data = get_json()
    p_id = posts_logic.create(PostClass, data)
    return make_ok(f'{PostClass.__name__} #{p_id} successfully created'), 201


@routes(bp, ['question', 'article'], '/<int:p_id>')
def get_post(p_id):
    PostClass = get_post_class(request.path)
    post = posts_logic.get(PostClass, p_id)
    return jsonify(post)


@routes(bp, ['question', 'article'], '/<int:p_id>', methods=['DELETE'])
@login_required
def delete_post(p_id):
    PostClass = get_post_class(request.path)
    posts_logic.delete(p_id)
    return make_ok(f'{PostClass.__name__} #{p_id} has been deleted')


@routes(bp, ['question', 'article'], '/<int:p_id>', methods=['PUT'])
@login_required
def update_post(p_id):
    PostClass = get_post_class(request.path)
    data = get_json()
    posts_logic.update(p_id, data)
    return make_ok(f'{PostClass.__name__} #{p_id} has been updated')


# todo
@routes(bp, ['question', 'article'], '/<int:p_id>/increase-views')
def increase_post_views(p_id):
    PostClass = get_post_class(request.path)
    posts_logic.increase_views(PostClass, p_id)
    return make_ok('Successfully increased '
                   f'{PostClass.__name__.lower()}\'s #{p_id} views')


@routes(bp, ['question', 'article', 'comment'], '/<int:p_id>/toggle-upvote')
@routes(bp, ['question', 'article', 'comment'], '/<int:p_id>/toggle-downvote')
@login_required
def vote_post(p_id):
    PostClass = get_post_class(request.path)
    action = ('up'
              if request.path[request.path.rfind('/') + 1:] == 'toggle-upvote'
              else 'down')
    result = posts_logic.toggle_vote(PostClass, p_id, action)
    if result == 'deleted':
        message = 'Successfully deleted vote '\
                  f'for {PostClass.__name__.lower()} #{p_id}'
    else:
        message = f'Successfully {action}voted '\
                  f'{PostClass.__name__.lower()} #{p_id}'
    return jsonify(message)


@routes(bp, ['question', 'article'], '/<int:p_id>/comments')
def get_post_comments(p_id):
    PostClass = get_post_class(request.path)
    comments = posts_logic.get_post_comments(PostClass, p_id)
    return jsonify(comments)


@routes(bp, ['question', 'article'], '/<int:p_id>/comment', methods=['POST'])
@login_required
def create_comment(p_id):
    PostClass = get_post_class(request.path)
    data = get_json()
    text = data['text']
    posts_logic.create_comment(PostClass, p_id, text)
    return make_ok(f'Comment for the {PostClass.__name__.lower()} '
                   f'#{p_id} has been created'), 201


@routes(bp, ['question', 'article'], '/<int:p_id>/domains', methods=['POST'])
def add_domains(p_id):
    PostClass = get_post_class(request.path)
    data = get_json()
    posts_logic.add_domains(PostClass, p_id, data)
    return make_ok('Successfully added '
                   f'domains to {PostClass.__name__.lower()}')


# @routes(bp, ['question', 'article'], '/<int:p_id>/domains',
# methods=['DELETE'])
# def delete_domains(p_id):
