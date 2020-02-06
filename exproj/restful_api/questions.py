from flask import jsonify, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from . import *
from ..db import *
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

            q_id = questions_logic.create_question(current_user.id, args['question'], args['desc'])
            return make_ok('Created question with id #{}'.format(q_id))
        else:
            args = request.args
            data = questions_logic.get_questions(args.get('order'))
            return jsonify(data)
    except Exception as e:
        return make_400('Problem. {}'.format(e))


# @bp.route('/questions/<int:id>')
# def get_question(id):
#     return 'get question #' + str(id)
