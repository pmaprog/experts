from exproj.db import *


def get_many():
    with get_session() as s:
        tags = [t.as_dict() for t in s.query(Tag).all()]
        return tags


def get(t_id):
    with get_session() as s:
        tag = Tag.get_or_404(s, t_id).as_dict()
        return tag


def create(name):
    with get_session() as s:
        if s.query(Tag).filter(Tag.name == name).one_or_none():
            abort(409, 'Tag with this name already exists')

        tag = Tag(name=name)
        s.add(tag)


def update(t_id, name):
    with get_session() as s:
        if s.query(Tag).filter(Tag.name == name).one_or_none():
            abort(409, 'Tag with this name already exists')

        tag = Tag.get_or_404(s, t_id)
        tag.name = name


def delete(t_id):
    with get_session() as s:
        tag = Tag.get_or_404(s, t_id)
        tag.posts = tag.users_tags = tag.users_interests = []
        s.delete(tag)
