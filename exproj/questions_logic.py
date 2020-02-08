from datetime import datetime

from .db import get_session
from .db import User, Question, Answer
from .exceptions import QuestionNotFound


def get_all(order=None):
    with get_session() as s:
        query = s.query(Question)
        if order == 'desc':
            query = query.order_by(Question.create_time.desc())
        questions = [q.as_dict() for q in query.all()]
        return questions


def get(id):
    with get_session() as s:
        q = s.query(Question).get(id)
        if q is None:
            raise QuestionNotFound(id)
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
        return s.query(Question).order_by(-Question.id).first().id


# refactor this
def delete(id):
    with get_session() as s:
        q = s.query(Question).get(id)
        if q is None:
            raise QuestionNotFound(id)
        for i in q.answers.all():
            s.delete(i)
        s.delete(q)


def update(id, attrs):
    with get_session() as s:
        q = s.query(Question).get(id)
        if q is None:
            raise QuestionNotFound(id)

        for attr, val in attrs.items():
            if hasattr(q, attr):
                setattr(q, attr, val)

        s.add(q)


def get_question_answers(id):
    with get_session() as s:
        return s.query(Question).get(id).answers.all()


def post_new_answer(q_id, user_id, text):
    with get_session() as s:
        answer = Answer(user_id=user_id, q_id=q_id, text=text)
        s.add(answer)
