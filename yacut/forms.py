from flask_wtf import FlaskForm
from wtforms import SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError

from yacut.constants import MAX_LEN_ORIGINAL, MAX_LEN_SHORT, SHORT_URL_CHARS
from yacut.models import URLMap

# Константы для меток и сообщений
ORIGINAL_LINK_LABEL = 'Длинная ссылка'
CUSTOM_ID_LABEL = 'Ваш вариант короткой ссылки'
CREATE_BUTTON_LABEL = 'Создать'

# Константы для сообщений валидации
REQUIRED_FIELD_MESSAGE = 'Обязательное поле'
INCORRECT_URL_MESSAGE = 'Некорректная ссылка'
INVALID_CHARS_MESSAGE = ('Используются недопустимые символы (разрешены '
                         'только A-Z, a-z, 0-9).')
DUPLICATE_SHORT_LINK_MESSAGE = 'Предложенный вариант короткой ссылки уже существует.'


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            Length(min=1, max=MAX_LEN_ORIGINAL),
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            URL(require_tld=True, message=INCORRECT_URL_MESSAGE)]
    )
    custom_id = URLField(
        CUSTOM_ID_LABEL,
        validators=[
            Length(min=1, max=MAX_LEN_SHORT),
            Optional()]
    )

    def validate_custom_id(self, field):
        """
        Валидация короткой ссылки с проверкой в базе данных
        и по допустимым символам
        """
        if field.data:
            # Проверка на допустимые символы
            if not all(char in SHORT_URL_CHARS for char in field.data):
                raise ValidationError(INVALID_CHARS_MESSAGE)

            # Проверка уникальности в базе данных
            if URLMap.query.filter_by(short=field.data).first():
                raise ValidationError(DUPLICATE_SHORT_LINK_MESSAGE)

    submit = SubmitField(CREATE_BUTTON_LABEL)
