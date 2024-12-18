import random
import string

def get_unique_short_id(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(chars) for _ in range(length))
        from .models import URLMap
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
