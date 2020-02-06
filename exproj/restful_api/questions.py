from flask import jsonify, request, redirect, url_for, Blueprint

from . import *
from ..db import *
from .. import questions_logic


bp = Blueprint('questions', __name__)


@bp.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'POST':
        return 'create question'
    else:
        return 'get all questions'


# @bp.route('/questions/<int:id>')
# def get_question(id):
#     return 'get question #' + str(id)
