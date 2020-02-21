from datetime import datetime
from schema import Schema, And

from .db import get_session
from .db import User, Question, Answer
from .exceptions import WrongDataError, QuestionNotFound


def get_many(offset=None, limit=None):
    with get_session() as s:
        query = s.query(Question).order_by(Question.create_time.desc())

        if offset and limit:
            try:
                offset = int(offset)
                limit = int(limit)
            except:
                raise WrongDataError('offset and limit should be numbers')

            if offset < 0 or limit < 1:
                raise WrongDataError('offset or limit has wrong values')

            data = query.slice(offset, offset + limit)
        else:
            data = query.all()

        questions = [q.as_dict() for q in data]
        return questions


def get(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            raise QuestionNotFound(q_id)
        return q.as_dict()


def get_user_questions(user_id):
    with get_session() as s:
        return s.query(User).get(user_id).questions


def create(user_id, question, desc):
    question = Question(
        user_id=user_id,
        question=question,
        desc=desc
    )
    with get_session() as s:
        s.add(question)
        return s.query(Question).order_by(Question.create_time.desc()).first().id


# todo: refactor this
def delete(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            raise QuestionNotFound(q_id)
        for i in q.answers.all():
            s.delete(i)
        s.delete(q)


def update(q_id, new_data):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            raise QuestionNotFound(q_id)

        for attr, val in new_data.items():
            if hasattr(q, attr):
                setattr(q, attr, val)

        # return current id
        return new_data.get('id', q.id)


def get_question_answers(q_id):
    with get_session() as s:
        return s.query(Question).get(q_id).answers.all()


def create_new_answer(q_id, user_id, text):
    with get_session() as s:
        answer = Answer(user_id=user_id, q_id=q_id, text=text)
        s.add(answer)
