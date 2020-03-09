from flask_login import current_user

from .db import *


def get_posts(PostClass, u_id):
    with get_session() as s:
        User.get_or_404(s, u_id)
        posts = [p.as_dict() for p in s.query(PostClass)
                 .filter(PostClass.u_id == u_id)
                 .order_by(PostClass.creation_date.desc()).all()]
        return posts


def make_expert(u_id):
    if current_user.access < USER_ACCESS['moderator']:
        abort(403)

    with get_session() as s:
        u = User.get_or_404(s, u_id)
        u.is_expert = True
