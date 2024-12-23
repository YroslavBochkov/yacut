import re
from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.constants import MAX_LEN_SHORT
from yacut.settings import Config

INCORRECT_REQUEST_MESSAGE = 'Некорректный запрос'
EMPTY_REQUEST_BODY_MESSAGE = 'Отсутствует тело запроса'
REQUIRED_URL_FIELD_MESSAGE = '"url" является обязательным полем!'
INVALID_SHORT_URL_MESSAGE = 'Указано недопустимое имя для короткой ссылки'


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
    
    custom_id = data.get('custom_id')
    
    if custom_id:
        if len(custom_id) > MAX_LEN_SHORT:
            raise InvalidAPIUsage(INVALID_SHORT_URL_MESSAGE)
        
        if not re.match(Config.SHORT_URL_PATTERN, custom_id):
            raise InvalidAPIUsage(INVALID_SHORT_URL_MESSAGE)

    try:
        url_map = URLMap.create(
            original=data['url'],
            short=custom_id
        )
        return jsonify({
            'url': url_map.original,
            'short_link': url_map.get_short_link()
        }), HTTPStatus.CREATED
    except ValueError as e:
        raise InvalidAPIUsage(str(e))


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    """Метод API для получения оригинальной ссылки."""
    try:
        url_map = URLMap.get(short)
        return jsonify({'url': url_map.original}), HTTPStatus.OK
    except ValueError as e:
        raise InvalidAPIUsage(str(e), status_code=404)
