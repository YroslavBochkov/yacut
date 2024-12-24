from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField
from wtforms.validators import (
    DataRequired, Length, Optional, URL, ValidationError, Regexp
)

from yacut.constants import MAXIMUM_LENGTH_ORIGINAL, MAXIMUM_LENGTH_SHORT, SHORT
from yacut.models import URLMap

ORIGINAL_LINK_LABEL = 'Длинная ссылка'
CUSTOM_ID_LABEL = 'Ваш вариант короткой ссылки'
CREATE_BUTTON_LABEL = 'Создать'

REQUIRED_FIELD_MESSAGE = 'Обязательное поле'
INCORRECT_URL_MESSAGE = 'Некорректная ссылка'
INVALID_CHARS_MESSAGE = (
    'Используются недопустимые символы (разрешены только A-Z, a-z, 0-9).'
)
DUPLICATE_SHORT_LINK_MESSAGE = (
    'Предложенный вариант короткой ссылки уже существует.'
)


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""
    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            Length(max=MAXIMUM_LENGTH_ORIGINAL),
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            URL(require_tld=True, message=INCORRECT_URL_MESSAGE)
        ]
    )
    custom_id = URLField(
        CUSTOM_ID_LABEL,
        validators=[
            Length(max=MAXIMUM_LENGTH_SHORT),
            Regexp(
                regex=SHORT,
                message=INVALID_CHARS_MESSAGE
            ),
            Optional()
        ]
    )
    submit = SubmitField(CREATE_BUTTON_LABEL)

    def validate_custom_id(self, field):
        """Валидация короткой ссылки с проверкой в базе данных."""
        if field.data:
            try:
                URLMap.get(field.data)
                raise ValidationError(DUPLICATE_SHORT_LINK_MESSAGE)
            except URLMap.URLValidationError:
                pass
