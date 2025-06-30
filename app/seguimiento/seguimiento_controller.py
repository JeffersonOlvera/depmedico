from flask import flash, redirect, render_template, request, session, url_for, send_file
from app.seguimiento.seguimiento_schema import SeguimientoSchema
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
from pydantic import ValidationError
from app.seguimiento.seguimiento_service import SeguimientoService
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

service = SeguimientoService()


class SeguimientoController:
    def form(self):
        return render_template("forms/colaborador/registro_seguimiento_drogas.html")

    def guardar(self):
        """Procesa y guarda el formulario seguimiento"""
        try:
            print("ENVIANDO A GUARDAR EL FORMULARIO CERTIFICADO")
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")

            print("Datos recibidos del formulario:", form_data)

            # Validación con Pydantic
            form_data_converted = form_data.copy()
            # upgrade_form = Form(**form_data_converted)
            print("Formulario validado con Pydantic.")

            # Preparar payload para la API
            payload = self._preparar_payload(form_data)
            print("Payload preparado:", payload)

            # Enviar a la API
            response = service.enviar_formulario(payload)
            print("Respuesta de la API:", response)
            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("seguimiento.formulario_success", campaign="seguimiento")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/colaborador/registro_seguimiento_drogas.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_seguimiento_drogas.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_seguimiento_drogas.html",
                errores={},
                form_data=form_data,
            )

    def _preparar_payload(self, form_data):
        """Prepara el payload para enviar a la API"""
        return {
            "Usuario_registro": session.get("nombreColaborador", ""),
            "Tipo_ficha": "SeguimientoDroga",
            "Cedula": session.get("cedula", ""),
            "Nombre": session.get("nombreColaborador", ""),
            "Cargo": form_data.get("Cargo", ""),
            "Tiempo_cargo": form_data.get("Tiempo_cargo", ""),
            "Edad": form_data.get("Edad", ""),
            "Enfer_catastrofica": form_data.get("Enfer_catastrofica", ""),
            "Enfer_cron_transmi": form_data.get("Enfer_cron_transmi", ""),
            "Enfer_cron_notransmi": form_data.get("Enfer_cron_notransmi", ""),
            "Enfer_nodiagnosticada": form_data.get("Enfer_nodiagnosticada", ""),
            "Droga": form_data.get("Droga", ""),
            "Frecuencia_consumo": form_data.get("Frecuencia_consumo", ""),
            "Fact_psico_sociales": form_data.get("Fact_psico_sociales", ""),
            "Fact_psico_sociales_detalle": form_data.get(
                "Fact_psico_sociales_detalle", ""
            ),
            "Socializacion_personal": form_data.get("Socializacion_personal", ""),
            "Firma_colaborador": form_data.get("firma_colaborador", ""),
            "Status": "Pendiente",
        }

    def actualizar(self):
        """Procesa y guarda el formulario ocupacional"""
        try:
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")

            payload = {
                **form_data,
                "usuario_actualizacion": usuario,
                "status": "Completada",
                "tipo_ficha": "SeguimientoDroga",
            }

            data_validated = SeguimientoSchema(**payload).dict()

            response = service.actualizar_formulario(data_validated)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/medico/form_segdrogas_doc.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_segdrogas_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_segdrogas_doc.html",
                errores={},
                form_data=form_data,
            )

    def cargar(self):
        form_data = {}
        errores = {}

        try:
            cedula = request.form.get("cedula")
            response = service.obtener_por_ced(cedula)
            form_data = response.json()
            print(form_data)

            return render_template(
                "forms/medico/form_segdrogas_doc.html", errores={}, form_data=form_data
            )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_segdrogas_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_segdrogas_doc.html",
                errores={},
                form_data=form_data,
            )

    def listar(self):
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
                    "https://192.168.137.16:47096/FormDepMedico/Cargar/fichaSegDrogas",
                    json=payload,
                    headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                    verify=False,
                )

                if response.status_code == 201:
                    response_data = response.json()
                    print("Respuesta de la API:\n", response_data)

                    print(response_data.get("Fecha_actualizacion"))
                    pdf_path_input = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "static",
                        "files",
                        "FICHA_SEGUIMIENTO.pdf",
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
                            "Cedula": (135, 138),
                            "Nombre": (135, 155),
                            "Cargo": (135, 173),
                            "Fecha_actualizacion": (425, 138),
                            "Edad": (425, 155),
                            "Tiempo_cargo": (425, 173),
                            "Enfer_catastrofica": (181, 212),
                            "Enfer_cron_transmi": (181, 235),
                            "Enfer_cron_notransmi": (181, 258),
                            "Enfer_nodiagnosticada": (181, 281),
                        }

                        Droga = response_data.get("Droga", "N/A")
                        print(Droga)
                        # Definir la posición dependiendo del valor de 'Droga'
                        if Droga == "No consume":
                            positions_page1["Droga"] = (181, 343)
                        elif Droga == "Alcohol":
                            positions_page1["Droga"] = (181, 365)
                        elif Droga == "Anfetaminas":
                            positions_page1["Droga"] = (181, 387)
                        elif Droga == "Cigarrillo":
                            positions_page1["Droga"] = (181, 408)
                        elif Droga == "Marihuana":
                            positions_page1["Droga"] = (181, 430)
                        elif Droga == "Base de cocaina":
                            positions_page1["Droga"] = (181, 452)
                        elif Droga == "Heroina":
                            positions_page1["Droga"] = (181, 474)
                        elif Droga == "Tabaco":
                            positions_page1["Droga"] = (181, 492)
                        elif Droga == "Morfina":
                            positions_page1["Droga"] = (181, 514)
                        elif Droga == "Hongos":
                            positions_page1["Droga"] = (181, 536)
                        elif Droga == "Drogas de sintesis":
                            positions_page1["Droga"] = (181, 558)
                        elif Droga == "Inhalantes":
                            positions_page1["Droga"] = (181, 580)
                        elif Droga == "Pegamentos":
                            positions_page1["Droga"] = (181, 601)
                        else:
                            print("No es un valor valido")

                        Socializacion = response_data.get(
                            "Socializacion_personal", "N/A"
                        )
                        print(Socializacion)
                        # Definir la posición dependiendo del valor de 'Droga'
                        if Socializacion == "Si":
                            positions_page1["Socializacion"] = (447, 618)
                        elif Socializacion == "No":
                            positions_page1["Socializacion"] = (494, 618)
                        else:
                            print("No es un valor valido")

                        Factores = response_data.get("Fact_psico_sociales", "N/A")
                        print(Factores)
                        # Definir la posición dependiendo del valor de 'Droga'
                        if Factores == "Si":
                            positions_page1["Factores"] = (422, 409)
                        elif Factores == "No":
                            positions_page1["Factores"] = (422, 433)
                        else:
                            print("No es un valor valido")

                        Frecuencia = response_data.get("Frecuencia_consumo", "N/A")
                        print(Frecuencia)
                        # Definir la posición dependiendo del valor de 'Droga'
                        if Frecuencia == "No consume":
                            positions_page1["Frecuencia"] = (422, 344)
                        elif Frecuencia == "5-7 dias":
                            positions_page1["Frecuencia"] = (422, 212)
                        elif Frecuencia == "2-4 veces":
                            positions_page1["Frecuencia"] = (422, 234)
                        elif Frecuencia == "2-7 veces":
                            positions_page1["Frecuencia"] = (422, 258)
                        elif Frecuencia == "1 vez po semana":
                            positions_page1["Frecuencia"] = (422, 278)
                        elif Frecuencia == "2-12 veces Año":
                            positions_page1["Frecuencia"] = (422, 299)
                        elif Frecuencia == "1 vez al Año":
                            positions_page1["Frecuencia"] = (422, 322)
                        else:
                            print("No es un valor valido")

                        # Imprimir la "X" en la posición correspondiente a 'Droga'
                        if page_num == 0:  # Primera página
                            for field_name, position in positions_page1.items():
                                if field_name == "Droga":
                                    # Imprimir una "X" en la posición correspondiente
                                    page.insert_text(
                                        position, "X", fontsize=10, color=(0, 0, 0)
                                    )

                                elif field_name == "Factores":
                                    # Imprimir una "X" en la posición correspondiente
                                    page.insert_text(
                                        position, "X", fontsize=10, color=(0, 0, 0)
                                    )

                                elif field_name == "Socializacion":
                                    page.insert_text(
                                        position, "X", fontsize=10, color=(0, 0, 0)
                                    )

                                elif field_name == "Frecuencia":
                                    page.insert_text(
                                        position, "X", fontsize=10, color=(0, 0, 0)
                                    )

                                elif field_name in response_data:
                                    field_value = response_data[field_name]
                                    if (
                                        field_value
                                    ):  # Asegúrate de que el valor no sea nulo o vacío
                                        print(
                                            f"Campo '{field_name}' actualizado con valor: {field_value}"
                                        )
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

                                        # Define el área donde se imprimirá el texto de "Apto_detalles" y "Recomendaciones"
                            detalles_factores = response_data.get(
                                "Fact_psico_sociales_detalle", ""
                            )

                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            rect_detalles_apto = fitz.Rect(
                                110 + 171, 415 + 48, 533 + 171, 457 + 48
                            )

                            page.insert_textbox(
                                rect_detalles_apto,
                                detalles_factores,
                                fontsize=9,
                                color=(0, 0, 0),
                                align=fitz.TEXT_ALIGN_JUSTIFY,
                            )

                            # Imprimir la imagen de la firma en el PDF
                            firma_colaborador = response_data.get(
                                "Firma_colaborador", ""
                            )

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
                                        370 - 125, 670 - 28, 475 - 125, 705 - 28
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
                        download_name="FICHA_SEGUIMIENTO_" + cedula + ".pdf",
                        mimetype="application/pdf",
                    )

                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    return render_template(
                        "dashboard/dashboard_seguimiento.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_seguimiento.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: PDF,  {e}")
                return render_template(
                    "dashboard/dashboard_seguimiento.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_seguimiento.html")

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
                    "https://192.168.137.16:47096/FormDepMedico/Cargar/fichaSegDrogas",
                    json=payload,
                    headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                    verify=False,
                )

                if response.status_code == 201:

                    response_data = response.json()

                    coordinates = {
                        "C5": response_data.get("Cedula", "N/A"),
                        "C6": response_data.get("Nombre", "N/A"),
                        "C7": response_data.get("Cargo", "N/A"),
                        "H5": response_data.get("Fecha_actualizacion", "N/A"),
                        "H6": response_data.get("Edad", "N/A"),
                        "H7": response_data.get("Tiempo_cargo", "N/A"),
                        "D11": response_data.get("Enfer_catastrofica", "N/A"),
                        "D13": response_data.get("Enfer_cron_transmi", "N/A"),
                        "D15": response_data.get("Enfer_cron_notransmi", "N/A"),
                        "D17": response_data.get("Enfer_nodiagnosticada", "N/A"),
                        "F35": response_data.get("Fact_psico_sociales_detalle", "N/A"),
                    }

                    droga = response_data.get("Droga", "N/A")
                    # Definir la coordenada dependiendo del valor de 'Droga'
                    if droga == "No Consume":
                        coordinates["D23"] = "X"
                    elif droga == "Alcohol":
                        coordinates["D25"] = "X"
                    elif droga == "Anfetaminas":
                        coordinates["D27"] = "X"
                    elif droga == "Cigarrillo":
                        coordinates["D29"] = "X"
                    elif droga == "Marihuana":
                        coordinates["D31"] = "X"
                    elif droga == "Base de cocaina":
                        coordinates["D33"] = "X"
                    elif droga == "Heroina":
                        coordinates["D35"] = "X"
                    elif droga == "Tabaco":
                        coordinates["D37"] = "X"
                    elif droga == "Morfina":
                        coordinates["D39"] = "X"
                    elif droga == "Hongos":
                        coordinates["D41"] = "X"
                    elif droga == "Drogas de sintesis":
                        coordinates["D43"] = "X"
                    elif droga == "Inhalantes":
                        coordinates["D45"] = "X"
                    elif droga == "Pegamentos":
                        coordinates["D47"] = "X"
                    else:
                        coordinates["D23"] = "X"

                    frecuencia_consumo = response_data.get("Frecuencia_consumo", "N/A")

                    if frecuencia_consumo == "No consume":
                        coordinates["I23"] = "X"
                    elif frecuencia_consumo == "5-7 dias":
                        coordinates["I11"] = "X"
                    elif frecuencia_consumo == "2-4 veces":
                        coordinates["I13"] = "X"
                    elif frecuencia_consumo == "2-7 veces":
                        coordinates["I15"] = "X"
                    elif frecuencia_consumo == "1 vez por semana":
                        coordinates["I17"] = "X"
                    elif frecuencia_consumo == "2-12 veces Año":
                        coordinates["I19"] = "X"
                    elif frecuencia_consumo == "1 vez al Año":
                        coordinates["I21"] = "X"
                    else:
                        coordinates["D23"] = ""

                    socializacion_personal = response_data.get(
                        "Socializacion_personal", "N/A"
                    )

                    if socializacion_personal == "Si":
                        coordinates["H49"] = "X"
                    elif socializacion_personal == "No":
                        coordinates["J49"] = "X"
                    else:
                        coordinates["D23"] = ""

                    factores = response_data.get("Fact_psico_sociales", "N/A")

                    if factores == "No":
                        coordinates["I29"] = "X"
                    elif factores == "Si":
                        coordinates["I31"] = "X"
                    else:
                        coordinates["0"] = ""

                    # Cargar el archivo Excel existente
                    file_path = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "static",
                        "files",
                        "FICHA_SEGUIMIENTO.xlsx",
                    )

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb["Hoja1"]

                    # Escribir datos en las celdas según el diccionario de coordenadas
                    for cell, value in coordinates.items():
                        ws[cell] = value

                    # Procesar y redimensionar firma del colaborador
                    firma_colaborador = response_data.get("Firma_colaborador", "")
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
                                "SEGUIMIENTO_TEMP.png",
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, "wb") as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(
                                img_colaborador, "E50"
                            )  # Ajusta la posición según sea necesario
                            print("Firma del colaborador añadida.")

                        except (base64.binascii.Error, ValueError) as e:
                            print(f"Error al procesar la firma del colaborador: {e}")

                    # Guardar el archivo Excel modificado en un buffer temporal
                    output = BytesIO()
                    wb.save(output)
                    output.seek(0)

                    # Enviar el archivo Excel como respuesta para descarga
                    return send_file(
                        output,
                        as_attachment=True,
                        download_name=f"FICHA_SEGUIMIENTO_{cedula}.xlsx",
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    print("Error en la respuesta de la API: " + response.text)
                    return render_template(
                        "dashboard/dashboard_seguimiento.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_seguimiento.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: EXCEL,  {e}")
                return render_template(
                    "dashboard/dashboard_seguimiento.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_seguimiento.html")

    def dashboard(self):
        return render_template("dashboard/dashboard_seguimiento.html")
