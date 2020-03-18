from flask import abort
from flask_login import current_user
from sqlalchemy import or_
from schema import Schema, And, Optional, Use

from exproj import logger
from exproj.db import get_session, USER_ACCESS
from exproj.db import User, Post, Question, Article, Comment, DPostVotes


def get(c_id):
    with get_session() as s:
        comment = Comment.get_or_404(s, c_id)
        return comment.as_dict()


def update(c_id):
    pass


def delete(c_id):
    with get_session() as s:
        c = Comment.get_or_404(s, c_id)
        if (current_user.access < USER_ACCESS['moderator'] and
                c.u_id != current_user.id):
            abort(403)
        c.status = 'deleted'
        c.post.comment_count -= 1
        current_user.comment_count -= 1
