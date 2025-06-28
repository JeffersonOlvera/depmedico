from flask import Blueprint, render_template, session, redirect, url_for, request
from app.certificado.certificado_controller import CertificadoController
from app.core.middleware.auth_middleware import proteger_ruta
import requests

certificado_routes = Blueprint("certificado", __name__)
controller = CertificadoController()


@certificado_routes.route("/")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "admin", "GTH", "doctora2", "externo"])
def form():
    return controller.form()


@certificado_routes.route("/guardar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def guardar():
    return controller.guardar()


@certificado_routes.route("/cargar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH", "externo"])
def cargar():
    return controller.cargar()


@certificado_routes.route("/listar")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def listar():
    return controller.listar()


@certificado_routes.route("/actualizar", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def actualizar():
    return controller.actualizar()


@certificado_routes.route("/dashboard")
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def dashboard():
    return controller.dashboard()


@certificado_routes.route("/pdf", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def pdf():
    return controller.pdf()


@certificado_routes.route("/excel", methods=["GET", "POST"])
@proteger_ruta(roles_permitidos=["colaborador", "doctora", "doctora2", "admin", "GTH"])
def excel():
    return controller.excel()


@certificado_routes.route("/formulario_success")
def formulario_success():
    return render_template("formulario_success.html")
