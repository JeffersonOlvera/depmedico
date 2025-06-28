from datetime import datetime
from app.core.api_service import BaseApiService


class ConsentimientoService(BaseApiService):
    def __init__(self):
        super().__init__(
            base_url="https://192.168.137.16:47096/FormDepMedico",
            resource="fichaConsInformado",
            headers={
                "AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s",
                "Content-Type": "application/json",
            },
        )

    def enviar_formulario(self, payload):
        return self.post("Guardar", payload)

    def actualizar_formulario(self, payload):
        response = self.post("Actualizar", payload)
        print("Respuesta de actualizar_formulario:", response)
        return response

    def obtener_por_ced(self, cedula):
        return self.post("Cargar", {"cedula": cedula})

    def obtener_todas(self, fecha_desde="2024-02-24", fecha_hasta="2030-05-02"):

        return self.post("Listar", {
            "fechaDesde": fecha_desde,
            "fechaHasta": fecha_hasta,
        })

    def validar_fecha_ingreso(self, fecha_ingreso_str):
        fecha_tope = datetime.strptime(f"{datetime.now().year}-12-31", "%Y-%m-%d")
        fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%m/%d/%Y %I:%M:%S %p")
        return fecha_ingreso <= fecha_tope, fecha_ingreso
