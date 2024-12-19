from string import ascii_letters, digits

# Максимальная длина оригинальной ссылки
MAX_LEN_ORIGINAL = 256

# Максимальная длина короткой ссылки
MAX_LEN_SHORT = 16

# Допустимые символы для короткой ссылки
SHORT_URL_CHARS = ascii_letters + digits

# Регулярное выражение для проверки короткой ссылки
SHORT_URL_PATTERN = r'^[{}]{{1,{}}}$'.format(
    ''.join(sorted(set(SHORT_URL_CHARS))), 
    MAX_LEN_SHORT
)
