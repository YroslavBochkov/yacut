import random
import re
from datetime import datetime
from flask import url_for

from yacut import db
from yacut.constants import (
    MAX_LEN_ORIGINAL,
    MAX_LEN_SHORT,
    SHORT_URL_CHARS,
    REDIRECT_VIEW
)
from yacut.constants import Config


class URLMap(db.Model):
    """Модель для сохранения оригинальной и короткой ссылки на источник."""
    class URLValidationError(ValueError):
        """Кастомное исключение для ошибок валидации."""

    ERROR_INVALID_SHORT_URL = 'Указано недопустимое имя для короткой ссылки'
    ERROR_DUPLICATE_SHORT_URL = (
        'Предложенный вариант короткой ссылки уже существует.'
    )
    ERROR_GENERATION_FAILED = (
        'Не удалось сгенерировать уникальную короткую ссылку'
    )
    ERROR_NOT_FOUND = 'Указанный id не найден'
    ERROR_EMPTY_ORIGINAL = 'Отсутствует оригинальная ссылка'
    ERROR_LONG_ORIGINAL = 'Слишком длинная оригинальная ссылка'

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
    def get_unique_short():
        """Метод создает уникальную короткую ссылку."""
        for _ in range(Config.MAX_UNIQUE_SHORT_ATTEMPTS):
            short = ''.join(
                random.choices(
                    population=SHORT_URL_CHARS,
                    k=Config.GENERATED_SHORT_LENGTH
                )
            )
            if not URLMap.query.filter_by(short=short).first():
                return short
        raise RuntimeError(URLMap.ERROR_GENERATION_FAILED)

    @staticmethod
    def get(short):
        """Метод получает объект по его короткой ссылке."""
        result = URLMap.query.filter_by(short=short).first()
        if not result:
            raise URLMap.URLValidationError(URLMap.ERROR_NOT_FOUND)
        return result

    @staticmethod
    def create(original, short=None):
        """Создание новой записи с проверкой и генерацией короткой ссылки."""
        if not original:
            raise URLMap.URLValidationError(URLMap.ERROR_EMPTY_ORIGINAL)

        if len(original) > MAX_LEN_ORIGINAL:
            raise URLMap.URLValidationError(URLMap.ERROR_LONG_ORIGINAL)

        if short:
            if len(short) > MAX_LEN_SHORT:
                raise URLMap.URLValidationError(
                    URLMap.ERROR_INVALID_SHORT_URL
                )
            if not re.match(Config.SHORT_URL_PATTERN, short):
                raise URLMap.URLValidationError(
                    URLMap.ERROR_INVALID_SHORT_URL
                )

        if not short:
            short = URLMap.get_unique_short()

        if URLMap.query.filter_by(short=short).first():
            raise URLMap.URLValidationError(
                URLMap.ERROR_DUPLICATE_SHORT_URL
            )

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map
