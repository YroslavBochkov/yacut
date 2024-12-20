import random
import re
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from yacut import db
from yacut.constants import (
    MAX_LEN_ORIGINAL, 
    MAX_LEN_SHORT, 
    SHORT_URL_CHARS
)
from yacut.settings import Config
from yacut.error_handlers import InvalidAPIUsage


class URLMap(db.Model):
    """Модель для сохранения оригинальной и короткой ссылки на источник."""

    class URLValidationError(Exception):
        """Ошибка для валидаторов генерации короткой ссылки."""

    # Константы для сообщений
    class Messages:
        ERROR_LONG_URL = f'Превышена максимальная длина ссылки в {MAX_LEN_ORIGINAL} символов'
        ERROR_INVALID_SHORT_URL = 'Указано недопустимое имя для короткой ссылки'
        ERROR_DUPLICATE_SHORT_URL = 'Предложенный вариант короткой ссылки уже существует.'
        ERROR_GENERATION_FAILED = 'Не удалось сгенерировать уникальную короткую ссылку'

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
    def get_unique_short_id():
        """Метод создает уникальную короткую ссылку."""
        for _ in range(Config.MAX_UNIQUE_ID_ATTEMPTS):
            short_url = ''.join(
                random.choices(population=SHORT_URL_CHARS, k=6)
            )
            if URLMap.query.filter_by(short=short_url).first() is None:
                return short_url
        
        raise URLMap.URLValidationError(URLMap.Messages.ERROR_GENERATION_FAILED)

    @classmethod
    def get_by_short(cls, short):
        """Метод получает объект по его короткой ссылке."""
        obj = cls.query.filter_by(short=short).first()
        if obj is None:
            raise InvalidAPIUsage('Указанный id не найден', status_code=404)
        return obj

    @classmethod
    def create(cls, original, short=None):
        """
        Создание новой записи с проверкой и генерацией короткой ссылки.
        """
        # Проверка длины оригинальной ссылки
        if len(original) > MAX_LEN_ORIGINAL:
            raise cls.URLValidationError(cls.Messages.ERROR_LONG_URL)

        # Проверка пользовательского варианта короткой ссылки
        if short:
            # Проверка длины
            if len(short) > MAX_LEN_SHORT:
                raise cls.URLValidationError(cls.Messages.ERROR_INVALID_SHORT_URL)

            # Проверка формата
            if not re.match(Config.SHORT_URL_PATTERN, short):
                raise cls.URLValidationError(cls.Messages.ERROR_INVALID_SHORT_URL)

            # Проверка уникальности
            if cls.query.filter_by(short=short).first():
                raise cls.URLValidationError(cls.Messages.ERROR_DUPLICATE_SHORT_URL)

        # Генерация короткой ссылки, если не передана
        if not short:
            short = cls.get_unique_short_id()

        # Создание нового объекта
        url_map = cls(
            original=original,
            short=short
        )

        # Сохранение
        try:
            db.session.add(url_map)
            db.session.commit()
            return url_map
        except IntegrityError:
            db.session.rollback()
            raise cls.URLValidationError(cls.Messages.ERROR_DUPLICATE_SHORT_URL)
