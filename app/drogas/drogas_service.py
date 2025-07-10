import os
from flask import jsonify
import requests
from datetime import datetime


class DrogaService:

    BASE_URL = os.getenv("BASE_URL", "https://192.168.137.16:47096")
    API_GUARDAR = f"{BASE_URL}/FormDepMedico/Guardar/fichaDrogas"
    API_ACTUALIZAR = f"{BASE_URL}/FormDepMedico/Actualizar/fichaDrogas"
    API_CARGAR = f"{BASE_URL}/FormDepMedico/Cargar/fichaDrogas"
    API_LISTAR = f"{BASE_URL}/FormDepMedico/Listar/fichaDrogas"

    HEADERS = {
        "AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s",
        "Content-Type": "application/json",
    }

    def enviar_formulario(self, payload):
        """Envía el formulario a la API"""

        print(f"PAYLOAD RECIBIDO: {payload}")

        try:

            response = requests.post(
                self.API_GUARDAR,
                json=payload,
                headers=self.HEADERS,
                verify=False,
                timeout=30,
            )
            print("TEEEEEEEEEEEEST")
            print(f"Código de estado: {response.status_code}")
            print(f"Respuesta: {response.text}")

            if response.status_code == 200:
                return {"success": True, "message": "Formulario enviado correctamente"}
            else:
                return {
                    "success": False,
                    "message": f"Error API - Código: {response.status_code}",
                }

        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout al enviar el formulario"}
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Error de conexión al enviar el formulario",
            }
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}

    def obtener_datos_ingreso(self, cedula):
        try:
            payload = {"cedula": cedula}
            response = requests.post(
                self.API_URL, json=payload, headers=self.HEADERS, verify=False
            )

            if response.status_code == 201:
                return response.json()
            else:
                return None
        except Exception as e:
            raise RuntimeError(f"Error al llamar a la API: {e}")

    def validar_fecha_ingreso(self, fecha_ingreso_str):
        fecha_tope = datetime.strptime(f"{datetime.now().year}-12-31", "%Y-%m-%d")
        fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%m/%d/%Y %I:%M:%S %p")
        return fecha_ingreso <= fecha_tope, fecha_ingreso

    def obtener_todas(self, rango_fechas={}):
        """Obtiene todas las fichas de drogas en un rango de fechas"""
        print("TESSST")
        try:

            payload = {"fechaDesde": "2024-02-24", "fechaHasta": "2030-05-02"}

            response = requests.post(
                self.API_LISTAR, headers=self.HEADERS, verify=False, json=payload
            )

            print(response, response.status_code)
            if response.status_code in [200, 201]:

                return jsonify(response.json())
            else:

                return (
                    jsonify(
                        {
                            "error": f"Error al obtener datos de API. Código de respuesta: {response.status_code}"
                        }
                    ),
                    response.status_code,
                )
        except requests.exceptions.RequestException as e:
            return (
                jsonify(
                    {"error": f"Ocurrió un error al realizar la petición al API: {e}"}
                ),
                500,
            )

    def obtener_por_ced(self, cedula):
        try:
            print("CEDULA RECIBIDAAAA: " + cedula)

            payload = {"cedula": cedula}

            response = requests.post(
                self.API_CARGAR,
                json=payload,
                headers=self.HEADERS,
                verify=False,
                timeout=30,
            )

            print(f"Código de estado: {response.status_code}")

            if response.status_code == 201:
                return response
            else:
                return {
                    "success": False,
                    "message": f"Error API - Código: {response.status_code}",
                }

        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout al enviar el formulario"}
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Error de conexión al enviar el formulario",
            }
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}

    def actualizar_formulario(self, payload):
        """Envía el formulario a la API"""

        print(f"PAYLOAD RECIBIDO: {payload}")

        try:

            response = requests.post(
                self.API_ACTUALIZAR,
                json=payload,
                headers=self.HEADERS,
                verify=False,
                timeout=30,
            )
            print(f"Código de estado DROGA ACTU: {response.status_code}")
            print(f"Respuesta DROGA ACTU: {response.text}")

            if response.status_code == 200:
                return {"success": True, "message": "Formulario enviado correctamente"}
            else:
                return {
                    "success": False,
                    "message": f"Error API - Código: {response.status_code}",
                }

        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout al enviar el formulario"}
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Error de conexión al enviar el formulario",
            }
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}
