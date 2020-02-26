from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy

from . import *
from .. import posts_logic

bp = Blueprint('questions', __name__)  # todo: may be create prefix /questions?


@bp.route('/posts')
def get_posts():
    args = request.args
    type = args.get('type')
    if type not in ['questions', 'articles']:
        abort(422, '')
    offset = args.get('offset')
    limit = args.get('limit')
    questions = posts_logic.get_many(offset, limit)
    return make_ok(questions=questions)


@bp.route('/post', methods=['POST'])
@login_required
def create_post():
    data = get_json()
    p_id = posts_logic.create(current_user.id, data)
    return make_ok(f'Question #{p_id} successfully created'), 201


@bp.route('/question/<int:p_id>')
@bp.route('/article/<int:p_id>')
def get_question(p_id):
    question = posts_logic.get(p_id)
    return make_ok(question=question)


@bp.route('/question/<int:p_id>', methods=['DELETE'])
@bp.route('/article/<int:p_id>', methods=['DELETE'])
@login_required
def delete_question(p_id):
    posts_logic.delete(p_id)
    return make_ok(f'Question #{p_id} has been deleted')


@bp.route('/question/<int:p_id>', methods=['PUT'])
@bp.route('/article/<int:p_id>', methods=['PUT'])
@login_required
def update_question(p_id):
    data = get_json()
    updated_question = posts_logic.update(p_id, data)
    return make_ok(f'Question #{p_id} has been updated', question=updated_question)


# todo
@bp.route('/post/<int:p_id>/increase-views')
def increase_question_views(p_id):
    posts_logic.increase_views(p_id)
    return make_ok(f'Successfully increased question #{p_id} views')


@bp.route('/question/<int:p_id>/toggle-upvote')
@bp.route('/question/<int:p_id>/toggle-downvote')
@bp.route('/article/<int:p_id>/toggle-upvote')
@bp.route('/article/<int:p_id>/toggle-downvote')
@login_required
def vote_question(p_id):
    action = 'up' if request.path[request.path.rfind('/') + 1:] == 'toggle-upvote' else 'down'
    status = posts_logic.toggle_vote(current_user.id, p_id, action)
    if status == 'deleted':
        message = f'Successfully deleted vote for question #{p_id}'
    else:
        message = f'Successfully {action}voted question #{p_id}'
    return make_ok(message)


@bp.route('/question/<int:p_id>/comments')
def get_question_answers(p_id):
    answers = posts_logic.get_question_answers(p_id)
    return make_ok(answers=answers)


@bp.route('/question/<int:p_id>/comment', methods=['POST'])
def create_answer(p_id):
    data = get_json()
    text = data['text']
    answer = posts_logic.create_answer(p_id, current_user.id, text)
    return make_ok(f'Answer for the question #{p_id} has been created', answer=answer), 201
