from datetime import datetime

from .db import get_session
from .db import User, Question, Answer
from flask import abort
from werkzeug.exceptions import BadRequest

from schema import Schema, And, Optional


def get_many(offset=None, limit=None):
    with get_session() as s:
        query = s.query(Question).order_by(Question.create_time.desc())

        if offset and limit:
            try:
                offset = int(offset)
                limit = int(limit)
            except:
                raise BadRequest('offset and limit should be numbers')

            if offset < 0 or limit < 1:
                raise BadRequest('offset or limit has wrong values')

            data = query.slice(offset, offset + limit)
        else:
            data = query.all()

        questions = [q.as_dict() for q in data]
        return questions


def get(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)
        return q.as_dict()


def get_user_questions(user_id):
    with get_session() as s:
        return s.query(User).get(user_id).questions


def create(user_id, data):
    Schema({
        'title': And(str, lambda s: 20 < len(s) <= 128),
        'body': And(str, lambda s: 0 < len(s) <= 1024)
    }).validate(data)

    with get_session() as s:
        q = Question(user_id=user_id, title=data['title'], body=data['body'])
        s.add(q)
        s.commit()
        return q.id  # return created question's id


# todo: refactor this
def delete(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)
        for i in q.answers.all():
            s.delete(i)
        s.delete(q)


def update(q_id, new_data):
    Schema(And(lambda x: x != {}, {
        Optional('id'): And(int, lambda n: n > 0)
    })).validate(new_data)

    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)

        for attr, val in new_data.items():
            setattr(q, attr, val)

        return q


def get_question_answers(q_id):
    with get_session() as s:
        return s.query(Question).get(q_id).answers.all()


def create_new_answer(q_id, user_id, text):
    with get_session() as s:
        answer = Answer(user_id=user_id, q_id=q_id, text=text)
        s.add(answer)
