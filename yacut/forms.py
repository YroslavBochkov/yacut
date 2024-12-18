from flask_wtf import FlaskForm
from wtforms import SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp

from yacut.constants import MAX_LEN_ORIGINAL, MAX_LEN_SHORT, MIN_LEN


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[
            Length(MIN_LEN, MAX_LEN_ORIGINAL),
            DataRequired(message='Обязательное поле'),
            URL(require_tld=True, message='Некорректная ссылка')]
    )
    custom_id = URLField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(MIN_LEN, MAX_LEN_SHORT),
            Optional(),
            Regexp(regex=r'[A-Za-z0-9]+',
                   message=('Используются недопустимые символы (разрешены'
                            'только A-Z, a-z, 0-9).'))]
    )
    submit = SubmitField('Создать')