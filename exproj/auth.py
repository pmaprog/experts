from .db import User, get_session
from passlib.hash import sha256_crypt


def user_loader(user_id):
    with get_session() as s:
        return s.query(User).filter(
                User.cookie_id == user_id
        ).one_or_none()


def check_user(mail):
    with get_session() as s:
        return s.query(User).filter(
                User.mail == mail,
                User.status == 'active'
        ).one_or_none()
