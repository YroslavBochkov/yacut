import random
import re
from datetime import datetime

from flask import url_for
from sqlalchemy.exc import IntegrityError

from yacut import db
from yacut.constants import (MAX_LEN_ORIGINAL, MAX_LEN_SHORT,
                             STR_FOR_GEN_URL, PATTERN_FOR_CHECK_URL)
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
            short_link=url_for('redirect_short_url', url=self.short,
                               _external=True)
        )

    @staticmethod
    def get_unique_short_id():
        """Метод создает уникальную короткую ссылку."""
        while True:
            short_url = ''.join(
                random.choices(population=STR_FOR_GEN_URL, k=6)
            )
            if URLMap.query.filter_by(short=short_url).first() is None:
                return short_url

    @classmethod
    def get_obj_by_short(cls, url):
        """Метод получает объект по его короткой ссылке."""
        return cls.query.filter_by(short=url).first()

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
            InvalidAPIUsage: При ошибках валидации или существовании ссылки
        """
        # Если короткая ссылка не передана или пустая - генерируем
        if not short:
            short = cls.get_unique_short_id()

        # Проверка уникальности
        if cls.get_obj_by_short(short):
            raise InvalidAPIUsage('Предложенный вариант короткой ссылки уже существует.')

        # Создание объекта
        url_map = cls(
            original=original,
            short=short
        )

        try:
            db.session.add(url_map)
            db.session.commit()
            return url_map
        except IntegrityError:
            db.session.rollback()
            raise InvalidAPIUsage('Предложенный вариант короткой ссылки уже существует.')
