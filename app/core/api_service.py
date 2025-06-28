# app/core/api_service.py

import requests


class BaseApiService:
    def __init__(self, base_url, resource, headers=None):
        self.base_url = base_url.rstrip("/")
        self.resource = resource
        self.headers = headers or {}

    def post(self, endpoint, payload, timeout=30):
        try:
            url = f"{self.base_url}/{endpoint}/{self.resource}"
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                verify=False,
                timeout=timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout al enviar la solicitud"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Error de conexión"}
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}

    def get(self, endpoint, params=None, timeout=30):
        try:
            url = f"{self.base_url}/{endpoint}/{self.resource}"
            
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                verify=False,
                timeout=timeout,
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}

    def _handle_response(self, response):
        try:
            if response.status_code in [200, 201]:
                try:
                    return {"success": True, "data": response.json()}
                except ValueError:
                    return {"success": True, "data": response.text}  # Retorna como texto plano
            return {
                "success": False,
                "message": f"Error API - Código: {response.status_code}",
                "response": response.text,
            }
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}

