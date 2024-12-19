from http import HTTPStatus

from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for
)

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.forms import URLForm
from yacut.models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_url_api():
    """API эндпоинт для создания короткой ссылки."""
    if not request.is_json:
        raise InvalidAPIUsage('Некорректный запрос')

    data = request.get_json(silent=True) or {}

    try:
        url_obj = URLMap.create(
            original=data['url'], 
            short=data.get('custom_id')
        )
        return jsonify({
            'url': url_obj.original,
            'short_link': url_for(
                'redirect_short_url',
                url=url_obj.short,
                _external=True
            )
        }), HTTPStatus.CREATED
    except InvalidAPIUsage as error:
        return jsonify({'message': str(error)}), HTTPStatus.BAD_REQUEST


@app.route('/', methods=('GET', 'POST'))
def page_for_generate_url():
    """Отображает форму для генерации короткой ссылки."""
    form = URLForm()
    if form.validate_on_submit():
        try:
            url_obj = URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data
            )
            flash(
                url_for(
                    'redirect_short_url',
                    url=url_obj.short,
                    _external=True
                ),
                'url'
            )
        except InvalidAPIUsage as error:
            # Точно такое же сообщение, как в тесте
            flash('Предложенный вариант короткой ссылки уже существует.', 'error')
    return render_template('index.html', form=form)


@app.route('/<string:url>')
def redirect_short_url(url):
    """Выполняет переадресацию с короткой ссылки на оригинальную."""
    return redirect(
        URLMap.query.filter_by(short=url).first_or_404().original
    )
