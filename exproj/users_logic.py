from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from datetime import datetime
import requests
import logging
import os
import nanoid

from .db import *
from . import util
from . import logger


def register_user(email, name, surname, password, lvl=2):
    with get_session() as s:
        user = s.query(User).filter(
                User.email == email,
                User.status == 'deleted',
        ).one_or_none()

        # checking unique link
        confirmation_link = ''
        while True:
            confirmation_link = nanoid.generate(size=50)
            exists = s.query(User).filter(
                    User.confirmation_link == confirmation_link
            ).one_or_none()
            if not exists:
                break

        if user:
            user.status = config.DEFAULT_USER_STATUS
            user.confirmation_link = confirmation_link
            user.lvl = lvl
        else:
            user = User(email=email, name=name,
                        surname=surname, password=password,
                        lvl=lvl, confirmation_link=confirmation_link)
            s.add(user)
        if config.DEFAULT_USER_STATUS == 'unconfirmed':
            util.send_email(email, confirmation_link)
        logger.info('Registering new user [{}]'.format(email))


def confirm_user(confirmation_link):
    with get_session() as s:
        user = s.query(User).filter(
                User.confirmation_link == confirmation_link,
                User.status == 'unconfirmed',
        ).one_or_none()
        if user:
            user.status = 'active'
            logger.info('User [{}] is confirmed'.format(user.email))
            return 'user confirmed'
        else:
            return 'user is currently confirmed by this link'


def update_profile(id, args):
    with get_session() as s:
        user = s.query(User).filter(
            User.id == id,
            User.status == 'active',
            ).one_or_none()

        for arg, val in args.items():
            if hasattr(user, arg):
                setattr(user, arg, val)
            else:
                raise KeyError(arg)


def posts(u_id, type):
    with get_session() as s:
        u = s.query(User).get(u_id)
        if u is None:
            abort(404)
        posts = [p.as_dict() for p in getattr(u, type).order_by(Post.create_time.desc()).all()]
        return posts
