from flask import Blueprint, jsonify, request

from . import *
from exproj.logic import tags as tags_logic

bp = Blueprint('tags', __name__, url_prefix='/tag')


@bp.route('/all')
def get_tags():
    tags = tags_logic.get_many()
    return jsonify(tags)


@bp.route('/')
def create_tag():
    name = request.args.get('name')
    tags_logic.create(name)
    return make_ok('Tag successfully created'), 201


@bp.route('/<int:t_id>')
def get_tag(t_id):
    tag = tags_logic.get(t_id)
    return jsonify(tag)


@bp.route('/<int:t_id>', methods=['PUT'])
def update_tag(t_id):
    name = request.args.get('name')
    tags_logic.update(t_id, name)
    return make_ok('Tag successfully updated')


@bp.route('/<int:t_id>', methods=['DELETE'])
def delete_tag(t_id):
    tags_logic.delete(t_id)
    return make_ok('Tag successfully deleted')
