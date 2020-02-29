from flask import abort
from flask_login import UserMixin
from sqlalchemy import (Column, Integer, String, ForeignKey, Table,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TEXT, ENUM, UUID
from sqlalchemy.orm import relationship, backref

from datetime import datetime
import uuid
import bcrypt

from . import Base, get_session
from .. import config


User_status = ENUM('unconfirmed', 'active', 'deleted', 'banned',
                   name='user_status')
Question_access_levels = ENUM('all', 'experts', name='permissions')


class DPostVotes(Base):
    __tablename__ = 'd_post_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    p_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    is_upvoted = Column(Boolean, nullable=False)

    user = relationship('User', backref='voted_posts')
    post = relationship('Post', backref='voted_users')


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    password = Column(TEXT, nullable=False)
    cookie_id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                       unique=True, nullable=False)
    lvl = Column(Integer, default=2, nullable=False)
    status = Column(User_status, default=config.DEFAULT_USER_STATUS, nullable=False)
    confirmation_link = Column(String, nullable=False)
    # warns

    posts = relationship('Post', lazy='dynamic')
    questions = relationship('Question', lazy='dynamic')
    articles = relationship('Article', lazy='dynamic')
    comments = relationship('Comment', lazy='dynamic')

    def get_id(self):
        return self.cookie_id

    def change_password(self, old_password, new_password):
        opw = str(old_password).encode('utf-8')
        pw = str(self.password).encode('utf-8')
        if bcrypt.checkpw(opw, pw):
            npw = bcrypt.hashpw(str(new_password).encode('utf-8'),
                                bcrypt.gensalt())
            self.password = npw.decode('utf-8')
            return 1
        else:
            return 0

    @property
    def full_name(self):
        return self.name + ' ' + self.surname


class Post(Base):
    __tablename__ = 'posts'
    name = 'Post'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(9), nullable=False)
    title = Column(String(128), nullable=False)
    body = Column(String(1024), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    status = Column(String, default='ok', nullable=False)
    # edit_time = Column(DateTime)
    # domains
    # files

    # edited_by = relationship('User', foreign_keys='')
    author = relationship('User', lazy='subquery')
    comments = relationship('Comment', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'posts'
    }

    def as_dict(self):
        d = {
            'id': self.id,
            'u_id': self.u_id,
            'email': self.author.email,
            'title': self.title,
            'body': self.body,
            'create_time': self.create_time.timestamp(),
            'views_count': self.views_count,
            'rating': self.rating,
            'comments_count': 'todo',
            'tags': 'todo'
        }
        return d


class Question(Post):
    name = 'Question'
    access = Column(Question_access_levels, default='all')

    __mapper_args__ = {
        'polymorphic_identity': 'questions'
    }


class Article(Post):
    name = 'Article'
    __mapper_args__ = {
        'polymorphic_identity': 'articles'
    }


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    p_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow(), nullable=False)
    text = Column(String, nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    status = Column(String, default='ok', nullable=False)
    # edit_time
    # visible

    # edited_by
    author = relationship('User')  # foreign_keys='Comment.u_id'
    post = relationship('Post')  # foreign_keys='Comment.p_id'

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['create_time'] = self.create_time.timestamp()
        d['email'] = self.author.email
        return d
