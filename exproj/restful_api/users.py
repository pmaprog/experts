from flask import Blueprint

from . import *
from .. import users_logic, posts_logic
from ..util import get_post_class


bp = Blueprint('users', __name__)


# todo
@bp.route('/user/<int:u_id>/questions')
@bp.route('/user/<int:u_id>/articles')
@bp.route('/user/<int:u_id>/comments')
def get_user_posts(u_id):
    PostClass = get_post_class(request.path)
    posts = users_logic.get_posts(PostClass, u_id)
    return jsonify(posts)
