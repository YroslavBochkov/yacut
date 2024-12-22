import random
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from yacut import db
from yacut.constants import (
    MAX_LEN_ORIGINAL,
    MAX_LEN_SHORT,
    SHORT_URL_CHARS
)
from yacut.settings import Config


class URLMap(db.Model):
    """Модель для сохранения оригинальной и короткой ссылки на источник."""
    class URLValidationError(Exception):
        """Ошибка для валидаторов генерации короткой ссылки."""

    GENERATED_SHORT_ID_LENGTH = 6

    ERROR_LONG_URL = (
        f'Превышена максимальная длина ссылки в '
        f'{MAX_LEN_ORIGINAL} символов'
    )
    ERROR_INVALID_SHORT_URL = (
        'Указано недопустимое имя для короткой ссылки'
    )
    ERROR_DUPLICATE_SHORT_URL = (
        'Предложенный вариант короткой ссылки уже существует.'
    )
    ERROR_GENERATION_FAILED = (
        'Не удалось сгенерировать уникальную короткую '
        'ссылку'
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
            short_link=Config.get_short_link(self.short)
        )

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
        for _ in range(Config.MAX_UNIQUE_ID_ATTEMPTS):
            short_url = ''.join(
                random.choices(
                    population=SHORT_URL_CHARS,
                    k=URLMap.GENERATED_SHORT_ID_LENGTH
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
