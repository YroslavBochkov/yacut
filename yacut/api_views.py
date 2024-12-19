from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.error_handlers import (
    InvalidAPIUsage,
    validate_url_map
)
from yacut.models import URLMap
from yacut.settings import Config

# Константы для сообщений
INCORRECT_REQUEST = 'Некорректный запрос'
ID_NOT_FOUND = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def generate_short_url():
    """Метод API для генерации короткой ссылки."""
    if not request.is_json:
        raise InvalidAPIUsage(INCORRECT_REQUEST)

    data = request.get_json(silent=True)
    validated_data = validate_url_map(data)

    url_map = URLMap.create(
        original=validated_data['url'],
        short=validated_data.get('custom_id')
    )

    short_link = Config.get_short_link(url_map.short)

    return jsonify(
        url=url_map.original,
        short_link=short_link
    ), HTTPStatus.CREATED


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    """Метод API для получения оригинальной ссылки."""
    url_obj = URLMap.get_obj_by_short(short)
    if url_obj is None:
        raise InvalidAPIUsage(
            ID_NOT_FOUND,
            status_code=HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': url_obj.original}), HTTPStatus.OK
