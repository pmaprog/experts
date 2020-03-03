from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from .. import config, logger

_engine = create_engine(config.DB_CONNECTION_STRING)
_Session = scoped_session(sessionmaker(bind=_engine, expire_on_commit=False))
class _Base:
    query = _Session.query_property()

    @classmethod
    def get_or_404(cls, s, id_):
        # todo: check for deleted post, for active user
        p = s.query(cls).get(id_)
        if not p:
            abort(404, f'{cls.__name__} with id #{id_} not found')
        return p


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
            email='root_mail',
            password=password,
            name='Name',
            surname='Surname',
            lvl=0,
            status='active',
            confirmation_link='none',
        )
        s.add(root)
    logger.info('Default user with mail [root_mail] was created')


from .models import *
