from flask import Flask
from flask_cors import CORS

from main.controllers.cache import cache

DATABASE_URI = 'mysql://root:123456@127.0.0.1/cache'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(cache)


cors = CORS(send_wildcard=True)
cors.init_app(app)

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
