from flask import render_template, redirect, flash, url_for
from . import app, db
from .forms import URLMapForm
from .models import URLMap
from .utils import get_unique_short_id

@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLMapForm()
    short_url = None

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data or get_unique_short_id()

        # Проверка корректности custom_id
        if not custom_id.isalnum() or len(custom_id) > 16:
            flash('Указан недопустимый вариант короткой ссылки', 'error')
            return render_template('index.html', form=form)

        # Проверка существования custom_id
        existing = URLMap.query.filter_by(short=custom_id).first()
        if existing:
            flash('Предложенный вариант короткой ссылки уже существует.', 'error')
            return render_template('index.html', form=form)

        # Создание новой ссылки
        new_url = URLMap(original=original_link, short=custom_id)
        db.session.add(new_url)
        db.session.commit()

        short_url = url_for('redirect_to_original', short_id=custom_id, _external=True)
        flash(short_url, 'url')

    return render_template('index.html', form=form, short_url=short_url)

@app.route('/<short_id>')
def redirect_to_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
