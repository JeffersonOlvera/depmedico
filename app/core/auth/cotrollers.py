import datetime
import uuid
import jwt
from flask import (
    Blueprint,
    request,
    session,
    redirect,
    url_for,
    render_template,
    jsonify,
    flash,
)
from app.core.auth.services import AuthService
from app.core.middleware.auth_middleware import proteger_ruta

auth_routes = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    errores = {}
    form_data = request.form.to_dict()

    if request.method == "POST":
        if "cedula" in request.form:
            cedula = request.form.get("cedula")
            result = auth_service.login_by_cedula(cedula)
            if result:
                return result

        elif "idllamada" in request.form:
            user_token = request.form.get("idllamada")
            if user_token == session.get(
                "token"
            ) and datetime.datetime.now() < datetime.datetime.strptime(
                session["fechaHoraTopeToken"], "%Y/%m/%d %H:%M:%S"
            ):
                flash("Autenticación exitosa. Bienvenido!")
                session["usuario_autenticado"] = True
                return redirect(url_for("auth.home"))
            else:
                flash("Token inválido o expirado")
                errores["idllamada"] = "Token inválido o expirado"

    return render_template(
        "login.html",
        errores=errores,
        form_data=form_data,
        show_full_form=session.get("show_full_form", False),
    )


@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_routes.route("/verificar-cedula", methods=["POST"])
def verificar_cedula():
    cedula = request.form.get("cedula")
    if not cedula:
        return jsonify({"success": False, "message": "Cédula no proporcionada"})
    success, message = auth_service.verificar_cedula(cedula)
    return jsonify({"success": success, "message": message})


@auth_routes.route("/", methods=["GET"])
def index():
    if not session.get("usuario_autenticado"):
        return redirect(url_for("auth.login"))
    return redirect(url_for("auth.home"))

@auth_routes.route("/inicio", methods=["GET"])
def home_gth():
    try:
            usuario = session.get("nombreColaborador")
            rol = session.get("rol")
            autenticado = session.get("usuario_autenticado", False)

            if not autenticado:
                return redirect(url_for("auth.login"))

            if rol:
                return render_template(
                    "home_colaborador.html", usuario=usuario
                )
           
            else:
                return render_template("error.html", mensaje="Rol no autorizado"), 403

    except Exception as e:
            print("[ERROR] home:", e)
            return render_template("error.html", mensaje="Error interno del servidor"), 500
        
@auth_routes.route("/home", methods=["GET"])
def home():
    try:
        usuario = session.get("nombreColaborador")
        rol = session.get("rol")
        autenticado = session.get("usuario_autenticado", False)

        if not autenticado:
            return redirect(url_for("auth.login"))

        if rol == "doctora":
            return render_template("dashboard/dashboard_ocupacional.html", usuario=usuario)
        elif rol == "doctora2":
            return render_template(
                "dashboard/dashboard_preocupacional.html", usuario=usuario
            )
        elif rol == "GTH":
            return render_template(
                "tokens.html", usuario=usuario
            )
        elif rol in ["colaborador", "externo", "admin"]:
            return render_template("home_colaborador.html", usuario=usuario)
        else:
            return render_template("error.html", mensaje="Rol no autorizado"), 403

    except Exception as e:
        print("[ERROR] home:", e)
        return render_template("error.html", mensaje="Error interno del servidor"), 500


@auth_routes.route("/tokens", methods=["GET"])
@proteger_ruta(roles_permitidos=["doctora", "admin", "GTH"])
def view_tokens():
    return render_template("tokens.html")


@auth_routes.route("/validate_token", methods=["POST"])
def validate_token():
    token = request.form.get("token")
    if not token:
        flash("Token no proporcionado", "error")
        return render_template("login.html")
    try:
        decoded_token = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        flash("Token válido", "success")
        session["usuario_autenticado"] = True
        session["rol"] = "externo"
        session["externo"] = True
        return redirect(url_for("auth.home"))
    except jwt.ExpiredSignatureError:
        flash("Token expirado", "error")
        return render_template("login.html"), 401
    except jwt.InvalidTokenError:
        flash("Token inválido", "error")
        return render_template("login.html"), 401


@auth_routes.route("/", methods=["POST"])
def generate_tokens():
    cantidad = request.form.get("tokenAmount")
    try:
        count = int(cantidad)
        if count <= 0 or count > 100:
            return (
                jsonify({"message": "El número de tokens debe estar entre 1 y 100"}),
                400,
            )

        tokens = []
        for _ in range(count):
            token_payload = {
                "user_id": str(uuid.uuid4()),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=48),
                "iat": datetime.datetime.utcnow(),
                "token_id": str(uuid.uuid4()),
            }
            token = jwt.encode(token_payload, "SECRET_KEY", algorithm="HS256")
            tokens.append(token)

        flash(f"Se generaron {count} tokens correctamente", "success")
        return render_template("tokens.html", tokens={"tokens": tokens})

    except Exception as e:
        return jsonify({"message": f"Error al generar tokens: {str(e)}"}), 500
