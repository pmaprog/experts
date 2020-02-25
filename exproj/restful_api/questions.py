from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from . import *
from .. import questions_logic

bp = Blueprint('questions', __name__)  # todo: may be create prefix /questions?


@bp.route('/questions')
def get_questions():
    args = request.args
    offset = args.get('offset')
    limit = args.get('limit')
    questions = questions_logic.get_many(offset, limit)
    return make_ok(questions=questions)


@bp.route('/question', methods=['POST'])
@login_required
def create_question():
    data = get_json()
    q_id = questions_logic.create(current_user.id, data)
    return make_ok(f'Question #{q_id} successfully created'), 201


@bp.route('/question/<int:q_id>')
def get_question(q_id):
    question = questions_logic.get(q_id)
    return make_ok(question=question)


@bp.route('/question/<int:q_id>', methods=['DELETE'])
@login_required
def delete_question(q_id):
    questions_logic.delete(q_id)
    return make_ok(f'Question #{q_id} has been deleted')


@bp.route('/question/<int:q_id>', methods=['PUT'])
@login_required
def update_question(q_id):
    data = get_json()
    updated_question = questions_logic.update(q_id, data)
    return make_ok(f'Question #{q_id} has been updated', question=updated_question)


# todo
@bp.route('/question/<int:q_id>/increase-views')
def increase_question_views(q_id):
    questions_logic.increase_views(q_id)
    return make_ok(f'Successfully increased question #{q_id} views')


@bp.route('/question/<int:q_id>/toggle-upvote')
@login_required
def upvote_question(q_id):
    status = questions_logic.toggle_vote(current_user.id, q_id, 'up')
    if status == 'deleted':
        message = f'Successfully deleted vote for question #{q_id}'
    else:
        message = f'Successfully upvoted question #{q_id}'
    return make_ok(message)


@bp.route('/question/<int:q_id>/toggle-downvote')
@login_required
def downvote_question(q_id):
    status = questions_logic.toggle_vote(current_user.id, q_id, 'down')
    if status == 'deleted':
        message = f'Successfully deleted vote for question #{q_id}'
    else:
        message = f'Successfully downvoted question #{q_id}'
    return make_ok(message)


@bp.route('/question/<int:q_id>/answers')
def get_question_answers(q_id):
    answers = questions_logic.get_question_answers(q_id)
    return make_ok(answers=answers)


@bp.route('/question/<int:q_id>/answer', methods=['POST'])
def create_answer(q_id):
    data = get_json()
    text = data['text']
    answer = questions_logic.create_answer(q_id, current_user.id, text)
    return make_ok(f'Answer for the question #{q_id} has been created', answer=answer), 201
