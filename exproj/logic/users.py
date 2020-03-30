from . import _slice
from exproj.db import *


def get_many(offset=None, limit=None):
    with get_session() as s:
        query = s.query(User).order_by(User.registration_date.desc())

        if offset and limit:
            data = _slice(query, offset, limit)
        else:
            data = query.all()

        return [u.as_dict() for u in data]


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
            if param == 'tags':
                if not current_user.has_access('moderator'):
                    abort(403, 'You cant change tags')
                u.tags = s.query(Tag).filter(Tag.id.in_(value)).all()
            elif param == 'interests':
                u.interests = s.query(Tag).filter(Tag.id.in_(value)).all()
            else:
                setattr(u, param, value)
