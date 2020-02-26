from flask import Blueprint, jsonify, request, make_response, abort
from flask_login import (login_required, login_user, logout_user,
                         login_fresh, current_user)

import bcrypt

from . import *
from .. import auth, users_logic, posts_logic


bp = Blueprint('users', __name__)


@bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        abort(409, 'User is currently authenticated')

    data = get_json()
    user = auth.check_user(data['email'])
    if user:
        pw = str(data['password']).encode('utf-8')
        upw = str(user.password).encode('utf-8')
        if bcrypt.checkpw(pw, upw):
            login_user(user)
            return make_ok('User was logged in')
        else:
            abort(400, 'Invalid login or password')
    else:
        abort(400, 'Invalid login or password')


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return make_ok('User was logged out')


@bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        abort(409, 'User is currently authenticated')

    args = get_json()

    pw = bcrypt.hashpw(str(args['password']).encode('utf-8'),
                       bcrypt.gensalt())
    users_logic.register_user(args['email'], args['name'],
                              args['surname'], pw.decode('utf-8'))
    return make_ok('User was registered')


@bp.route('/confirm', methods=['POST'])
def confirm():
    args = get_json()
    users_logic.confirm_user(args['link'])
    return make_ok('User was confirmed')


# todo
@bp.route('/user/<int:u_id>/posts')
@bp.route('/user/<int:u_id>/questions')
@bp.route('/user/<int:u_id>/articles')
# @bp.route('/user/<int:u_id>/comments')
def get_user_posts(u_id):
    type = request.path[request.path.rfind('/') + 1:]
    posts = posts_logic.get_user_posts(u_id, type)
    return make_ok(posts=posts)
