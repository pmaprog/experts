from flask import abort
from flask_login import current_user, UserMixin
from sqlalchemy import (Column, Integer, String, ForeignKey, Table,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TEXT, ENUM, UUID
from sqlalchemy.orm import relationship, backref

from datetime import datetime
import uuid

from . import Base, get_session
from .. import config

USER_ACCESS = {
    'guest': 0,
    'user': 1,
    'expert': 2,
    'moderator': 3,
    'admin': 4,
    'superadmin': 5
}

Account_status = ENUM('unconfirmed', 'active', 'deleted', 'banned', name='account_status')
Post_status = ENUM('ok', 'deleted', name='post_status')
# Question_access = ENUM('all', 'experts', name='question_access')


class DPostVotes(Base):
    __tablename__ = 'd_post_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    p_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    is_upvoted = Column(Boolean, nullable=False)


class DCommentVotes(Base):
    __tablename__ = 'd_comment_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    c_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)
    is_upvoted = Column(Boolean, nullable=False)


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    cookie_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    account_status = Column(Account_status, default=config.DEFAULT_USER_STATUS, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(TEXT, nullable=False)
    confirmation_link = Column(String, nullable=False)
    position = Column(String, nullable=False)
    access = Column(Integer, default=USER_ACCESS['user'], nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    # is_expert = Column(String, default=False, nullable=False)
    # domains
    # warns
    question_count = Column(Integer, default=0, nullable=False)
    article_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)

    posts = relationship('Post', lazy='dynamic')
    questions = relationship('Question', lazy='dynamic')
    articles = relationship('Article', lazy='dynamic')
    comments = relationship('Comment', lazy='dynamic')
    voted_posts = relationship('DPostVotes', lazy='dynamic')
    voted_comments = relationship('DCommentVotes', lazy='dynamic')

    def get_id(self):
        return self.cookie_id

    # todo: rename this method and create another one
    def has_access(self, post):
        return post.u_id == current_user.id or self.access >= post.access


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(9), nullable=False)
    title = Column(String(128), nullable=False)
    body = Column(String(1024), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(Post_status, default='ok', nullable=False)
    # edit_time = Column(DateTime)
    # domains
    # files

    # edited_by = relationship('User', foreign_keys='')
    author = relationship('User', lazy='subquery')
    comments = relationship('Comment', lazy='dynamic')
    voted_users = relationship('DPostVotes')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'posts'
    }

    def as_dict(self):
        return {
            'id': self.id,
            'u_id': self.u_id,
            'email': self.author.email,
            'title': self.title,
            'body': self.body,
            'creation_date': self.creation_date.timestamp(),
            'view_count': self.view_count,
            'score': self.score,
            'comment_count': self.comment_count,
            'tags': ['todo']
        }


class Question(Post):
    access = Column(Integer, default=USER_ACCESS['guest'], nullable=False)

    # def __init__(self, *args, **kwargs):
    #     super(Question, self).__init__(*args, **kwargs)
    #     self.access = USER_ACCESS[kwargs.get('access')]

    # def has_access(self):
    #     return (self.author is current_user or
    #             current_user.access >= self.access)

    __mapper_args__ = {
        'polymorphic_identity': 'questions'
    }


class Article(Post):
    __mapper_args__ = {
        'polymorphic_identity': 'articles'
    }


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    p_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    text = Column(String, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(String, default='ok', nullable=False)
    # is_answer
    # edit_time
    # visible

    # edited_by
    author = relationship('User', lazy='subquery')
    post = relationship('Post', lazy='subquery')
    voted_users = relationship('DCommentVotes')

    def as_dict(self):
        return {
            'id': self.id,
            'u_id': self.u_id,
            'email': self.author.email,
            'text': self.text,
            'creation_date': self.creation_date.timestamp(),
            'score': self.score,
        }
