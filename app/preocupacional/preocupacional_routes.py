from flask import Blueprint, render_template, session, redirect, url_for, request
from app.preocupacional.preocupacional_controller import PreocupacionalController
from app.core.middleware.auth_middleware import proteger_ruta

preocupacional_routes = Blueprint("preocupacional", __name__)
controller = PreocupacionalController()


@preocupacional_routes.route("/")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def form():
    return controller.form()


@preocupacional_routes.route("/guardar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def guardar():
    return controller.guardar()


@preocupacional_routes.route("/cargar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def cargar():
    return controller.cargar()


@preocupacional_routes.route("/actualizar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def actualizar():
    return controller.actualizar()


@preocupacional_routes.route("/dashboard")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def dashboard():
    print("ACCEDIENDO AL DASHBOARD DE PREOCUPACIONAL")
    return controller.dashboard()

@preocupacional_routes.route("/listar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def listar():
    return controller.listar()


@preocupacional_routes.route("/pdf", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def pdf():
    return controller.pdf()


@preocupacional_routes.route("/excel", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def excel():
    return controller.excel()


@preocupacional_routes.route("/formulario_success")
def formulario_success():
    return render_template("formulario_success.html")
