from datetime import datetime
from flask import flash, redirect, render_template, request, session, url_for
from pydantic import ValidationError
from app.consentimiento.consentimiento_service import ConsentimientoService
from flask import (
    Blueprint,
    json,
    request,
    flash,
    redirect,
    url_for,
    render_template,
    jsonify,
    session,
    current_app,
    send_file,
)
from pydantic import BaseModel, constr, validator, ValidationError
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from functools import wraps
import os
import json
import re
import requests
import pandas as pd
import base64
from typing import Optional
import fitz  # Manipular el PDF
from io import BytesIO
import io
import openpyxl
from openpyxl import Workbook
from PIL import Image
import PIL
from tempfile import NamedTemporaryFile
import urllib3
from openpyxl.drawing.image import Image as ExcelImage
from app.core.utils.resize_img import resize_image_base64
from app.core.utils.resize_img import base_firma_doc
from app.consentimiento.consentimiento_schema import ConsentimientoSchema

service = ConsentimientoService()

# Carpeta donde guardarás temporalmente las firmas (crear si no existe)
FIRMAS_PATH = os.path.join("static", "firmas_temp")
os.makedirs(FIRMAS_PATH, exist_ok=True)


class ConsentimientoController:
    def __init__(self, service):
        self.service = service

    def form(self):

        return render_template(
            "forms/colaborador/registro_consentimiento.html",
            errores={},
            form_data={},
        )

    def guardar(self):
        """Procesa y guarda el formulario ocupacional"""
        form_data = request.form.to_dict()
        usuario = session.get("usuario", "No disponible")
        print("Datos recibidos del formulario:", form_data)

        try:
            schema = ConsentimientoSchema(**form_data)
            form_validado = schema.dict()
            # print("Formulario validado con Pydantic.")

            payload = self._preparar_payload(form_validado, usuario)
            print("Payload preparado:", payload)

            response = self.service.enviar_formulario(payload)
            print("Respuesta de la API:", response)
            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/colaborador/registro_consentimiento.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_consentimiento.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_consentimiento.html",
                errores={},
                form_data=form_data,
            )

    def _preparar_payload(self, form_data, usuario):
        """Prepara el payload para enviar a la API"""
        return {
            "usuario_registro": session.get("nombreColaborador", "No disponible"),
            "nombre": session.get("nombreColaborador", "No disponible"),
            "cedula": session.get("cedula", "No disponible"),
            "fecha": form_data.get("fecha"),
            "firma": form_data.get("firma", "") or session.get("firma_colaborador", ""),
            "status": "Pendiente",
        }

    def actualizar(self):
        """Procesa y guarda el formulario ocupacional"""
        try:
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")

            # Obtener la firma del formulario
            firma_formulario = form_data.get("firma", "").strip()
            if firma_formulario:
                firma_final = firma_formulario
            else:
                ruta_firma_guardada = session.get("firma_colaborador_path", "")
                cedula_sesion = session.get("firma_colaborador_cedula", "")
                cedula_form = form_data.get("cedula", "")

                # Verificar que la firma guardada pertenece al mismo usuario
                if (
                    ruta_firma_guardada
                    and cedula_form == cedula_sesion
                    and os.path.exists(ruta_firma_guardada)
                ):
                    with open(ruta_firma_guardada, "rb") as f:
                        firma_bytes = f.read()
                        firma_final = (
                            "data:image/png;base64,"
                            + base64.b64encode(firma_bytes).decode()
                        )
                else:
                    firma_final = ""

            payload = {
                **form_data,
                "usuario_actualizacion": usuario,
                "status": "Completada",
                "firma": firma_final,
            }

            form_data_converted = form_data.copy()

            response = service.actualizar_formulario(payload)
            print("Respuesta de la API:", response)
            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")

                ruta_firma_guardada = session.get("firma_colaborador_path", "")
                if ruta_firma_guardada and os.path.exists(ruta_firma_guardada):
                    try:
                        os.remove(ruta_firma_guardada)
                        session.pop("firma_colaborador_path", None)
                        session.pop("firma_colaborador_cedula", None)
                        print("Firma temporal eliminada.")
                    except Exception as e:
                        print("Error al eliminar firma temporal:", str(e))

                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/medico/form_consentimiento_doc.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_consentimiento_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_consentimiento_doc.html",
                errores={},
                form_data=form_data,
            )

    def cargar(self):
        form_data = {}
        errores = {}

        try:
            cedula = request.form.get("cedula")
            response = service.obtener_por_ced(cedula)
            # print("Respuesta de la API:", response)
            form_data = response.get("data", {})
            # print("DATA:", form_data)
            firma_base64 = form_data.get("Firma", "")

            if firma_base64:
                # Guardar la firma en un archivo temporal
                timestamp = int(datetime.now().timestamp())
                nombre_archivo = f"firma_{cedula}_{timestamp}.png"
                ruta_archivo = os.path.join(FIRMAS_PATH, nombre_archivo)

                with open(ruta_archivo, "wb") as f:
                    f.write(base64.b64decode(firma_base64.split(",")[-1]))
                session["firma_colaborador_path"] = ruta_archivo
                session["firma_colaborador_cedula"] = cedula

                print("Firma guardada en:", ruta_archivo)
            else:
                session["firma_colaborador_path"] = ""

            return render_template(
                "forms/medico/form_consentimiento_doc.html",
                errores={},
                form_data=form_data,
            )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_consentimiento_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_consentimiento_doc.html",
                errores={},
                form_data=form_data,
            )

    def listar(self, rango_fechas={}):
        print("Entra al listar")
        return service.obtener_todas()

    def pdf(self):
        if request.method == "POST":
            form_data = request.form.to_dict()
            cedula = form_data.get("cedula")
            session["cedula"] = cedula

            payload = {"cedula": cedula}
            print("CEDULA: ", cedula)
            try:
                # Realiza una solicitud POST a la API con la cédula
                response = requests.post(
                    "https://192.168.137.16:47096/FormDepMedico/Cargar/fichaConsInformado",
                    json=payload,
                    headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                    verify=False,
                )

                if response.status_code == 201:
                    response_data = response.json()
                    print("Respuesta de la API:\n", response_data)

                    pdf_path_input = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "static",
                        "files",
                        "CONSENTIMIENTO_INFORMADO.pdf",
                    )
                    doc = fitz.open(pdf_path_input)  # Abre el documento PDF existente

                    # Procesa cada página del PDF
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        widgets = page.widgets()  # Obtener los campos de formulario

                        if widgets:
                            print(f"Páginas con campos de formulario: {page_num + 1}")
                            for widget in widgets:
                                field_name = widget.field_name
                                field_value = (
                                    widget.field_value
                                )  # Usar field_value para obtener el valor del campo

                                print(
                                    f"Campo: {field_name}, Valor actual: {field_value}"
                                )

                                # Actualiza el campo si está presente en response_data
                                if field_name in response_data:
                                    if (
                                        widget.field_type
                                        == fitz.PDF_WIDGET_TYPE_CHECKBOX
                                    ):
                                        # Marca el checkbox si el valor es True en response_data
                                        widget.field_value = (
                                            True if response_data[field_name] else False
                                        )

                                        widget.update()
                                        print(
                                            f"Checkbox '{field_name}' actualizado con valor: {widget.field_value}"
                                        )

                                    else:
                                        # Para otros campos (como texto), actualiza el valor
                                        widget.field_value = response_data[field_name]
                                        widget.update()
                                        print(
                                            f"Campo '{field_name}' actualizado con valor: {response_data[field_name]}"
                                        )

                        # Establece las posiciones para cada campo a actualizar
                        positions_page1 = {
                            "Nombre": (80, 111),
                            "Cedula": (485, 111),
                            "Fecha": (104, 275),
                        }

                        if page_num == 0:  # Primera página
                            for field_name, position in positions_page1.items():
                                if field_name in response_data:
                                    field_value = response_data[field_name]
                                    if (
                                        field_value
                                    ):  # Asegúrate de que el valor no sea nulo o vacío
                                        print(
                                            f"Campo '{field_name}' actualizado con valor: {field_value}"
                                        )
                                        # Ajuste en el tamaño de fuente a 10 para mejor visibilidad
                                        page.insert_text(
                                            position,
                                            str(field_value),
                                            fontsize=10,
                                            color=(0, 0, 0),
                                        )
                                    else:
                                        print(
                                            f"El campo '{field_name}' está vacío en response_data"
                                        )

                            # Imprimir la imagen de la firma en el PDF
                            firma_colaborador = response_data.get("Firma", "")

                            # Proceso de la firma del colaborador
                            if firma_colaborador:
                                if firma_colaborador.startswith(
                                    "data:image/png;base64,"
                                ):
                                    firma_colaborador = firma_colaborador.split(",")[1]

                                if len(firma_colaborador) % 4:
                                    firma_colaborador += "=" * (
                                        4 - len(firma_colaborador) % 4
                                    )

                                try:
                                    print(
                                        "Procesando firma colaborador...",
                                        firma_colaborador,
                                    )
                                    data_sign = resize_image_base64(
                                        firma_colaborador, 600, 600
                                    )
                                    REDUCED_SIGN = base64.b64decode(data_sign)

                                    signature_position = fitz.Rect(
                                        370 - 200, 670 - 375, 475 - 200, 705 - 375
                                    )
                                    page.insert_image(
                                        signature_position, stream=REDUCED_SIGN
                                    )
                                    print("Firma colaborador añadida.")
                                except (base64.binascii.Error, ValueError) as e:
                                    flash(
                                        f"Error al decodificar la firma: {e}", "error"
                                    )
                                    print(f"Error al decodificar la firma: {e}")

                    # Aplanar todas las páginas
                    new_doc = fitz.open()  # Crear un nuevo documento PDF

                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(
                            matrix=fitz.Matrix(3, 3)
                        )  # Usa una matriz para mayor calidad

                        # Crea una nueva página en el nuevo documento con el mismo tamaño
                        new_page = new_doc.new_page(width=pix.width, height=pix.height)

                        # Inserta la imagen de la página original en la nueva página
                        new_page.insert_image(
                            fitz.Rect(0, 0, pix.width, pix.height), stream=pix.tobytes()
                        )

                    doc.close()  # Cierra el documento original
                    print("Se cierra el doc. Guardando...")
                    # Guarda el nuevo documento PDF aplanado en un archivo temporal
                    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
                    pdf_path_output = temp_file.name
                    temp_file.close()  # Cerrar el handle antes de usar el archivo

                    # Ahora guardar el documento
                    new_doc.save(pdf_path_output)
                    new_doc.close()

                    # Envía el archivo PDF temporal como una descarga
                    print("PDF Completado")

                    return send_file(
                        pdf_path_output,
                        as_attachment=True,
                        download_name="CONSENTIMIENTO_INFORMADO_" + cedula + ".pdf",
                        mimetype="application/pdf",
                    )

                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    return render_template(
                        "dashboard/dashboard_consentimiento.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_consentimiento.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: PDF,  {e}")
                return render_template(
                    "dashboard/dashboard_consentimiento.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_consentimiento.html")

    def excel(self):
        if request.method == "POST":
            print("Entra al post")
            form_data = request.form.to_dict()
            cedula = form_data.get("cedula")
            session["cedula"] = cedula
            print("datos recibidos del formulario", form_data)

            payload = {"cedula": cedula}

            try:
                # Realiza una solicitud POST a la API con la cédula
                response = requests.post(
                    "https://192.168.137.16:47096/FormDepMedico/Cargar/fichaConsInformado",
                    json=payload,
                    headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                    verify=False,
                )

                if response.status_code == 201:
                    response_data = response.json()
                    print(response_data)
                    # Diccionario de coordenadas
                    coordinates = {
                        "D8": response_data.get("Nombre", "N/A"),
                        "J8": response_data.get("Cedula", "N/A"),
                        "D20": response_data.get("Fecha", "N/A"),
                    }
                    # Cargar el archivo Excel existente
                    file_path = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "static",
                        "files",
                        "CONSENTIMIENTO_INFORMADO.xlsx",
                    )

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb["Hoja1"]

                    # Escribir datos en las celdas según el diccionario de coordenadas
                    for cell, value in coordinates.items():
                        ws[cell] = value

                    # Procesar y redimensionar firma del colaborador
                    firma_colaborador = response_data.get("Firma", "")
                    if firma_colaborador:
                        if firma_colaborador.startswith("data:image/png;base64,"):
                            firma_colaborador = firma_colaborador.split(",")[1]
                        if len(firma_colaborador) % 4:
                            firma_colaborador += "=" * (4 - len(firma_colaborador) % 4)

                        try:
                            print("Procesando firma del colaborador...")
                            data_sign = resize_image_base64(
                                firma_colaborador, 250, 150
                            )  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            tempxlsx1 = os.path.join(
                                os.path.dirname(__file__),
                                "..",
                                "..",
                                "static",
                                "files",
                                "CONSENTIMIENTOTEMP.png",
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, "wb") as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(
                                img_colaborador, "F24"
                            )  # Ajusta la posición según sea necesario
                            print("Firma del colaborador añadida.")

                        except (base64.binascii.Error, ValueError) as e:
                            print(f"Error al procesar la firma del colaborador: {e}")

                            # Procesar y redimensionar firma del colaborador
                    firma_doc = response_data.get("Firma_doc", "")
                    if firma_doc:
                        if firma_doc.startswith("data:image/png;base64,"):
                            firma_doc = firma_doc.split(",")[1]
                        if len(firma_doc) % 4:
                            firma_doc += "=" * (4 - len(firma_doc) % 4)

                        try:
                            print("Procesando firma del doctor...")
                            data_sign = resize_image_base64(
                                firma_doc, 250, 150
                            )  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            tempxlsx1 = os.path.join(
                                os.path.dirname(__file__),
                                "..",
                                "files",
                                "CONSENTIMIENTO2_TEMP.png",
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, "wb") as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(
                                "files/CONSENTIMIENTO2_TEMP.png"
                            )
                            ws.add_image(
                                img_colaborador, "C24"
                            )  # Ajusta la posición según sea necesario
                            print("Firma del doctor añadida.")

                        except (base64.binascii.Error, ValueError) as e:
                            print(f"Error al procesar la firma del doctor: {e}")

                    # Guardar el archivo Excel modificado en un buffer temporal
                    output = BytesIO()
                    wb.save(output)
                    output.seek(0)

                    # Enviar el archivo Excel como respuesta para descarga
                    return send_file(
                        output,
                        as_attachment=True,
                        download_name=f"CONSENTIMIENTO_INFORMADO_{cedula}.xlsx",
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    print("Error en la respuesta de la API: " + response.text)
                    return render_template(
                        "dashboard/dashboard_consentimiento.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_consentimiento.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: EXCEL,  {e}")
                return render_template(
                    "dashboard/dashboard_consentimiento.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_consentimiento.html")

    def dashboard(self):
        return render_template("dashboard/dashboard_consentimiento.html")
