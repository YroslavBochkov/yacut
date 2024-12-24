import random
import re
from datetime import datetime
from flask import url_for

from yacut import db
from yacut.constants import (
    MAXIMUM_LENGTH_ORIGINAL,
    MAXIMUM_LENGTH_SHORT,
    SHORT_URL_CHARS,
    GENERATED_SHORT_LENGTH,
    SHORT
)


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

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(MAXIMUM_LENGTH_ORIGINAL), nullable=False
    )
    short = db.Column(
        db.String(MAXIMUM_LENGTH_SHORT), unique=True, nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Метод создает словарь из атрибутов объекта."""
        return dict(
            url=self.original,
            short_link=self.get_short_link()
        )

    def get_short_link(self):
        """Генерация короткой ссылки."""
        return url_for(
            'redirect_short_url', short=self.short, _external=True
        )

    @staticmethod
    def get_unique_short():
        """Метод создает уникальную короткую ссылку."""
        for _ in range(GENERATED_SHORT_LENGTH):
            if short := ''.join(
                random.choices(
                    population=SHORT_URL_CHARS,
                    k=GENERATED_SHORT_LENGTH
                )
            ):
                if not URLMap.query.filter_by(short=short).first():
                    return short
        raise RuntimeError(URLMap.ERROR_GENERATION_FAILED)

    @staticmethod
    def get(short):
        """Метод получает объект по его короткой ссылке."""
        if result := URLMap.query.filter_by(short=short).first():
            return result
        raise URLMap.URLValidationError(URLMap.ERROR_NOT_FOUND)

    @staticmethod
    def create(original, short=None, validate=False):
        """Создание новой записи с проверкой и генерацией короткой ссылки."""
        if validate:
            if len(original) > MAXIMUM_LENGTH_ORIGINAL:
                raise URLMap.URLValidationError(
                    'Слишком длинная оригинальная ссылка'
                )

            if short:
                if len(short) > MAXIMUM_LENGTH_SHORT:
                    raise URLMap.URLValidationError(
                        URLMap.ERROR_INVALID_SHORT_URL
                    )
                if not re.match(SHORT, short):
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
