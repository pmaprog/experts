from flask import abort
from flask_login import current_user
from sqlalchemy import or_

from . import logger
from .db import *


def get_many(PostClass, u_id=None, closed=None, offset=None, limit=None):
    with get_session() as s:
        query = s.query(PostClass)\
            .filter(PostClass.status == 'active')\
            .order_by(PostClass.creation_date.desc())

        if u_id:
            query = query.filter(PostClass.u_id == u_id)

        if PostClass == Question:
            if closed and closed != '0':
                if PostClass != Question:
                    abort(422, '`closed` parameter is not compatible with article')
                if not current_user.has_access('expert'):
                    abort(403, 'You can\'t view closed questions')
                query = query.filter(Question.closed.is_(True))
            else:
                query = query.filter(Question.closed.is_(False))

        if offset and limit:
            try:
                offset = int(offset)
                limit = int(limit)
            except:
                abort(422, 'query parameters '
                           '`offset` and `limit` should be numbers')

            if offset < 0 or limit < 1:
                abort(422, 'query parameters '
                           '`offset` or `limit` has wrong values')

            data = query.slice(offset, offset + limit)
        else:
            data = query.all()

        posts = [p.as_dict() for p in data]
        return posts


def get(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)

        if p.closed and not current_user.has_access('expert'):
            abort(403)

        return p.as_dict()


def create(PostClass, data):
    u_id = current_user.id

    PostClass.schema.validate(data)
    if data['closed'] is True and not current_user.has_access('expert'):
        abort(422, 'You cannot create closed questions')

    with get_session() as s:
        s.add(current_user)
        if PostClass == Question:
            p = Question(u_id=u_id, title=data['title'], body=data['body'],
                         only_experts_answer=data['only_experts_answer'],
                         only_chosen_domains=data['only_chosen_domains'],
                         closed=data['closed'])
        elif PostClass == Article:
            p = Article(u_id=u_id, title=data['title'], body=data['body'])
        s.add(p)
        s.commit()
        # current_user.increment_count(PostClass)

        if PostClass == Question:
            current_user.question_count += 1
        elif PostClass == Article:
            current_user.article_count += 1

        return p.id  # return created question's id


def delete(PostClass, p_id):
    with get_session() as s:
        s.add(current_user)

        p = PostClass.get_or_404(s, p_id)

        if (not current_user.has_access('moderator') and
                p.u_id != current_user.id):
            abort(403)

        if PostClass == Question:
            current_user.question_count -= 1
        elif PostClass == Article:
            current_user.article_count -= 1

        # todo: decrease comment_count for all users who comment to the post
        p.status = 'deleted'


def update(PostClass, p_id, new_data):
    PostClass.schema.validate(new_data)

    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)

        if (not current_user.has_access('moderator') and
                p.u_id != current_user.id):
            abort(403)

        for param, value in new_data.items():
            setattr(p, param, value)

        return p.as_dict()


# todo
def increase_views(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        p.view_count += 1


def toggle_vote(PostClass, p_id, action):
    u_id = current_user.id

    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        if (PostClass == Question and
                p.closed and not current_user.has_access('expert')):
            abort(403)

        if PostClass == Comment:
            if (isinstance(p.post, Question) and
                    p.closed and not current_user.has_access('expert')):
                abort(403)
            cur_vote = s.query(DCommentVotes).get((u_id, p_id))
            new_vote = DCommentVotes(u_id=u_id, c_id=p_id)
        else:
            cur_vote = s.query(DPostVotes).get((u_id, p_id))
            new_vote = DPostVotes(u_id=u_id, p_id=p_id)
        if action == 'up':
            if cur_vote:
                if cur_vote.upvoted:
                    s.delete(cur_vote)
                    p.score -= 1
                    return 'deleted'
                else:
                    p.score += 2
                    cur_vote.upvoted = True
            else:
                p.score += 1
                new_vote.upvoted = True
                s.add(new_vote)
            return 'up'
        elif action == 'down':
            if cur_vote:
                if not cur_vote.upvoted:
                    s.delete(cur_vote)
                    p.score += 1
                    return 'deleted'
                else:
                    p.score -= 2
                    cur_vote.upvoted = False
            else:
                p.score -= 1
                new_vote.upvoted = False
                s.add(new_vote)
            return 'down'
        else:
            raise ValueError('Action should be only `up` or `down`')


def get_post_comments(PostClass, p_id):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)

        if p.closed and not current_user.has_access('expert'):
            abort(403, 'You must be an expert')

        comments = [c.as_dict() for c in p.comments
                    .filter(Comment.status == 'active')
                    .order_by(Comment.creation_date.desc()).all()]
        return comments


def create_comment(PostClass, p_id, text):
    u_id = current_user.id

    with get_session() as s:
        s.add(current_user)
        p = PostClass.get_or_404(s, p_id)

        if PostClass == Question and not current_user.can_answer(p):
            abort(403, 'You must be an expert to answer the question')

        comment = Comment(u_id=u_id, p_id=p_id, text=text)
        p.comments.append(comment)
        p.comment_count += 1
        current_user.comment_count += 1
        s.commit()
        return comment.as_dict()


def update_domains(PostClass, p_id, domains):
    with get_session() as s:
        p = PostClass.get_or_404(s, p_id)
        # d = s.query(Domain).filter(Domain.id.in_(data['domains'])).all()
        # subd = s.query(Domain).filter(Domain.id.in_(data['subdomains']),
        #                               Domain.parent.isnot(None)).all()
        for d in domains:
            s.add(DPostDomains(p_id=p_id, d_id=d.id, sub=d.parent is not None))
