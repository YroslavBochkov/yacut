from http import HTTPStatus

from flask import jsonify, render_template

from yacut import app, db


class URLValidationError(Exception):
    """Ошибка для валидаторов генерации короткой ссылки."""

    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidAPIUsage(Exception):
    """Ошибка для API-интерфейса."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Метод возвращает словарь с сообщением."""
        return dict(message=self.message)


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Хендлер для ошибок api."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    """Хендлер для ошибки 404."""
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error):
    """Хендлер для ошибки 500."""
    db.session.rollback()
    return render_template('errors/500.html'), HTTPStatus.INTERNAL_SERVER_ERROR