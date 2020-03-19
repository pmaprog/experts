"""
    Приставка d(ictonary) означает что объект имеет структуру словаря
"""

from datetime import datetime
import uuid

from flask_login import current_user, UserMixin
from sqlalchemy import (Column, Integer, String, ForeignKey, Table,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TEXT, ENUM, UUID
from sqlalchemy.orm import relationship, backref

from . import Base, get_session
from .. import config

USER_ACCESS = {
    'user':       0,
    'expert':     1,
    'moderator':  2,
    'admin':      3,
    'superadmin': 4
}

Account_status = ENUM('unconfirmed', 'active', 'deleted',
                      'banned', name='account_status')
Post_status = ENUM('active', 'deleted', 'archived', name='post_status')


class DPostVotes(Base):
    __tablename__ = 'd_post_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    p_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    upvoted = Column(Boolean, nullable=False)


class DCommentVotes(Base):
    __tablename__ = 'd_comment_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    c_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)
    upvoted = Column(Boolean, nullable=False)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


# class DPostTags(Base):
#     __tablename__ = 'd_post_tags'
#
#     p_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
#     t_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
#     # tag = relationship('Tag', lazy='joined')


# class DUserTags(Base):
#     __tablename__ = 'd_user_tags'
#
#     u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
#     t_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
#     # domain = relationship('Domain', lazy='joined')


post_tags = Table(
    'd_post_tags',
    Base.metadata,
    Column('p_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('t_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


user_tags = Table(
    'd_user_tags',
    Base.metadata,
    Column('u_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('t_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


user_interests = Table(
    'd_user_interests',
    Base.metadata,
    Column('u_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('t_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    cookie_id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                       unique=True, nullable=False)
    status = Column(Account_status, default=config.DEFAULT_USER_STATUS,
                    nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(TEXT, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmation_link = Column(String, nullable=False)
    access = Column(Integer, default=USER_ACCESS['user'], nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    question_count = Column(Integer, default=0, nullable=False)
    article_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    # secondary info
    position = Column(String, nullable=True)

    # todo: each function has lazy='dynamic'. doesn't look good
    posts = relationship('Post', lazy='dynamic')
    questions = relationship('Question', lazy='dynamic')
    articles = relationship('Article', lazy='dynamic')
    comments = relationship('Comment', lazy='dynamic')
    d_voted_posts = relationship('DPostVotes', lazy='dynamic')
    d_voted_comments = relationship('DCommentVotes', lazy='dynamic')
    tags = relationship('Tag', secondary=user_tags, lazy='dynamic')
    interests = relationship('Tag', secondary=user_interests, lazy='dynamic')
    # d_tags = relationship('DUserTags', lazy='dynamic')
    # d_interests = relationship('DUserInterests', lazy='dynamic')
    # certificates
    # warns

    def get_id(self):
        return self.cookie_id

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'role': [key for key, value in USER_ACCESS.items()
                     if value == self.access][0],
            'tags': [t.name for t in self.tags.all()],
            'interests': [t.name for t in self.interests.all()],
            'position': self.position,
            'rating': self.rating,
            'registration_date': self.registration_date.timestamp(),
            'question_count': self.question_count,
            'article_count': self.article_count,
            'comment_count': self.comment_count
        }

    def has_access(self, access):
        return self.access >= USER_ACCESS[access]

    # todo
    def can_answer(self, q):
        if q.u_id == self.id:
            return True

        if ((q.closed or q.only_experts_answer or q.only_chosen_tags) and
                not self.has_access('expert')):
            return False

        if (q.only_chosen_tags and
                len(set(self.tags.all()) & set(q.tags.all())) == 0):
            return False

        return True

    # def increment_count(self, cls):
    #     if cls == Question:
    #         self.question_count += 1
    #     if cls == Article:
    #         self.article_count += 1
    #     if cls == Comment:
    #         self.comment_count += 1


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(Post_status, default='active', nullable=False)
    # edit_date = Column(DateTime)
    # files

    author = relationship('User', lazy='joined')
    comments = relationship('Comment', lazy='dynamic')
    d_voted_users = relationship('DPostVotes', lazy='dynamic')
    tags = relationship('Tag', secondary=post_tags, lazy='dynamic')
    # d_domains = relationship('DPostDomains', lazy='dynamic')
    # edited_by = relationship('User', foreign_keys='')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'post'
    }

    def as_dict(self):
        return {
            'id': self.id,
            'u_id': self.u_id,
            'email': self.author.email,
            'title': self.title,
            'body': self.body,
            'creation_date': self.creation_date.timestamp(),
            'score': self.score,
            'view_count': self.view_count,
            'comment_count': self.comment_count,
            'tags': [t.name for t in self.tags.all()],
        }


class Question(Post):
    only_experts_answer = Column(Boolean, nullable=False)
    only_chosen_tags = Column(Boolean, nullable=False)
    closed = Column(Boolean, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'question'
    }


class Article(Post):
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    p_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    text = Column(String, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(String, default='active', nullable=False)
    # edit_time
    # visible

    # edited_by
    author = relationship('User', lazy='joined')
    post = relationship('Post', lazy='joined')
    d_voted_users = relationship('DCommentVotes', lazy='dynamic')

    def as_dict(self):
        return {
            'id': self.id,
            'p_id': self.p_id,
            'u_id': self.u_id,
            'email': self.author.email,
            'text': self.text,
            'creation_date': self.creation_date.timestamp(),
            'score': self.score,
        }
