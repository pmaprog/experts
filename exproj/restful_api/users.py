from werkzeug.exceptions import BadRequest
from flask import Blueprint, jsonify, request, make_response
from flask_login import (login_required, login_user, logout_user,
                         login_fresh, current_user)

import bcrypt

from . import *
from .. import auth, users_logic


bp = Blueprint('users', __name__)


@bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        raise BadRequest('User is currently authenticated')

    data = request.get_json()
    user = auth.check_user(data['mail'])
    if user:
        pw = str(data['password']).encode('utf-8')
        upw = str(user.password).encode('utf-8')
        if bcrypt.checkpw(pw, upw):
            login_user(user)
            return make_ok(200, 'User was logged in')
        else:
            raise BadRequest('Invalid login or password')
    else:
        raise BadRequest('Invalid login or password')


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return make_ok(200, 'User was logged out')


@bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        raise BadRequest('User is currently authenticated')

    args = request.get_json()

    pw = bcrypt.hashpw(str(args['password']).encode('utf-8'),
                       bcrypt.gensalt())
    users_logic.register_user(args['mail'], args['name'],
                              args['surname'], pw.decode('utf-8'))
    return make_ok(200, 'User was registered')


@bp.route('/confirm', methods=['POST'])
def confirm():
    args = request.get_json()
    users_logic.confirm_user(args['link'])
    return make_ok(200, 'User was confirmed')
