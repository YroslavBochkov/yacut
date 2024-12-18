from string import ascii_letters, digits

MIN_LEN = 1
MAX_LEN_ORIGINAL = 256
MAX_LEN_SHORT = 16

STR_FOR_GEN_URL = ascii_letters + digits

PATTERN_FOR_CHECK_URL = r'^[A-Za-z0-9]{1,16}$'
