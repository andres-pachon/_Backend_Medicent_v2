from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.Config.settings import Config
from app.database.database import db, bcrypt, jwt
from app.Routes.auth_routes import auth_bp
from app.Routes.adherencia_routes import adherencia_bp
from app.Routes.inventario_routes import inventario_bp

migrate = Migrate()

import app.models

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Registro de Blueprints
    app.register_blueprint(
        auth_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        adherencia_bp,
        url_prefix="/api/adherencia"
    )

    app.register_blueprint(
        inventario_bp,
        url_prefix="/api/inventario"
    )

    return app