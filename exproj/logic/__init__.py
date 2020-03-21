from exproj.db import *


# def _update_tags(obj, tag_ids):
#     with get_session() as s:
#         tags = s.query(Tag).filter(Tag.id.in_(tag_ids)).all()
#
#     for t in obj.tags.all():
#         obj.tags.remove(t)
#
#     for t in tags:
#         obj.tags.append(t)
