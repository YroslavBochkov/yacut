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

    @classmethod
    def get_by_short(cls, short):
        """Метод получает объект по его короткой ссылке."""
        return cls.query.filter_by(short=short).first()

    @classmethod
    def create(cls, original, short=None):
        """
        Создание новой записи с проверкой и генерацией короткой ссылки.

        Args:
            original (str): Оригинальная длинная ссылка
            short (str, optional): Пользовательский вариант короткой ссылки

        Returns:
            URLMap: Созданный объект

        Raises:
            InvalidAPIUsage: При проблемах создания ссылки
        """
        # Проверка пользовательского варианта короткой ссылки
        if short:
            # Валидация формата
            if not re.match(Config.SHORT_URL_PATTERN, short):
                raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')

            # Проверка уникальности
            if cls.get_by_short(short):
                raise InvalidAPIUsage('Предложенный вариант короткой ссылки уже существует.')

        # Генерация короткой ссылки, если не передана
        if not short:
            short = cls.get_unique_short_id()

        # Создание нового объекта
        url_map = cls(
            original=original,
            short=short
        )

        # Абстракция сохранения
        return cls.save(url_map)

    @classmethod
    def save(cls, url_map):
        """
        Абстрактный метод сохранения с обработкой ошибок.

        Args:
            url_map (URLMap): Объект для сохранения

        Returns:
            URLMap: Сохраненный объект

        Raises:
            InvalidAPIUsage: При ошибках сохранения
        """
        try:
            db.session.add(url_map)
            db.session.commit()
            return url_map
        except IntegrityError:
            db.session.rollback()
            raise InvalidAPIUsage('Предложенный вариант короткой ссылки уже существует.')
