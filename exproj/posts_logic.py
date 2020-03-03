from datetime import datetime
from contextlib import suppress

from .db import get_session
from .db import User, Post, Question, Article, Comment, DPostVotes
from flask import abort

from schema import Schema, And, Optional, Use


def get_many(PostClass, offset=None, limit=None):
    with get_session() as s:
        query = s.query(PostClass).order_by(PostClass.creation_date.desc())

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

        posts = [p.as_dict() for p in data]
        return posts


def get(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        return p.as_dict()


def create(PostClass, u_id, data):
    Schema({
        'title': And(str, And(lambda s: 20 < len(s) <= 128, error='from 20 to 128')),
        'body': And(str, lambda s: 0 < len(s) <= 1024)
    }).validate(data)

    with get_session() as s:
        p = PostClass(u_id=u_id, title=data['title'], body=data['body'])
        s.add(p)
        s.commit()
        return p.id  # return created question's id


def delete(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        p.status = 'deleted'


def update(PostClass, p_id, new_data):
    Schema(And(lambda x: x != {}, {
        Optional('id'): And(int, lambda n: n > 0),
        Optional('title'): And(str, lambda s: 20 < len(s) <= 128),
        Optional('body'): And(str, lambda s: 0 < len(s) <= 1024),
    })).validate(new_data)

    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)

        for attr, val in new_data.items():
            setattr(p, attr, val)

        return p.as_dict()


# todo
def increase_views(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        p.view_count += 1


def toggle_vote(PostClass, u_id, p_id, action):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)

        cur_vote = s.query(DPostVotes).get((u_id, p_id))
        new_vote = DPostVotes(u_id=u_id, p_id=p_id)
        if action == 'up':
            if cur_vote:
                if cur_vote.is_upvoted:
                    s.delete(cur_vote)
                    p.rating -= 1
                    return 'deleted'
                else:
                    p.rating += 2
                    cur_vote.is_upvoted = True
            else:
                p.rating += 1
                new_vote.is_upvoted = True
                s.add(new_vote)
            return 'up'
        elif action == 'down':
            if cur_vote:
                if not cur_vote.is_upvoted:
                    s.delete(cur_vote)
                    p.rating += 1
                    return 'deleted'
                else:
                    p.rating -= 2
                    cur_vote.is_upvoted = False
            else:
                p.rating -= 1
                new_vote.is_upvoted = False
                s.add(new_vote)
            return 'down'
        else:
            raise ValueError('Action should be only `up` or `down`')


def get_post_comments(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        comments = [c.as_dict() for c in p.comments.all()]
        return comments


def create_comment(PostClass, u_id, p_id, text):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        comment = Comment(u_id=u_id, p_id=p_id, text=text)
        p.comments.append(comment)
        p.comment_count += 1
        s.commit()
        return comment.as_dict()


def get_comment(c_id):
    with get_session() as s:
        comment = Comment.get_or_404(s, c_id)
        return comment
