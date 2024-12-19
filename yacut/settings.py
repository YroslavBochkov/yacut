# yacut/settings.py
from flask import url_for

class Config:
    """Конфигурация приложения"""
    
    # Константа для имени view-функции
    REDIRECT_ENDPOINT = 'redirect_short_url'

    @classmethod
    def get_short_link(cls, short):
        """
        Централизованный метод генерации короткой ссылки
        
        Args:
            short (str): Короткий идентификатор ссылки
        
        Returns:
            str: Полная короткая ссылка
        """
        return url_for(cls.REDIRECT_ENDPOINT, url=short, _external=True)
