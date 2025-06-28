from pydantic import BaseModel

class CertificadoSchema(BaseModel):
    usuario_actualizacion: str = ""
    nombre: str = ""
    cedula: str = ""
    nhc: str = ""
    edad: str = ""
    sexo: str = ""
    cargo: str = ""
    tiempo_cargo: str = ""
    fecha_emision: str = ""
    
    ingreso: str = ""
    periodico: str = ""
    reintegro: str = ""
    
    apto: str = ""
    apto_observacion: str = ""
    apto_limitaciones: str = ""
    no_apto: str = ""
    apto_detalles: str = ""
    
    recomendaciones: str = ""
    firma_colaborador: str = ""
    firma_doc: str = ""
    status: str = ""
