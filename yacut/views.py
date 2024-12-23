from http import HTTPStatus
from flask import (
    redirect,
    render_template,
    abort,
    flash,
    url_for,
    request
)
from yacut import app
from yacut.forms import URLForm
from yacut.models import URLMap

DUPLICATE_SHORT_URL_ERROR = (
    'Предложенный вариант короткой ссылки уже существует.'
)


@app.route('/', methods=('GET', 'POST'))
def page_for_generate_url():
    """Отображает форму для генерации короткой ссылки."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    try:
        url_map = URLMap.create(
            original=form.original_link.data,
            short=form.custom_id.data
        )
        short_url = url_for('redirect_short_url', url=url_map.short, _external=True)
        return render_template(
            'index.html',
            form=form,
            short_url=short_url
        )
    except (ValueError, RuntimeError) as e:
        flash(str(e))
        return render_template('index.html', form=form)


@app.route('/<string:url>')
def redirect_short_url(url):
    """Выполняет переадресацию с короткой ссылки на оригинальную."""
    url_map = URLMap.query.filter_by(short=url).first()
    if not url_map:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)
