from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # Initialize migrate without the app object

def dateformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = '12345'
    csrf = CSRFProtect(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Now pass in the app object to migrate
    login_manager.login_view = 'auth.login'
    app.jinja_env.filters['dateformat'] = dateformat
    # User loader function for Flask-Login
    from .models.users import User  # Ensure this import is correct for your package structure

    @login_manager.user_loader
    def user_loader(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app