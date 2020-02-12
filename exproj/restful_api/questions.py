from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from . import *
from .. import questions_logic


bp = Blueprint('questions', __name__)


@bp.route('/questions', methods=['GET'])
def get_questions():
    args = request.args
    data = questions_logic.get_many(args.get('order'))
    return jsonify(data)


@bp.route('/questions', methods=['POST'])
@login_required
def create_question():
    attrs = request.json
    q_id = questions_logic.create(current_user.id, attrs['question'], attrs['desc'])
    return make_ok(f'Question with id #{q_id} successfully created'), 201


@bp.route('/questions/<int:id>')
@login_required
def get_question(id):
    data = questions_logic.get(id)
    return jsonify(data)


@bp.route('/questions/<int:id>', methods=['DELETE'])
@login_required
def delete_question(id):
    questions_logic.delete(id)
    return make_ok('Question with id {} was deleted'.format(id)), 204


# todo: change to PUT
@bp.route('/questions/<int:id>', methods=['PATCH'])
@login_required
def update_question(id):
    attrs = request.json
    questions_logic.update(id, attrs)
    new_id = attrs.get('id', id)
    updated_question = questions_logic.get(new_id)
    return make_ok('Question with id {} updated'.format(id), params=updated_question)
