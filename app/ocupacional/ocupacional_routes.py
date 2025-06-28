from flask import Blueprint, render_template, session, redirect, url_for, request
from app.ocupacional.ocupacional_controller import OcupacionalController
from app.core.middleware.auth_middleware import proteger_ruta

ocupacional_routes = Blueprint("ocupacional", __name__)
controller = OcupacionalController()


@ocupacional_routes.route("/")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "admin", "GTH", "externo"])
def form():
    return controller.form()


@ocupacional_routes.route("/guardar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def guardar():
    return controller.guardar()

@ocupacional_routes.route("/validar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def validar():
    return controller.validar()


@ocupacional_routes.route("/cargar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def cargar():
    return controller.cargar()


@ocupacional_routes.route("/actualizar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def actualizar():
    return controller.actualizar()


@ocupacional_routes.route("/dashboard")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def dashboard():
    return controller.dashboard()

@ocupacional_routes.route("/listar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def listar():
    return controller.listar()


@ocupacional_routes.route("/pdf", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def pdf():
    return controller.pdf()


@ocupacional_routes.route("/excel", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def excel():
    return controller.excel()


@ocupacional_routes.route("/formulario_success")
def formulario_success():
    return render_template("formulario_success.html")
