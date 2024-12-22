from flask import (
    redirect,
    render_template,
    abort
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
            short=form.custom_id.data or None
        )
        return render_template(
            'index.html',
            form=form,
            short_url=url_map.short
        )
    except ValueError as e:
        return render_template('index.html', form=form, error=str(e))


@app.route('/<string:url>')
def redirect_short_url(url):
    """Выполняет переадресацию с короткой ссылки на оригинальную."""
    try:
        return redirect(URLMap.get_by_short(url).original)
    except ValueError:
        abort(404)
