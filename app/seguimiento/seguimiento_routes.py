from flask import Blueprint, render_template, session, redirect, url_for, request
from app.seguimiento.seguimiento_controller import SeguimientoController
from app.core.middleware.auth_middleware import proteger_ruta

seguimiento_routes = Blueprint("seguimiento", __name__)
controller = SeguimientoController()


@seguimiento_routes.route("/")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def form():
    return controller.form()


@seguimiento_routes.route("/guardar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def guardar():
    return controller.guardar()


@seguimiento_routes.route("/cargar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def cargar():
    return controller.cargar()


@seguimiento_routes.route("/actualizar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def actualizar():
    return controller.actualizar()


@seguimiento_routes.route("/dashboard")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def dashboard():
    return controller.dashboard()



@seguimiento_routes.route("/listar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def listar():
    return controller.listar()

@seguimiento_routes.route("/pdf", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def pdf():
    return controller.pdf()


@seguimiento_routes.route("/excel", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def excel():
    return controller.excel()


@seguimiento_routes.route("/formulario_success")
def formulario_success():
    return render_template("formulario_success.html")
