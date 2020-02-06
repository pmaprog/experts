from . import config
from .db import *
from . import util

from .exceptions import NotJsonError, NoData
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from datetime import datetime
import requests
import logging
import os
import nanoid


def register_user(mail, name, surname, password, lvl=2):
    with get_session() as s:
        user = s.query(User).filter(
                User.mail == mail,
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
            user = User(mail=mail, name=name,
                        surname=surname, password=password,
                        lvl=lvl, confirmation_link=confirmation_link)
            s.add(user)
        if config.DEFAULT_USER_STATUS == 'unconfirmed':
            util.send_email(mail, confirmation_link)
        logging.info('Registering new user [{}]'.format(mail))


def confirm_user(confirmation_link):
    with get_session() as s:
        user = s.query(User).filter(
                User.confirmation_link == confirmation_link,
                User.status == 'unconfirmed',
        ).one_or_none()
        if user:
            user.status = 'active'
            logging.info('User [{}] is confirmed'.format(user.mail))
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
