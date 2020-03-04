from .db import User, get_session


def user_loader(user_id):
    with get_session() as s:
        return s.query(User).filter(
                User.cookie_id == user_id,
                User.account_status == 'active'
        ).one_or_none()


def check_user(email):
    with get_session() as s:
        return s.query(User).filter(
                User.email == email,
                User.account_status == 'active'
        ).one_or_none()
