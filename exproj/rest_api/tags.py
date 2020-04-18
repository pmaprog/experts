from flask import Blueprint, jsonify, request
from flask_login import login_required

from . import make_ok, access_required
from exproj.logic import tags as tags_logic
from exproj.validation import validate_tag_name

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
    validate_tag_name(name)
    tags_logic.create(name)
    return make_ok('Tag successfully created'), 201


@bp.route('/<tag>', methods=['PUT'])
@login_required
@access_required('moderator')
def update_tag(tag):
    new_name = request.args.get('name')
    validate_tag_name(new_name)
    tags_logic.update(tag, new_name)
    return make_ok('Tag successfully updated')


@bp.route('/<tag>', methods=['DELETE'])
@login_required
@access_required('moderator')
def delete_tag(tag):
    tags_logic.delete(tag)
    return make_ok('Tag successfully deleted')
