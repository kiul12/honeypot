from flask import Flask
from dotenv import load_dotenv

from .extensions import db, migrate, login_manager, csrf, limiter, create_redis_client
from .models import User


def create_app():
    load_dotenv()
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.config.from_object('config.Config')

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    limiter.init_app(app)
    limiter.storage_uri = f"redis://{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/{app.config['REDIS_DB']}"

    # Redis client
    app.redis = create_redis_client(app)

    # Blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.admin import admin_bp
    from .blueprints.api import api_bp
    from .blueprints.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/admin')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app