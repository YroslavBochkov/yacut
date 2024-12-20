# Проект YaCut c API
Проект YaCut — это сервис укорачивания ссылок. Его назначение — ассоциировать длинную пользовательскую ссылку с короткой, которую предлагает сам пользователь или предоставляет сервис.

## Ключевые возможности проекта:
- генерация коротких ссылок и связь их с исходными длинными ссылками.
- переадресация на исходный адрес при обращении к коротким ссылкам.
- возможность создания собственных коротких ссылок.

## Примеры запросов к API, варианты ответов и ошибок приведены в спецификации openapi.yml

# Запуск проекта:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/YroslavBochkov/yacut.git
```

```
cd yacut
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

* Если у вас Linux/MacOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Применить миграции для создания базы данных

```
flask db upgrade
```

Создать файл .env

Запустить проект

```
flask run
```

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green?logo=flask)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.21-red?logo=sqlalchemy)](https://www.sqlalchemy.org/)

## Автор

[Ярослав Бочков](https://github.com/YroslavBochkov)