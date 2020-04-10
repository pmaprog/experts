from flask import abort

from exproj.db import get_session, Tag


def get_many():
    with get_session() as s:
        tags = [t.name for t in s.query(Tag).all()]
        return tags


def create(name):
    with get_session() as s:
        if s.query(Tag).filter_by(name=name).first():
            abort(409, 'Tag with this name already exists')

        tag = Tag(name=name)
        s.add(tag)


def update(name, new_name):
    with get_session() as s:
        if s.query(Tag).filter_by(name=new_name).first():
            abort(409, 'Tag with this name already exists')

        tag = s.query(Tag).filter_by(name=name).first()
        if tag is None:
            abort(404, 'Tag not found')

        tag.name = new_name


def delete(name):
    with get_session() as s:
        tag = s.query(Tag).filter_by(name=name).first()
        if tag is None:
            abort(404, 'Tag not found')

        tag.posts = tag.users_tags = tag.users_interests = []
        s.delete(tag)
