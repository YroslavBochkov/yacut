# yacut/error_handlers.py
from http import HTTPStatus
import re
from flask import jsonify, render_template

from yacut import app, db
from yacut.constants import (
    MAX_LEN_SHORT,
    MAX_LEN_ORIGINAL,
    SHORT_URL_PATTERN
)


class URLValidationError(Exception):
    """Ошибка для валидаторов генерации короткой ссылки."""

    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidAPIUsage(Exception):
    """Ошибка для API-интерфейса."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Метод возвращает словарь с сообщением."""
        return dict(message=self.message)


def validate_url_map(data):
    """Комплексная валидация данных для создания короткой ссылки."""
    # Проверка на пустые данные
    if not data:
        raise URLValidationError('Отсутствует тело запроса')

    # Проверка наличия обязательных полей
    if 'url' not in data:
        raise URLValidationError('"url" является обязательным полем!')

    # Проверка длины оригинальной ссылки
    if len(data['url']) > MAX_LEN_ORIGINAL:
        raise URLValidationError(
            f'Превышена максимальная длина ссылки в '
            f'{MAX_LEN_ORIGINAL} символов'
        )

    # Проверка кастомного идентификатора
    if data.get('custom_id'):
        # Проверка длины
        if len(data['custom_id']) > MAX_LEN_SHORT:
            raise URLValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )

        # Проверка на допустимые символы
        if not re.match(SHORT_URL_PATTERN, data['custom_id']):
            raise URLValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )

    return data


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Хендлер для ошибок api."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(URLValidationError)
def handle_validation_error(error):
    """Хендлер для ошибок валидации."""
    return jsonify({'message': error.message}), HTTPStatus.BAD_REQUEST


@app.errorhandler(404)
def page_not_found(error):
    """Хендлер для ошибки 404."""
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error):
    """Хендлер для ошибки 500."""
    db.session.rollback()
    return render_template('errors/500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
