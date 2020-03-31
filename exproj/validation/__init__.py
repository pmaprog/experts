from exproj.db import *


def validate_tags(tag_names):
    with get_session() as s:
        tags = s.query(Tag).filter(Tag.name.in_(tag_names)).all()

        if sorted(tag_names) != sorted([t.name for t in tags]):
            abort(422, 'Wrong tags')
