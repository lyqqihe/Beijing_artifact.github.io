from flask import Flask

app = Flask(__name__)

# 导入路由
from app import routes

def create_app():
    app = Flask(__name__)

    with app.app_context():
        from . import routes

    return app