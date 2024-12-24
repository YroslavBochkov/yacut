import re
from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.constants import (
    MAXIMUM_LENGTH_SHORT,
    SHORT
)

INCORRECT_REQUEST_MESSAGE = 'Некорректный запрос'
EMPTY_REQUEST_BODY_MESSAGE = 'Отсутствует тело запроса'
REQUIRED_URL_FIELD_MESSAGE = '"url" является обязательным полем!'
INVALID_SHORT_URL_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
URL_NOT_FOUND_MESSAGE = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def generate_short_url():
    """Метод API для генерации короткой ссылки."""
    if not request.is_json:
        raise InvalidAPIUsage(INCORRECT_REQUEST_MESSAGE)
    data = request.get_json(force=True, silent=True)
    if not data:
        raise InvalidAPIUsage(EMPTY_REQUEST_BODY_MESSAGE)
    if 'url' not in data:
        raise InvalidAPIUsage(REQUIRED_URL_FIELD_MESSAGE)
    short = data.get('custom_id')
    if short:
        if len(short) > MAXIMUM_LENGTH_SHORT:
            raise InvalidAPIUsage(INVALID_SHORT_URL_MESSAGE)
        if not re.match(SHORT, short):
            raise InvalidAPIUsage(INVALID_SHORT_URL_MESSAGE)
    try:
        url_map = URLMap.create(
            original=data['url'],
            short=short
        )
        return jsonify({
            'url': url_map.original,
            'short_link': url_map.get_short_link()
        }), HTTPStatus.CREATED
    except (
        URLMap.URLValidationError,
        ValueError,
        RuntimeError
    ) as e:
        raise InvalidAPIUsage(
            str(e),
            status_code=HTTPStatus.BAD_REQUEST
        )


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    """Метод API для получения оригинальной ссылки."""
    url_map = URLMap.query.filter_by(short=short).first()
    if not url_map:
        raise InvalidAPIUsage(
            URL_NOT_FOUND_MESSAGE,
            status_code=HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': url_map.original}), HTTPStatus.OK
