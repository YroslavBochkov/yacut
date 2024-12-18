# yacut/api_views.py
from http import HTTPStatus

from flask import jsonify, request, url_for
from sqlalchemy.exc import IntegrityError

from yacut import app, db
from yacut.error_handlers import (
    InvalidAPIUsage,
    validate_url_map
)
from yacut.models import URLMap


@app.route('/api/id/', methods=['POST'])
def generate_short_url():
    """Метод API для генерации короткой ссылки."""
    # Проверка, что это JSON-запрос
    if not request.is_json:
        raise InvalidAPIUsage('Некорректный запрос')

    # Получение JSON-данных
    data = request.get_json(silent=True)

    # Валидация данных
    validated_data = validate_url_map(data)

    # Создание объекта URLMap
    url_map = URLMap()
    url_map.original = validated_data['url']
    url_map.short = (
        validated_data.get('custom_id') or URLMap.get_unique_short_id()
    )

    try:
        # Сохранение в базу данных
        db.session.add(url_map)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )

    # Формирование короткой ссылки
    short_link = url_for(
        'redirect_short_url',
        url=url_map.short,
        _external=True
    )

    return jsonify(
        url=url_map.original,
        short_link=short_link
    ), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    """Метод API для получения оригинальной ссылки."""
    url_obj = URLMap.get_obj_by_short(short_id)
    if url_obj is None:
        raise InvalidAPIUsage(
            'Указанный id не найден',
            status_code=HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': url_obj.original}), HTTPStatus.OK
