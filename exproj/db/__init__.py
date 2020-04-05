from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from flask import abort

from exproj import config, logger


USER_ACCESS = {
    'guest':      0,
    'user':       1,
    'expert':     2,
    'moderator':  3,
    'admin':      4,
    'superadmin': 5
}

_engine = create_engine(config.DB_CONNECTION_STRING)
_Session = sessionmaker(bind=_engine, expire_on_commit=False)


class _Base:
    @classmethod
    def get_or_404(cls, s, id_):
        obj = s.query(cls).get(id_)
        if obj and (not hasattr(obj, 'status') or obj.status == 'active'):
            return obj
        abort(404, f'{cls.__name__} with id #{id_} not found')


Base = declarative_base(cls=_Base)


@contextmanager
def get_session():
    session = _Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


from .models import *


def create_tables(password):
    logger.info('Dropping existing tables')
    try:
        Base.metadata.reflect(_engine)
        Base.metadata.drop_all(_engine)
    except Exception as e:
        logger.info('Failed to drop tables.\n{}'.format(str(e)))
    logger.info('Creating tables')
    Base.metadata.create_all(_engine)
    logger.info('Tables was created')
    with get_session() as s:
        root = User(
            email=config.SUPER_ADMIN_MAIL,
            password=config.SUPER_ADMIN_PASSWORD,
            name='Name',
            surname='Surname',
            status='active',
            confirmation_link='none',
            access=USER_ACCESS['superadmin']
        )
        s.add(root)
    logger.info('Default user with mail [root_mail] was created')
