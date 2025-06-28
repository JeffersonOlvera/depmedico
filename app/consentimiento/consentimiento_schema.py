from pydantic import BaseModel, constr

class ConsentimientoSchema(BaseModel):
    nombre: str
    cedula: str
    fecha: str
    firma: str
