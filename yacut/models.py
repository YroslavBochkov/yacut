import random
import re
from datetime import datetime
from flask import url_for

from . import db

class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'url': self.original,
            'short_link': url_for('redirect_to_original', short_id=self.short, _external=True)
        }

    @staticmethod
    def get_unique_short_id(length=6):
        """Генерирует уникальную короткую ссылку."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        while True:
            short_url = ''.join(random.choice(chars) for _ in range(length))
            if not URLMap.query.filter_by(short=short_url).first():
                return short_url

    @staticmethod
    def validate_custom_id(custom_id):
        """Валидация custom_id."""
        if not custom_id:
            return False
        
        # Проверка на длину (до 16 символов)
        if len(custom_id) > 16:
            return False
        
        # Проверка на допустимые символы (только буквы и цифры)
        return bool(re.match(r'^[a-zA-Z0-9]+$', custom_id))

    @classmethod
    def create(cls, original, custom_id=None):
        """Создание новой ссылки с валидацией."""
        # Если custom_id не указан или невалиден - генерируем
        if not custom_id or not cls.validate_custom_id(custom_id):
            custom_id = cls.get_unique_short_id()
        
        # Проверка на уникальность custom_id
        if cls.query.filter_by(short=custom_id).first():
            raise ValueError('Предложенный вариант короткой ссылки уже существует.')
        
        # Создание и сохранение новой ссылки
        new_url = cls(original=original, short=custom_id)
        db.session.add(new_url)
        db.session.commit()
        
        return new_url
