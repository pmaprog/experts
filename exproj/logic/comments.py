from flask import abort
from flask_login import current_user

from exproj import logger
from exproj.db import get_session
from exproj.db import User, Post, Question, Article, Comment


def get(c_id):
    with get_session() as s:
        comment = Comment.get_or_404(s, c_id)

        if (isinstance(comment.post, Question) and comment.post.closed
                and not current_user.has_access('expert')
                and comment.post.u_id != current_user.id):
            abort(403)

        return comment.as_dict()


def update(c_id, text):
    with get_session() as s:
        comment = Comment.get_or_404(s, c_id)

        if (isinstance(comment.post, Question) and comment.post.closed
                and not current_user.has_access('moderator')
                and comment.post.u_id != current_user.id):
            abort(403)

        comment.text = text


def delete(c_id):
    with get_session() as s:
        comment = Comment.get_or_404(s, c_id)

        if (not current_user.has_access('moderator')
                and comment.u_id != current_user.id):
            abort(403)

        comment.post.comment_count -= 1
        comment.author.comment_count -= 1
        comment.status = 'deleted'
