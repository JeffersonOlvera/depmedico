import logging
import os
from dotenv import load_dotenv
from app.core.utils.logging import setup_logging
from flask import Flask, redirect, url_for
from app.core.auth.cotrollers import auth_routes
from app.colaborador.colaborador_routes import colaborador_routes
from app.ocupacional.ocupacional_routes import ocupacional_routes
from app.preocupacional.preocupacional_routes import preocupacional_routes
from app.seguimiento.seguimiento_routes import seguimiento_routes
from app.drogas.drogas_routes import drogas_routes
from app.consentimiento.consentimiento_routes import consentimiento_routes
from app.certificado.certificado_routes import certificado_routes


def create_app():
    # Primero determinar el entorno
    app_env = os.getenv("APP_ENV", "production")

    # Cargar el archivo .env correspondiente ANTES de obtener las variables
    env_file = ".env.dev" if app_env == "development" else ".env"
    load_dotenv(env_file)

    # AHORA obtener las variables de entorno (después de cargarlas)
    BASE_URL = os.getenv("BASE_URL", "https://192.168.137.16:47096")
    PORT = os.getenv("PORT", 8003)

    print(f"Archivo .env cargado: {env_file}")
    print(f"BASE_URL: {BASE_URL}")
    print(f"APP_ENV: {app_env}")

    app = Flask(__name__)
    app.secret_key = os.getenv("KEY", "test_123")
    setup_logging(app, log_level=logging.DEBUG)

    # Registrar blueprints
    app.register_blueprint(auth_routes, url_prefix="/")

    app.register_blueprint(colaborador_routes, url_prefix="/colaborador")
    app.register_blueprint(ocupacional_routes, url_prefix="/ocupacional")
    app.register_blueprint(preocupacional_routes, url_prefix="/preocupacional")
    app.register_blueprint(seguimiento_routes, url_prefix="/seguimiento")
    app.register_blueprint(drogas_routes, url_prefix="/drogas")
    app.register_blueprint(consentimiento_routes, url_prefix="/consentimiento")
    app.register_blueprint(certificado_routes, url_prefix="/certificado")

    # Manejador de error 404
    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8003)
