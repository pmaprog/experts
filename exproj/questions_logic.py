from datetime import datetime
from contextlib import suppress

from .db import get_session
from .db import User, Question, Answer, DQuestionVotes
from flask import abort

from schema import Schema, And, Optional, Use


def get_many(offset=None, limit=None):
    with get_session() as s:
        query = s.query(Question).order_by(Question.create_time.desc())

        if offset and limit:
            try:
                offset = int(offset)
                limit = int(limit)
            except:
                abort(422, 'offset and limit should be numbers')

            if offset < 0 or limit < 1:
                abort(422, 'offset or limit has wrong values')

            data = query.slice(offset, offset + limit)
        else:
            data = query.all()

        questions = [q.as_dict() for q in data]
        return questions


def get(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404, f'Question with id #{q_id} not found')
        return q.as_dict()


def get_user_questions(u_id):
    with get_session() as s:
        return s.query(User).get(u_id).questions


def create(u_id, data):
    Schema({
        'title': And(str, And(lambda s: 20 < len(s) <= 128, error='from 20 to 128')),
        'body': And(str, lambda s: 0 < len(s) <= 1024)
    }).validate(data)

    with get_session() as s:
        q = Question(u_id=u_id, title=data['title'], body=data['body'])
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
        Optional('id'): And(int, lambda n: n > 0),
        Optional('title'): And(str, lambda s: 20 < len(s) <= 128),
        Optional('body'): And(str, lambda s: 0 < len(s) <= 1024),
    })).validate(new_data)

    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)

        for attr, val in new_data.items():
            setattr(q, attr, val)

        return q.as_dict()


def increase_views(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)
        q.views += 1


def toggle_vote(u_id, q_id, action):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)

        cur_vote = s.query(DQuestionVotes).get((u_id, q_id))
        new_vote = DQuestionVotes(u_id=u_id, q_id=q_id)
        if action == 'up':
            if cur_vote:
                if cur_vote.is_upvoted:
                    s.delete(cur_vote)
                    q.rating -= 1
                    return 'deleted'
                else:
                    q.rating += 2
                    cur_vote.is_upvoted = True
            else:
                q.rating += 1
                new_vote.is_upvoted = True
                s.add(new_vote)
            return 'up'
        elif action == 'down':
            if cur_vote:
                if not cur_vote.is_upvoted:
                    s.delete(cur_vote)
                    q.rating += 1
                    return 'deleted'
                else:
                    q.rating -= 2
                    cur_vote.is_upvoted = False
            else:
                q.rating -= 1
                new_vote.is_upvoted = False
                s.add(new_vote)
            return 'down'
        else:
            raise ValueError('Action should be only `up` or `down`')


def get_question_answers(q_id):
    with get_session() as s:
        q = s.query(Question).get(q_id)
        if q is None:
            abort(404)
        answers = [a.as_dict() for a in q.answers.all()]
        return answers


def create_answer(q_id, u_id, text):
    with get_session() as s:
        answer = Answer(u_id=u_id, q_id=q_id, text=text)
        s.add(answer)
        s.commit()
        return answer.as_dict()


def get_answer(a_id):
    with get_session() as s:
        answer = s.query(Answer).get(a_id)
        if answer is None:
            abort(404, f'Answer #{a_id} not found')
        return answer
