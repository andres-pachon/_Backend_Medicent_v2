from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.Config.settings import Config
from app.database.database import db, bcrypt, jwt
from app.Routes.auth_routes import auth_bp
from app.Routes.adherencia_routes import adherencia_bp
from app.Routes.inventario_routes import inventario_bp
from app.Routes.admin_routes import admin_bp
from app.Routes.perfil_routes import perfil_bp

migrate = Migrate()

import app.models


@jwt.token_in_blocklist_loader
def bloquear_sesion_de_cuenta_inactiva(_jwt_header, jwt_payload):
    from app.models.usuario import Usuario

    try:
        id_usuario = int(jwt_payload.get("sub"))
    except (TypeError, ValueError):
        return True
    usuario = db.session.get(Usuario, id_usuario)
    return usuario is None or not usuario.activo

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

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

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/admin"
    )
    app.register_blueprint(
        perfil_bp,
        url_prefix="/api/perfil"
    )
    return app
