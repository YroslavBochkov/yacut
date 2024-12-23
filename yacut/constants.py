from string import ascii_letters, digits
MAX_LEN_ORIGINAL = 2048
MAX_LEN_SHORT = 16
SHORT_URL_CHARS = ascii_letters + digits
REDIRECT_VIEW = 'redirect_short_url'


class Config:
    """Конфигурация приложения"""
    MAX_UNIQUE_SHORT_ATTEMPTS = len(SHORT_URL_CHARS) ** 6
    SHORT_URL_PATTERN = r'^[a-zA-Z0-9]+$'
    GENERATED_SHORT_LENGTH = 6
