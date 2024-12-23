from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField
from wtforms.validators import (
    DataRequired, Length, Optional, URL, ValidationError, Regexp
)

from yacut.constants import MAX_LEN_ORIGINAL, MAX_LEN_SHORT
from yacut.constants import Config
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
            Length(max=MAX_LEN_ORIGINAL),
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            URL(require_tld=True, message=INCORRECT_URL_MESSAGE)
        ]
    )
    custom_id = URLField(
        CUSTOM_ID_LABEL,
        validators=[
            Length(max=MAX_LEN_SHORT),
            Regexp(
                regex=Config.SHORT_URL_PATTERN,
                message=INVALID_CHARS_MESSAGE
            ),
            Optional()
        ]
    )
    submit = SubmitField(CREATE_BUTTON_LABEL)

    def validate_custom_id(self, field):
        """Валидация короткой ссылки с проверкой в базе данных."""
        if field.data and URLMap.query.filter_by(short=field.data).first():
            raise ValidationError(DUPLICATE_SHORT_LINK_MESSAGE)
