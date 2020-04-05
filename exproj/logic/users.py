from os.path import join

from flask import abort
from flask_login import current_user

from . import slice, files
from exproj import config, logger
from exproj.db import get_session, User, Tag, Avatar


def get_many(offset=None, limit=None):
    with get_session() as s:
        query = s.query(User).order_by(User.registration_date.desc())

        data = slice(query, offset, limit)

        return [u.as_dict() for u in data]


def get(u_id):
    with get_session() as s:
        u = User.get_or_404(s, u_id)

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
                u.tags = s.query(Tag).filter(Tag.name.in_(value)).all()
            elif param == 'interests':
                u.interests = s.query(Tag).filter(Tag.name.in_(value)).all()
            else:
                setattr(u, param, value)


def get_avatar(u_id):
    with get_session() as s:
        u = User.get_or_404(s, u_id)

        if u.avatar is None:
            abort(404, 'Avatar not found')

        return join(config.avatars.DIRECTORY, f'avatar{u_id}.{u.avatar.ext}')


def update_avatar(u_id, file):
    with get_session() as s:
        u = User.get_or_404(s, u_id)
        if u.avatar:
            delete_avatar(u_id)

        ext = files.get_ext(file.filename)
        files.save(file, f'avatar{u_id}.{ext}', config.avatars)

        s.add(Avatar(u_id=u_id, ext=ext))


def delete_avatar(u_id):
    with get_session() as s:
        avatar = s.query(Avatar).filter_by(u_id=u_id).first()
        if avatar is None:
            abort(404, 'Avatar not found')

        s.delete(avatar)
        files.remove(f'avatar{u_id}.{avatar.ext}', config.avatars)
