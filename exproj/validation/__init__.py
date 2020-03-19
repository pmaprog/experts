from exproj.db import *


def validate_tags(tag_ids):
    with get_session() as s:
        tags = s.query(Tag).filter(Tag.id.in_(tag_ids)) \
            .order_by(Tag.id).all()

        if [t.id for t in tags] != sorted(tag_ids):
            abort(422, 'Wrong tag ids')
