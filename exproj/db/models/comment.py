from datetime import datetime

from sqlalchemy import (Column, Integer, String, ForeignKey, Table,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.orm import relationship, backref

from exproj.db import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    u_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    p_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    text = Column(String, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    status = Column(String, default='active', nullable=False)
    # last_edit_date
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
            'post_type': self.post.type,
            'email': self.author.email,
            'text': self.text if self.status == 'active' else None,
            'status': self.status,
            'creation_date': self.creation_date.timestamp(),
            'score': self.score,
        }


class DCommentVotes(Base):
    __tablename__ = 'd_comment_votes'

    u_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    c_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)
    upvoted = Column(Boolean, nullable=False)
