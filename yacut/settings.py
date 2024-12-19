from flask import url_for
from yacut.constants import SHORT_URL_CHARS, MAX_LEN_SHORT

class Config:
    """Конфигурация приложения"""

    # Константа для имени view-функции
    REDIRECT_ENDPOINT = 'redirect_short_url'

    # Максимальное число попыток генерации уникальной короткой ссылки
    MAX_UNIQUE_ID_ATTEMPTS = 10

    # Регулярное выражение для короткой ссылки
    SHORT_URL_PATTERN = r'^[{}]{{1,{}}}$'.format(
        ''.join(sorted(set(SHORT_URL_CHARS))), 
        MAX_LEN_SHORT
    )

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
