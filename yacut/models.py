import random
import re
from datetime import datetime

from flask import url_for

from yacut import db
from yacut.constants import (MAX_LEN_ORIGINAL, MAX_LEN_SHORT,
                             STR_FOR_GEN_URL, PATTERN_FOR_CHECK_URL)
from yacut.error_handlers import URLValidationError


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

    @staticmethod
    def get_obj_by_short(url):
        """Метод получает объект по его короткой ссылке."""
        return URLMap.query.filter_by(short=url).first()

    @staticmethod
    def validate_data(data):
        """Валидация полей модели."""
        if not data:
            raise URLValidationError('Отсутствует тело запроса')
        elif 'url' not in data:
            raise URLValidationError('"url" является обязательным полем!')
        elif not data.get('custom_id'):
            data['custom_id'] = URLMap.get_unique_short_id()
        elif re.search(PATTERN_FOR_CHECK_URL, data['custom_id']) is None:
            raise URLValidationError('Указано недопустимое имя для '
                                     'короткой ссылки')
        elif URLMap.get_obj_by_short(data['custom_id']) is not None:
            raise URLValidationError('Предложенный вариант короткой ссылки '
                                     'уже существует.')
        return data

    @staticmethod
    def create_obj(data):
        """Метод для создания объекта."""
        data = URLMap.validate_data(data)
        url_obj = URLMap(original=data['url'], short=data['custom_id'])
        db.session.add(url_obj)
        db.session.commit()
        return url_obj
