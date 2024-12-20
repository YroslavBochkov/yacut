from http import HTTPStatus
from flask import jsonify, request, abort
from werkzeug.exceptions import BadRequest

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.settings import Config


@app.route('/api/id/', methods=['POST'])
def generate_short_url():
    """Метод API для генерации короткой ссылки."""
    if not request.is_json:
        raise InvalidAPIUsage('Некорректный запрос')

    try:
        data = request.get_json(force=True, silent=False)
    except BadRequest:
        return jsonify({'message': 'Отсутствует тело запроса'}), HTTPStatus.BAD_REQUEST

    # Проверки во входящих данных
    if not data:
        return jsonify({'message': 'Отсутствует тело запроса'}), HTTPStatus.BAD_REQUEST

    if 'url' not in data:
        return jsonify({'message': '"url" является обязательным полем!'}), HTTPStatus.BAD_REQUEST

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
        return jsonify({'message': str(e)}), HTTPStatus.BAD_REQUEST


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_url(short):
    """Метод API для получения оригинальной ссылки."""
    url_map = URLMap.get_by_short(short)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
