import os
from os.path import join, exists
from shutil import move
from contextlib import suppress

from flask import abort
from flask_login import current_user

from . import slice
from exproj import logger
from exproj.db import get_session, User, Tag, Avatar
from exproj import config
from exproj.config import avatars


def get_many(offset=None, limit=None):
    with get_session() as s:
        query = s.query(User).order_by(User.registration_date.desc())

        data = slice(query, offset, limit)

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

        ext = file.filename.rsplit('.', 1)[1].lower()

        if ext not in avatars.ALLOWED_EXTENSIONS:
            abort(422, 'Unsupported file extension')
        if file.mimetype not in avatars.ALLOWED_MIME_TYPES:
            abort(422, 'Unsupported mime type')

        # Не будет работать, пока Chrome и Firefox не перестанут
        # ставить Content-Length равным 0 ¯\_(ツ)_/¯
        if file.content_length > avatars.MAX_SIZE:
            abort(422, 'File size too large')

        filename = f'avatar{u_id}.{ext}'
        tmp_path = join(config.FILE_UPLOADS.TEMP_FOLDER, filename)
        file.save(tmp_path)
        size = os.stat(tmp_path).st_size
        logger.debug('File size is {}'.format(size))
        if size > avatars.MAX_SIZE:
            os.remove(tmp_path)
            abort(422, 'File size too large')
        new_path = join(avatars.DIRECTORY, filename)
        move(tmp_path, new_path)

        s.add(Avatar(u_id=u_id, ext=ext))


def delete_avatar(u_id):
    with get_session() as s:
        avatar = s.query(Avatar).filter_by(u_id=u_id).first()
        if avatar is None:
            abort(404, 'Avatar not found')

        s.delete(avatar)

        path = join(avatars.DIRECTORY, f'avatar{u_id}.{avatar.ext}')
        with suppress():  # ignore exceptions (file not found)
            os.remove(path)
