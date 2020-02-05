import json

from flask import jsonify, request, redirect, url_for

from . import app
from .db import *
from . import questions_logic


@app.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'POST':
        return 'create question'
    else:
        return 'get all questions'


@app.route('/questions/<int:id>')
def get_question(id):
    return 'get question #' + str(id)
