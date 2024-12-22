import random
from datetime import datetime
from flask import url_for

from yacut import db
from yacut.constants import (
    MAX_LEN_ORIGINAL,
    MAX_LEN_SHORT,
    SHORT_URL_CHARS,
    REDIRECT_VIEW
)


class URLMap(db.Model):
    """Модель для сохранения оригинальной и короткой ссылки на источник."""
    class URLValidationError(ValueError):
        """Кастомное исключение для ошибок валидации."""

    GENERATED_SHORT_LENGTH = 6

    ERROR_INVALID_SHORT_URL = 'Указано недопустимое имя для короткой ссылки'
    ERROR_DUPLICATE_SHORT_URL = (
        'Предложенный вариант короткой ссылки уже существует.'
    )
    ERROR_GENERATION_FAILED = (
        'Не удалось сгенерировать уникальную короткую ссылку'
    )

    ERROR_NOT_FOUND = 'Указанный id не найден'

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LEN_ORIGINAL), nullable=False)
    short = db.Column(db.String(MAX_LEN_SHORT), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Метод создает словарь из атрибутов объекта."""
        return dict(
            url=self.original,
            short_link=self.get_short_link()
        )

    def get_short_link(self):
        """Генерация короткой ссылки."""
        return url_for(REDIRECT_VIEW, url=self.short, _external=True)

    @staticmethod
    def _get_or_raise(short, error_message):
        """Получает объект или вызывает исключение."""
        result = URLMap.query.filter_by(short=short).first()
        if result is None:
            raise URLMap.URLValidationError(error_message)
        return result

    @staticmethod
    def get_unique_short_id():
        """Метод создает уникальную короткую ссылку."""
        for _ in range(10):
            short_url = ''.join(
                random.choices(
                    population=SHORT_URL_CHARS,
                    k=URLMap.GENERATED_SHORT_LENGTH
                )
            )
            if URLMap.query.filter_by(short=short_url).first() is None:
                return short_url
        raise RuntimeError(URLMap.ERROR_GENERATION_FAILED)

    @staticmethod
    def get_by_short(short):
        """Метод получает объект по его короткой ссылке."""
        return URLMap._get_or_raise(short, URLMap.ERROR_NOT_FOUND)

    @staticmethod
    def create(original, short=None):
        """Создание новой записи с проверкой и генерацией короткой ссылки."""
        if short:
            if len(short) > MAX_LEN_SHORT:
                raise URLMap.URLValidationError(
                    URLMap.ERROR_INVALID_SHORT_URL
                )
            if not all(char.isascii() and char.isalnum() for char in short):
                raise URLMap.URLValidationError(
                    URLMap.ERROR_INVALID_SHORT_URL
                )

        if not short:
            short = URLMap.get_unique_short_id()

        if URLMap.query.filter_by(short=short).first():
            raise URLMap.URLValidationError(
                URLMap.ERROR_DUPLICATE_SHORT_URL
            )

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map
