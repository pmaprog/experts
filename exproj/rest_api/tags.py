from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_required

from . import make_ok, access_required
from exproj.logic import tags as tags_logic

bp = Blueprint('tags', __name__, url_prefix='/tag')


@bp.route('/all')
def get_tags():
    tags = tags_logic.get_many()
    return jsonify(tags)


@bp.route('/')
@login_required
@access_required('moderator')
def create_tag():
    name = request.args.get('name')
    tags_logic.create(name)
    return make_ok('Tag successfully created'), 201


@bp.route('/<tag>', methods=['PUT'])
@login_required
@access_required('moderator')
def update_tag(tag):
    new_name = request.args.get('name')
    tags_logic.update(tag, new_name)
    return make_ok('Tag successfully updated')


@bp.route('/<tag>', methods=['DELETE'])
@login_required
@access_required('moderator')
def delete_tag(tag):
    tags_logic.delete(tag)
    return make_ok('Tag successfully deleted')
