from flask import url_for
from yacut.constants import SHORT_URL_CHARS, MAX_LEN_SHORT


class Config:
    """Конфигурация приложения"""
    REDIRECT_ENDPOINT = 'redirect_short_url'
    MAX_UNIQUE_ID_ATTEMPTS = 10
    SHORT_URL_PATTERN = r'^[{}]{{1,{}}}$'.format(
        ''.join(sorted(set(SHORT_URL_CHARS))),
        MAX_LEN_SHORT
    )

    @classmethod
    def get_short_link(cls, short):
        """Централизованный метод генерации короткой ссылки"""
        return url_for(cls.REDIRECT_ENDPOINT, url=short, _external=True)
