class Config:
    """Конфигурация приложения"""
    MAX_UNIQUE_SHORT_ATTEMPTS = 10
    SHORT_URL_PATTERN = r'^[a-zA-Z0-9]+$'
    GENERATED_SHORT_LENGTH = 6
