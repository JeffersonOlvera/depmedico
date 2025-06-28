from flask import Blueprint, render_template, session, redirect, url_for, request
from app.consentimiento.consentimiento_controller import ConsentimientoController
from app.core.middleware.auth_middleware import proteger_ruta
from app.consentimiento.consentimiento_service import ConsentimientoService

consentimiento_routes = Blueprint("consentimiento", __name__)
service = ConsentimientoService()
controller = ConsentimientoController(service)


@consentimiento_routes.route("/")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def form():
    return controller.form()


@consentimiento_routes.route("/guardar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def guardar():
    return controller.guardar()


@consentimiento_routes.route("/cargar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def cargar():
    return controller.cargar()


@consentimiento_routes.route("/actualizar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def actualizar():
    return controller.actualizar()

@consentimiento_routes.route("/listar")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def listar():
    return controller.listar()

@consentimiento_routes.route("/dashboard")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def dashboard():
    return controller.dashboard()


@consentimiento_routes.route("/pdf", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def pdf():
    return controller.pdf()


@consentimiento_routes.route("/excel", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def excel():
    return controller.excel()


@consentimiento_routes.route("/formulario_success")
def formulario_success():
    return render_template("formulario_success.html")
