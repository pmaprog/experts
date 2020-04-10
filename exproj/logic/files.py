import os
import shutil
from os.path import join
from contextlib import suppress

from flask import abort

from exproj import logger, config


def get_ext(filename):
    return filename.rsplit('.', 1)[1].lower()


def save(file, filename, file_set):
    ext = get_ext(file.filename)

    if ext not in file_set.ALLOWED_EXTENSIONS:
        abort(422, 'Unsupported file extension')
    if file.mimetype not in file_set.ALLOWED_MIME_TYPES:
        abort(422, 'Unsupported mime type')
    if file.content_length > file_set.MAX_SIZE:
        abort(422, 'File size too large')

    tmp_path = join(config.FILE_UPLOADS.TEMP_DIRECTORY, filename)
    file.save(tmp_path)

    size = os.stat(tmp_path).st_size
    logger.debug('File size is {}'.format(size))
    if size > file_set.MAX_SIZE:
        os.remove(tmp_path)
        abort(422, 'File size too large')

    new_path = join(file_set.DIRECTORY, filename)
    shutil.move(tmp_path, new_path)


def remove(filename, file_set):
    path = join(file_set.DIRECTORY, filename)
    with suppress(Exception):  # ignore exceptions (file not found)
        os.remove(path)
