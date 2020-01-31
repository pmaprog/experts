from . import cfg
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
            user.status = cfg.DEFAULT_USER_STATUS
            user.confirmation_link = confirmation_link
            user.lvl = lvl
        else:
            user = User(mail=mail, name=name,
                        surname=surname, password=password,
                        lvl=lvl, confirmation_link=confirmation_link)
            s.add(user)
        if cfg.DEFAULT_USER_STATUS == 'unconfirmed':
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


def get_user_stat(user_id):
    result_creator = {}
    result_presenter = {}
    result_participant = {}
    with get_session() as s:
        as_creator = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_role == 'creator'
        ).all()

        for participant, event in as_creator:
            result_creator[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

        as_presenter = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_role == 'presenter'
        ).all()

        for participant, event in as_presenter:
            result_presenter[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

        as_participant = s.query(Participation, Event).filter(
                Participation.event == Event.id,
                Participation.participant == user_id,
                Participation.participation_role == 'participant'
        ).all()

        for participant, event in as_participant:
            result_participant[event.id] = {
                'id': event.id,
                'name': event.name,
                'date': event.date_time,
            }

    return result_creator, result_presenter, result_participant
