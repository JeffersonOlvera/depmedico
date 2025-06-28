import requests
from flask import jsonify
from typing import Optional, Dict, Any, Union


class ApiService:
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
        timeout: int = 30,
    ):
        """
        Inicializa el servicio con una URL base, encabezados opcionales, verificación SSL y timeout.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    def _make_request(
        self, endpoint: str, method: str = "POST", payload: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Método interno para hacer una solicitud HTTP genérica.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                json=payload,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )

            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": response.text,
                }

        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout en la solicitud"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Error de conexión"}
        except Exception as e:
            return {"success": False, "message": f"Error inesperado: {str(e)}"}

    def post(self, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request(endpoint=endpoint, method="POST", payload=payload)

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request(endpoint=endpoint, method="GET", payload=params)

    def put(self, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request(endpoint=endpoint, method="PUT", payload=payload)

    def delete(self, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request(endpoint=endpoint, method="DELETE", payload=payload)
