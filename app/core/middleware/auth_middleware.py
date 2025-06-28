# app/middlewares/auth_middleware.py
from functools import wraps
from flask import session, redirect, url_for, flash


def proteger_ruta(roles_permitidos=None):
    """
    Middleware para proteger rutas según autenticación y rol.

    :param roles_permitidos: Lista de roles que pueden acceder a la ruta.
    """

    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            if not session.get("usuario_autenticado"):
                flash("Debes iniciar sesión primero.", "error")
                return redirect(url_for("auth.login"))

            rol = session.get("rol")

            if roles_permitidos and rol not in roles_permitidos:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("auth.home"))

            return f(*args, **kwargs)

        return funcion_decorada

    return decorador
