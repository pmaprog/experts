from datetime import datetime

from sqlalchemy import (Column, Integer, String, ForeignKey, Table,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TEXT, ENUM, UUID
from sqlalchemy.orm import relationship, backref

from exproj.db import Base
from exproj.db.models.tag import d_post_tags


Post_status = ENUM('active', 'deleted', 'archived', name='post_status')


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
    # last_edit_date = Column(DateTime)
    # files

    author = relationship('User', lazy='joined')
    comments = relationship('Comment', lazy='dynamic')
    d_voted_users = relationship('DPostVotes', lazy='dynamic')
    tags = relationship('Tag', secondary=d_post_tags, lazy='dynamic')
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
            'status': self.status,
            'score': self.score,
            'view_count': self.view_count,
            'comment_count': self.comment_count,
            'tags': [t.name for t in self.tags.all()],
        }


class Question(Post):
    closed = Column(Boolean)
    only_experts_answer = Column(Boolean)
    only_chosen_tags = Column(Boolean)

    __mapper_args__ = {
        'polymorphic_identity': 'question'
    }

    def as_dict(self):
        d = super().as_dict()
        d.update({
            'closed': self.closed,
            'only_experts_answer': self.only_experts_answer,
            'only_chosen_tags': self.only_chosen_tags
        })
        return d


class Article(Post):
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }


class DPostVotes(Base):
    __tablename__ = 'd_post_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    p_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    upvoted = Column(Boolean, nullable=False)
