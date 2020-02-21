from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from schema import Schema

from . import *
from .. import questions_logic

bp = Blueprint('questions', __name__)


@bp.route('/questions')
def get_questions():
    args = request.args
    offset = args.get('offset')
    limit = args.get('limit')
    questions = questions_logic.get_many(offset, limit)
    return jsonify(questions)


@bp.route('/question', methods=['POST'])
@login_required
def create_question():
    data = request.get_json()
    q_id = questions_logic.create(current_user.id, data['question'], data['desc'])
    return make_ok(f'Question with id #{q_id} successfully created'), 201


@bp.route('/question/<int:q_id>')
@login_required
def get_question(q_id):
    question = questions_logic.get(q_id)
    return jsonify(question)


@bp.route('/question/<int:q_id>', methods=['DELETE'])
@login_required
def delete_question(q_id):
    questions_logic.delete(q_id)
    return make_ok('Question with id {} was deleted'.format(id)), 204


@bp.route('/question/<int:q_id>', methods=['PUT'])
@login_required
def update_question(q_id):
    data = request.get_json()
    new_id = questions_logic.update(q_id, data)
    updated_question = questions_logic.get(new_id)
    return make_ok('Question with id {} updated'.format(new_id), params=updated_question)
