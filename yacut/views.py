from flask import (
    flash,
    redirect,
    render_template,
    abort
)

from yacut import app
from yacut.forms import URLForm
from yacut.models import URLMap
from yacut.settings import Config


@app.route('/', methods=('GET', 'POST'))
def page_for_generate_url():
    """Отображает форму для генерации короткой ссылки."""
    form = URLForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        url_map = URLMap.create(
            original=form.original_link.data,
            short=form.custom_id.data or None
        )
        flash(Config.get_short_link(url_map.short), 'url')
    except URLMap.URLValidationError as e:
        flash(str(e), 'error')

    return render_template('index.html', form=form)


@app.route('/<string:url>')
def redirect_short_url(url):
    """Выполняет переадресацию с короткой ссылки на оригинальную."""
    try:
        return redirect(URLMap.get_by_short(url).original)
    except URLMap.URLValidationError:
        abort(404)
