from datetime import datetime, timedelta
import secrets
import re
from flask import flash, redirect, render_template, request, session, url_for
from markupsafe import Markup
import requests
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import current_app


class AuthService:
    """
    Servicio para manejar la autenticación y operaciones relacionadas con la seguridad.
    Implementa el principio de responsabilidad única y segregación de interfaces.
    """

    def __init__(self, repository=None):
        """
        Constructor que permite inyección de dependencias para facilitar pruebas unitarias.
        """
        # self.repository = repository or AuthRepository()
        pass

    def login_by_cedula(self, cedula):
        """
        Autentica a un colaborador usando su número de cédula.

        Args:
            cedula (str): Número de cédula del colaborador

        Returns:
            Rendered template o None: Template renderizado si hay que mostrar el formulario completo
        """
        # Lista de usuarios del área médica (hardcodeados)
        usuarios_area_medica = [
            {
                "cedula": "1717243149",
                "nombre": "MACIAS VERA GINA LUISANA",
                "rol": "doctora2",
            },
            {
                "cedula": "0925808552",
                "nombre": "REYES VERA KATHERINE NARCISA",
                "rol": "doctora",
            },
            {"cedula": "0910882604", "nombre": "FATIMA GUERRERO", "rol": "doctora"},
            {"cedula": "0955624507", "nombre": "RICARDO VELIZ", "rol": "admin"},
            {
                "cedula": "0917140436",
                "nombre": "GAVILANES ORTIZ JORGE JAVIER",
                "rol": "GTH",
            },
            {
                "cedula": "0502367642",
                "nombre": "SALAZAR FIALLOS MARITZA YADIRA",
                "rol": "GTH",
            },
        ]

        errores = {}
        form_data = request.form.to_dict()
        # Validación básica de la cédula
        if not cedula or len(cedula) < 10:
            flash("Cédula no válida")
            return render_template("login.html", errores=errores, form_data=form_data)

        # Buscar usuario en la lista local primero para asignar rol
        usuario = next((u for u in usuarios_area_medica if u["cedula"] == cedula), None)

        if usuario:
            session["nombreColaborador"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            print(
                f"[DEBUG] Usuario encontrado localmente: {usuario['nombre']}, Rol: {usuario['rol']}"
            )
        else:
            session["nombreColaborador"] = "USUARIO"
            session["rol"] = "colaborador"
            print("[DEBUG] Usuario no encontrado localmente, asignando rol por defecto")

        current_app.logger.info(f'[DEBUG] ROL: {session["rol"]}')
        # Hacer la llamada a la API
        try:
            response = requests.post(
                "https://192.168.137.16:47081/api/GTHLanbot",
                headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                params={"identificacion": cedula},
                verify=False,
            )

            current_app.logger.info(f"API Response: {response}")

            print(f"[DEBUG] Respuesta de la API: Status {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Guardar datos en sesión
                session["nombreColaborador"] = data.get(
                    "nombreColaborador", session.get("nombreColaborador", "")
                )
                session["token"] = data.get("token")
                session["fechaHoraTopeToken"] = data.get("fechaHoraTopeToken")
                session["correo"] = data.get("correo")
                session["estatusColaborador"] = data.get("estatusColaborador")
                session["ErrorID"] = data.get("ErrorID")
                session["ErrorMessage"] = data.get("ErrorMessage")
                session["cedula"] = cedula

                # print(f'[DEBUG] Token recibido: {session["token"]}')
                current_app.logger.info(f'[DEBUG] Token recibido: {session["token"]}')
                print(
                    f'[DEBUG] Fecha de expiración del token: {session["fechaHoraTopeToken"]}'
                )
                print(
                    f'[DEBUG] Datos de sesión: {session.get("nombreColaborador")}, {session.get("rol")}'
                )

                # Verificar estatus del colaborador
                if session["estatusColaborador"] in ["ALTA", "BAJA"]:
                    print(
                        "[DEBUG] Estatus de colaborador válido. Mostrando formulario completo."
                    )
                    flash(
                        Markup(
                            session.get("ErrorMessage", "Token generado correctamente")
                        )
                    )
                    session["show_full_form"] = True

                    return render_template(
                        "login.html",
                        form_data=form_data,
                        show_full_form=True,
                        errores=errores,
                    )
                else:
                    flash("Tu estatus no permite iniciar sesión")
                    return render_template(
                        "login.html", show_full_form=False, errores=errores
                    )
            else:
                flash("Datos no válidos o error en la conexión con el sistema")
                return render_template(
                    "login.html", show_full_form=False, errores=errores
                )

        except requests.exceptions.RequestException as e:
            flash("No se pudo establecer una conexión con el sistema de autenticación.")
            print(f"[ERROR] Error al conectarse a la API: {e}")
            return render_template("login.html", show_full_form=False, errores=errores)

        return render_template("login.html", errores=errores)

    def verificar_cedula(self, cedula):
        """
        Verifica si una cédula está registrada en el sistema sin iniciar sesión.

        Args:
            cedula (str): Número de cédula a verificar

        Returns:
            tuple: (success, message)
                - success (bool): True si la cédula es válida
                - message (str): Mensaje descriptivo
        """
        if not cedula:
            return False, "Cédula es obligatoria"

        if not self._validate_cedula_format(cedula):
            return False, "Formato de cédula inválido"

        # Aquí puedes implementar la validación con tu API
        # is_valid, _ = self.repository.validate_cedula(cedula)

        # Por ahora, simular validación
        return True, "Cédula verificada correctamente"

    def _validate_cedula_format(self, cedula):
        """
        Valida el formato de la cédula ecuatoriana.

        Args:
            cedula (str): Número de cédula

        Returns:
            bool: True si el formato es válido
        """
        if not cedula or len(cedula) != 10:
            return False

        if not cedula.isdigit():
            return False

        # Validación básica del dígito verificador de cédula ecuatoriana
        try:
            digits = [int(d) for d in cedula]
            check_digit = digits[-1]

            # Algoritmo de validación
            odd_sum = sum(digits[i] for i in range(0, 9, 2))
            even_sum = sum(
                min(digits[i] * 2, digits[i] * 2 - 9) for i in range(1, 9, 2)
            )

            total = odd_sum + even_sum
            calculated_check = (10 - (total % 10)) % 10

            return calculated_check == check_digit
        except:
            return False

    def logout(self, token=None):
        """
        Cierra la sesión de un usuario.

        Args:
            token (str, optional): Token JWT a invalidar

        Returns:
            tuple: (success, message)
        """
        if token:
            # Si se usa JWT, añadir el token a la lista negra
            # self.repository.add_token_to_blacklist(token)
            pass

        return True, "Sesión cerrada correctamente"

    def verify_token(self, token):
        """
        Verifica si un token JWT es válido.

        Args:
            token (str): Token JWT a verificar

        Returns:
            tuple: (is_valid, user_data)
                - is_valid (bool): True si el token es válido
                - user_data (dict): Datos del usuario si el token es válido
        """
        if not token:
            return False, None

        # Verificar si el token está en la lista negra
        if self.repository.is_token_blacklisted(token):
            return False, None

        try:
            # Decodificar token
            # payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            payload = "test"

            # Verificar expiración
            exp_timestamp = payload.get("exp")
            if (
                exp_timestamp is None
                or datetime.fromtimestamp(exp_timestamp) < datetime.now()
            ):
                return False, None

            # Obtener datos del usuario
            username = payload.get("sub")
            if not username:
                return False, None

            user = self.repository.get_user_by_username(username)
            if not user:
                return False, None

            user_data = {
                "id": user.id,
                "username": user.username,
                "roles": payload.get("roles", []),
            }

            return True, user_data

        except Exception as e:
            # Manejar errores de decodificación
            return False, None

    def validar_token_recuperacion(self, token):
        """
        Valida un token de recuperación de contraseña.

        Args:
            token (str): Token de recuperación

        Returns:
            tuple: (success, user_id)
        """
        if not token:
            return False, None

        # Verificar token en la BD
        token_data = self.repository.get_password_reset_token(token)

        if not token_data:
            return False, None

        # Verificar si el token ha expirado
        if token_data["expiration"] < datetime.now():
            return False, None

        return True, token_data["user_id"]
