from flask import Flask

from app import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_db()

    from app.routes.webhook import webhook_bp
    from app.routes.api import api_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(webhook_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)

    return app
