from sqlalchemy import (Column, Integer, String, ForeignKey,
                        DateTime, Boolean, UniqueConstraint)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin

from datetime import datetime
import uuid
import bcrypt

from . import Base
from exproj import config


User_status = ENUM('unconfirmed', 'active', 'deleted', 'banned',
                   name='user_status')
Question_permissions = ENUM('all', 'experts', 'some_experts', name='permissions')


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    cookie_id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                       unique=True, nullable=False)
    lvl = Column(Integer, default=2, nullable=False)
    status = Column(User_status, default=config.DEFAULT_USER_STATUS, nullable=False)
    confirmation_link = Column(String, nullable=False)

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


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(String(128), nullable=False)
    desc = Column(String(1024), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    # edit_time = Column(DateTime)
    # warns
    # warn_by
    # domains
    # files

    votes = Column(Integer, default=0, nullable=False)
    voted_up = Column(Integer, ForeignKey('users.id'))
    voted_down = Column(Integer, ForeignKey('users.id'))
    perms = Column(Question_permissions, default='all', nullable=False)  # приватность (все, только эксперты, только эксперты выбранных областей)
    archived = Column(Boolean, default=False, nullable=False)

    author = relationship('User',
                          foreign_keys='Question.user_id',
                          backref=backref('questions', lazy='dynamic'))
    # edited_by = relationship('User',
    #                          foreign_keys='')

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['create_time'] = self.create_time.timestamp()
        d['answers'] = []
        for a in self.answers.all():
            d['answers'].append(a.as_dict())
        return d


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    q_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow(), nullable=False)
    text = Column(String, nullable=False)
    votes = Column(Integer, default=0, nullable=False)
    voted_up = Column(Integer, ForeignKey('users.id'))
    voted_down = Column(Integer, ForeignKey('users.id'))
    # warns
    # warn_by
    # edit_time
    # edited_by

    author = relationship('User',
                          foreign_keys='Answer.user_id',
                          backref=backref('answers', lazy='dynamic'))

    question = relationship('Question',
                            foreign_keys='Answer.q_id',
                            backref=backref('answers', lazy='dynamic'))

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['create_time'] = self.create_time.timestamp()
        return d
