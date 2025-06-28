from flask import Blueprint, render_template, session, redirect, url_for, request

# from app.core.auth.cotrollers import AuthController
from app.core.auth.cotrollers import home as AuthHome
from app.core.middleware.auth_middleware import proteger_ruta

colaborador_routes = Blueprint("colaborador", __name__)
# auth_controller = AuthController()


@colaborador_routes.route("/registro-ocupacional")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def registro_ocupacional():
    return render_template("forms/colaborador/registro_ocupacional.html")


@colaborador_routes.route("/registro-certificado")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def registro_certificado():
    return render_template("forms/colaborador/registro_certificado.html")


@colaborador_routes.route("/registro-preocupacional")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def registro_preocupacional():
    return render_template("forms/colaborador/registro_preocupacional.html")


@colaborador_routes.route("/registro-consentimiento")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def registro_consentimiento():
    return render_template("forms/colaborador/registro_consentimiento.html")


@colaborador_routes.route("/registro-consumo-drogas")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def registro_consumo_drogas():
    return render_template("forms/colaborador/registro_drogas.html")


@colaborador_routes.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("auth.login"))


@colaborador_routes.route("/", methods=["GET"])
def index():
    return redirect(url_for("auth.home"))


@colaborador_routes.route("/", methods=["GET", "POST"])
def home():
    print("Home route accessed")
    # session['usuario_autenticado'] = True
    return AuthHome()
