from sqlalchemy import (Column, Integer, String, ForeignKey,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship, backref

from datetime import datetime

from exproj.db import Base, get_session


Permissions = ENUM('all', 'experts', 'some_experts', name='permissions')


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(String(128), nullable=False)
    desc = Column(String(1024), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    # edit_time
    # edited_by
    # warns
    # areas
    # files

    # change to votes
    voices = Column(Integer, default=0, nullable=False)
    voted_up = Column(Integer, ForeignKey('users.id'))
    voted_down = Column(Integer, ForeignKey('users.id'))
    perms = Column(Permissions, default='all', nullable=False)  # приватность (все, только эксперты, только эксперты выбранных областей)
    archived = Column(Boolean, default=False, nullable=False)

    author = relationship('User',
                          foreign_keys='Question.user_id',
                          backref=backref('questions', lazy='dynamic'))

    def get_author_name(self):
        return '{} {}'.format(self.author.name, self.author.surname)

    def get_desc(self):
        lines = self.desc.split('\n')
        desc = ''.join(['<br>' + i for i in lines])
        return '<p>{}</p>'.format(desc)


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    q_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow(), nullable=False)
    text = Column(String, nullable=False)
    voices = Column(Integer, default=0, nullable=False)
    voted_up = Column(Integer, ForeignKey('users.id'))
    voted_down = Column(Integer, ForeignKey('users.id'))
    # edit_time
    # edited_by

    author = relationship('User',
                          foreign_keys='Answer.user_id',
                          backref=backref('answers', lazy='dynamic'))

    question = relationship('Question',
                            foreign_keys='Answer.q_id',
                            backref=backref('answers', lazy='dynamic'))
