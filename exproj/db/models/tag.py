from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref

from exproj.db import Base


d_post_tags = Table(
    'd_post_tags',
    Base.metadata,
    Column('p_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('t_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

d_user_tags = Table(
    'd_user_tags',
    Base.metadata,
    Column('u_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('t_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

d_user_interests = Table(
    'd_user_interests',
    Base.metadata,
    Column('u_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('t_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    users_interests = relationship('User', secondary=d_user_interests,
                                   lazy='dynamic')
    users_tags = relationship('User', secondary=d_user_tags, lazy='dynamic')
    posts = relationship('Post', secondary=d_post_tags, lazy='dynamic')
