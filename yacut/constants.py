import re
from string import ascii_letters, digits

MAXIMUM_LENGTH_ORIGINAL = 2048
MAXIMUM_LENGTH_SHORT = 16
SHORT_URL_CHARS = ascii_letters + digits
REDIRECT_VIEW = 'redirect_short_url'


SHORT = r'^[' + re.escape(SHORT_URL_CHARS) + ']+$'
GENERATED_SHORT_LENGTH = 6
