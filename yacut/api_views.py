from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.settings import Config

INCORRECT_REQUEST_MESSAGE = 'Некорректный запрос'
EMPTY_REQUEST_BODY_MESSAGE = 'Отсутствует тело запроса'
REQUIRED_URL_FIELD_MESSAGE = '"url" является обязательным полем!'


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
    try:
        url_map = URLMap.create(
            original=data['url'],
            short=data.get('custom_id')
        )
        return jsonify({
            'url': url_map.original,
            'short_link': Config.get_short_link(url_map.short)
        }), HTTPStatus.CREATED
    except URLMap.URLValidationError as e:
        raise InvalidAPIUsage(str(e))


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    """Метод API для получения оригинальной ссылки."""
    try:
        url_map = URLMap.get_by_short(short)
        return jsonify({'url': url_map.original}), HTTPStatus.OK
    except URLMap.URLValidationError as e:
        raise InvalidAPIUsage(str(e), status_code=404)
