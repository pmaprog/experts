from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from sqlalchemy.exc import IntegrityError

from . import *
from ..exceptions import QuestionNotFound
from .. import questions_logic


bp = Blueprint('questions', __name__)


@bp.route('/questions', methods=['GET', 'POST'])
@login_required
def questions():
    try:
        if request.method == 'POST':
            args = request.json
            if not args:
                return make_400('Expected json')

            q_id = questions_logic.create(current_user.id, args['question'], args['desc'])
            return make_ok('Created question with id #{}'.format(q_id))

        # GET
        args = request.args
        data = questions_logic.get_all(args.get('order'))
        return jsonify(data)
    except Exception as e:
        return make_400('Problem. {}'.format(e))


@bp.route('/questions/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def question(id):
    try:
        if request.method == 'PATCH':
            attrs = request.json
            if not attrs:
                return make_400('Expected json')
            questions_logic.update(id, attrs)
            new_id = attrs.get('id', id)
            updated_question = questions_logic.get(new_id)
            return make_ok('Question with id {} updated'.format(id), params=updated_question)
        elif request.method == 'DELETE':
            questions_logic.delete(id)
            return make_ok('Question with id {} was deleted'.format(id))

        # GET
        data = questions_logic.get(id)
        return jsonify(data)
    except IntegrityError:
        return make_400('Id {} already exists!'.format(attrs['id']))
    except QuestionNotFound as e:
        return make_400('Question with id {} not found!'.format(e.id))
    except Exception as e:
        return make_400('Problem. {}'.format(e))
