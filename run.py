from yacut import app, db
from settings import Config

if __name__ == '__main__':
    app.run(
        host=Config.HOST, 
        port=Config.PORT
    )
