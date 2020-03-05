from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from datetime import datetime
import requests
import logging
import os
import nanoid

from .db import *
from . import util
from . import logger


def get_posts(PostClass, u_id):
    with get_session() as s:
        User.get_or_404(s, u_id)
        posts = [p.as_dict() for p in s.query(PostClass)
            .filter(PostClass.u_id == u_id)
            .order_by(PostClass.creation_date.desc()).all()]
        return posts
