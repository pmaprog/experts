from exproj.logic import posts as posts_logic
from exproj.db import *


def get_many():
    with get_session() as s:
        users = s.query(User).all()
        return [u.as_dict() for u in users]


def get(u_id):
    with get_session() as s:
        u = User.get_or_404(s, u_id)

        if u.id == current_user.id:
            pass  # todo

        return u.as_dict()


def update(u_id, new_data):
    with get_session() as s:
        u = User.get_or_404(s, u_id)

        if u_id != current_user.id and not current_user.has_access('moderator'):
            abort(403)

        for param, value in new_data.items():
            setattr(u, param, value)


# todo: offset, limit. Closed questions?
def get_posts(PostClass, u_id):
    with get_session() as s:
        User.get_or_404(s, u_id)  # check user is exists?

        if PostClass == Question:
            opened_questions = posts_logic.get_many(PostClass, u_id, False)
            closed_questions = posts_logic.get_many(PostClass, u_id, True)
            return opened_questions, closed_questions

        posts = posts_logic.get_many(PostClass, u_id)
        return posts
