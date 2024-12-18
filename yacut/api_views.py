from flask import jsonify, request, url_for
from . import app, db
from .models import URLMap
from .utils import get_unique_short_id

@app.route('/api/id/', methods=['POST'])
def create_short_url():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"message": "Отсутствует обязательное поле 'url'"}), 400

    original_url = data['url']
    custom_id = data.get('custom_id')

    if custom_id:
        if len(custom_id) > 16:
            return jsonify({"message": "Указано недопустимое имя для короткой ссылки"}), 400
        
        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify({"message": "Предложенный вариант короткой ссылки уже существует"}), 400
        
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    new_url = URLMap(original=original_url, short=short_id)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        "url": original_url,
        "short_link": url_for('redirect_to_original', short_id=short_id, _external=True)
    }), 201

@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    
    if not url_map:
        return jsonify({"message": "Указанный id не найден"}), 404
    
    return jsonify({"url": url_map.original}), 200

