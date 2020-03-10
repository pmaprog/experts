from datetime import datetime
import uuid

from flask_login import current_user, UserMixin
from sqlalchemy import (Column, Integer, String, ForeignKey, Table,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TEXT, ENUM, UUID
from sqlalchemy.orm import relationship, backref

from schema import Schema, And, Optional, Use

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
Post_status = ENUM('active', 'deleted', name='post_status')


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


class DUserDomains(Base):
    __tablename__ = 'd_user_domains'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    d_id = Column(Integer, ForeignKey('domains.id'), primary_key=True)


class DPostDomains(Base):
    __tablename__ = 'd_post_domains'

    p_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    d_id = Column(Integer, ForeignKey('domains.id'), primary_key=True)
    sub = Column(Boolean, default=False, nullable=False)
    imaginary = Column(Boolean, default=False, nullable=False)


# todo: may be change to table? it is not necessary to create whole class
class DUserInterests(Base):
    __tablename__ = 'd_user_interests'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    d_id = Column(Integer, ForeignKey('domains.id'), primary_key=True)


class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey('domains.id'))
    name = Column(String, nullable=False)  # todo: unique?


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
    confirmation_link = Column(String, nullable=False)
    position = Column(String, nullable=False)
    access = Column(Integer, default=USER_ACCESS['user'], nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    question_count = Column(Integer, default=0, nullable=False)
    article_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)

    # todo: each function has lazy='dynamic'. doesn't look good
    posts = relationship('Post', lazy='dynamic')
    questions = relationship('Question', lazy='dynamic')
    articles = relationship('Article', lazy='dynamic')
    comments = relationship('Comment', lazy='dynamic')
    voted_posts = relationship('DPostVotes', lazy='dynamic')
    voted_comments = relationship('DCommentVotes', lazy='dynamic')
    domains = relationship('DUserDomains', lazy='dynamic')
    interests = relationship('DUserInterests', lazy='dynamic')
    # certificates
    # warns

    registration_schema = Schema({
        'name': str,
        'surname': str,
        'password': str,
        'email': str,
        'position': str,
    })
    update_schema = Schema(And(
        lambda x: x != {},
        {
            Optional('name'): str,
            Optional('surname'): str,
            Optional('email'): str,
            Optional('position'): str
        }
    ))

    def get_id(self):
        return self.cookie_id

    def as_dict(self):
        return {
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'role': [key for key, value in USER_ACCESS.items()
                     if value == self.access][0],
            'position': self.position,
            'rating': self.rating,
            'question_count': self.question_count,
            'article_count': self.article_count,
            'comment_count': self.comment_count
        }

    def has_access(self, access):
        return self.access >= USER_ACCESS[access]

    def can_answer(self, q):
        if q.u_id == self.id:
            return True

        if ((q.closed or q.only_experts_answer or q.only_chosen_domains) and
                not self.has_access('expert')):
            return False

        if (q.only_chosen_domains and
                 len(set([i.d_id for i in self.domains.all()]) &
                     set([i.d_id for i in q.domains.all()])) == 0):
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

    author = relationship('User', lazy='subquery')
    comments = relationship('Comment', lazy='dynamic')
    voted_users = relationship('DPostVotes', lazy='dynamic')
    domains = relationship('DPostDomains', lazy='dynamic')
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
            'view_count': self.view_count,
            'score': self.score,
            'comment_count': self.comment_count,
            'domains': [d.d_id for d in self.domains
                .filter(DPostDomains.sub == False).all()],
            'subdomains': [subd.d_id for subd in self.domains
                .filter(DPostDomains.sub == True,
                        Domain.parent.isnot(None)).all()]
        }


class Question(Post):
    only_experts_answer = Column(Boolean, nullable=False)
    only_chosen_domains = Column(Boolean, nullable=False)
    closed = Column(Boolean, nullable=False)

    schema = Schema({
        'title': And(str, lambda s: 20 < len(s) <= 128),
        'body': And(str, lambda s: 0 < len(s) <= 1024),
        'only_experts_answer': bool,
        'only_chosen_domains': bool,
        'closed': bool
    })

    __mapper_args__ = {
        'polymorphic_identity': 'question'
    }


class Article(Post):
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }

    schema = Schema({
        'title': And(str, lambda s: 20 < len(s) <= 128),
        'body': And(str, lambda s: 0 < len(s) <= 1024)
    })


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
    author = relationship('User', lazy='subquery')
    post = relationship('Post', lazy='subquery')
    voted_users = relationship('DCommentVotes', lazy='dynamic')

    # schema = Schema({
    #     'text': And(str, lambda s: 20 < len(s) <= 250),
    # })

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
