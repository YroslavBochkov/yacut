from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp

class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка', 
        validators=[
            DataRequired(message='Обязательное поле'), 
            URL(message='Некорректный URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки', 
        validators=[
            Optional(), 
            Length(max=16, message='Максимальная длина 16 символов'),
            Regexp(r'^[a-zA-Z0-9]+$', message='Только буквы и цифры')
        ]
    )
    submit = SubmitField('Создать')
