from flask import flash, redirect, render_template, request, session, url_for, send_file
from app.certificado.certificado_service import CertificadoService
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
from app.certificado.certificado_schema import CertificadoSchema

service = CertificadoService()


class CertificadoController:
    def form(self):
        return render_template("forms/colaborador/registro_certificado.html")

    def guardar(self):
        """Procesa y guarda el formulario ocupacional"""
        try:
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")

            # Preparar payload para la API
            payload = self._preparar_payload(form_data, usuario)

            # Enviar a la API
            response = service.enviar_formulario(payload)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("certificado.formulario_success", campaign="certificado")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/colaborador/registro_certificado.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_certificado.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_certificado.html",
                errores={},
                form_data=form_data,
            )

    def _preparar_payload(self, form_data, usuario):
        """Prepara el payload para enviar a la API"""
        return {
            "usuario_registro": "",
            "nombre": session.get("nombreColaborador", "No disponible"),
            "cedula": session.get("cedula", "No disponible"),
            "nhc": form_data.get("nhc"),
            "edad": form_data.get("edad"),
            "sexo": form_data.get("sexo"),
            "cargo": form_data.get("cargo"),
            "tiempo_cargo": form_data.get("tiempo_cargo"),
            "fecha_emision": form_data.get("fecha_emision"),
            "ingreso": form_data.get("ingreso"),
            "periodico": form_data.get("periodico"),
            "reintegro": form_data.get("reintegro"),
            "apto": form_data.get("apto"),
            "apto_observacion": form_data.get("apto_observacion"),
            "apto_limitaciones": form_data.get("apto_limitaciones"),
            "no_apto": form_data.get("no_apto"),
            "apto_detalles": form_data.get("apto_detalles"),
            "recomendaciones": form_data.get("recomendaciones"),
            "firma_colaborador": form_data.get("firma_colaborador"),
            "firma_doc": form_data.get("firma_doc", ""),
            "status": "Pendiente",
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
            }
            print(payload)

            data_validated = CertificadoSchema(**payload).dict()

            response = service.actualizar_formulario(data_validated)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("certificado.formulario_success", campaign="certificado")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/colaborador/registro_certificado.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_certificado.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_certificado.html",
                errores={},
                form_data=form_data,
            )

    def cargar(self):
        """Cargar el formulario ocupacional"""
        try:
            form_data = {}
            errores = {}
            cedula = request.args.get("cedula")
            response = service.obtener_por_ced(cedula)
            form_data = response.json()

            nombre = form_data.get("Nombre")
            cedula = form_data.get("Cedula")
            nhc = form_data.get("NHC")
            edad = form_data.get("Edad")
            sexo = form_data.get("Sexo")
            cargo = form_data.get("Cargo")
            tiempo_cargo = form_data.get("Tiempo_cargo")
            ingreso = form_data.get("Ingreso")
            periodico = form_data.get("Periodico")
            reintegro = form_data.get("Reintegro")
            apto = form_data.get("Apto")
            apto_observacion = form_data.get("Apto_observacion")
            apto_limitaciones = form_data.get("Apto_limitaciones")
            no_apto = form_data.get("No_apto")
            apto_detalles = form_data.get("Apto_detalles")
            recomendaciones = form_data.get("Recomendaciones")
            firma_colaborador = form_data.get("Firma_colaborador")
            firma_doc = form_data.get("Firma_doc", "")
            fecha_emision_raw = form_data.get("Fecha_emision")

            try:
                fecha_emision = datetime.strptime(
                    fecha_emision_raw, "%d/%m/%Y"
                ).strftime("%Y-%m-%d")
            except ValueError:
                fecha_emision = ""

            data = {
                "nombre": nombre,
                "cedula": cedula,
                "nhc": nhc,
                "edad": edad,
                "sexo": sexo,
                "cargo": cargo,
                "tiempo_cargo": tiempo_cargo,
                "ingreso": ingreso,
                "periodico": periodico,
                "reintegro": reintegro,
                "fecha_emision": fecha_emision,
                "apto": apto,
                "apto_observacion": apto_observacion,
                "apto_limitaciones": apto_limitaciones,
                "no_apto": no_apto,
                "apto_detalles": apto_detalles,
                "recomendaciones": recomendaciones,
                "firma_colaborador": firma_colaborador,
                "firma_doc": firma_doc,
                "status": "Pendiente",
            }

            return render_template(
                "forms/medico/form_certificado_doc.html", errores={}, form_data=data
            )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_certificado.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_certificado.html",
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
                response = requests.post(
                    f"{BASE_URL}/FormDepMedico/Cargar/fichaCertOcup",
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
                        "CERTIFICADO_OCUPACIONAL.pdf",
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

                        # Obtener la fecha de emisión del response_data
                        fecha_emision_raw = response_data.get("Fecha_emision")
                        fecha_emision = datetime.strptime(fecha_emision_raw, "%Y-%m-%d")
                        dia = fecha_emision.day
                        mes = fecha_emision.month
                        anio = fecha_emision.year

                        # Definir las posiciones donde quieres que se impriman el día, mes y año en la página
                        # Estas posiciones son solo ejemplos, cámbialas según la ubicación que necesites
                        posicion_dia = (260, 298)  # Coordenada para el día
                        posicion_mes = (325, 298)  # Coordenada para el mes
                        posicion_anio = (375, 298)  # Coordenada para el año
                        # Imprimir el día, mes y año en la página
                        page.insert_text(
                            posicion_dia, str(dia), fontsize=10, color=(0, 0, 0)
                        )
                        page.insert_text(
                            posicion_mes, str(mes), fontsize=10, color=(0, 0, 0)
                        )
                        page.insert_text(
                            posicion_anio, str(anio), fontsize=10, color=(0, 0, 0)
                        )

                        # Establece las posiciones para cada campo a actualizar
                        positions_page1 = {
                            "Nombre": (247, 230),
                            "Cedula": (420, 165),
                            "NHC": (420, 185),
                            "Edad": (137, 250),
                            "Sexo": (189, 255),
                            "Cargo": (294, 255),
                            "Tiempo_cargo": (480, 255),
                            "Ingreso": (288, 328),
                            "Periodico": (414, 328),
                            "Reintegro": (513, 328),
                            "Apto": (140, 382),
                            "Apto_observacion": (272, 382),
                            "Apto_limitaciones": (412, 382),
                            "No_apto": (495, 382),
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

                                        # Define el área donde se imprimirá el texto de "Apto_detalles" y "Recomendaciones"
                            detalles_apto = response_data.get(
                                "Apto_detalles", "Sin detalles disponibles."
                            )
                            recomendaciones = response_data.get(
                                "Recomendaciones", "Sin recomendaciones."
                            )
                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            rect_detalles_apto = fitz.Rect(110, 415, 533, 457)
                            rect_recomendaciones = fitz.Rect(110, 485, 533, 530)

                            # Dibujar un borde alrededor del área de "Apto_detalles"
                            # page.draw_rect(rect_detalles_apto, color=(0, 0, 0), width=1)

                            # Insertar el texto ajustado en el área definida para "Apto_detalles"
                            # 'clip' asegurará que solo el texto que cabe se muestre
                            page.insert_textbox(
                                rect_detalles_apto,
                                detalles_apto,
                                fontsize=9,
                                color=(0, 0, 0),
                                align=fitz.TEXT_ALIGN_JUSTIFY,
                            )

                            # Dibujar un borde alrededor del área de "Recomendaciones"
                            # page.draw_rect(rect_recomendaciones, color=(0, 0, 0), width=1)

                            # Insertar el texto ajustado en el área definida para "Recomendaciones"
                            # El parámetro 'clip' corta el texto al área definida por el rectángulo
                            page.insert_textbox(
                                rect_recomendaciones,
                                recomendaciones,
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
                                        370 + 10, 670 - 75, 475 + 10, 705 - 75
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

                                    # Imprimir la imagen de la firma en el PDF
                            firma_doc = base_firma_doc

                            # Proceso de la firma del colaborador
                            if firma_doc:
                                if firma_doc.startswith("data:image/png;base64,"):
                                    firma_doc = firma_doc.split(",")[1]

                                if len(firma_doc) % 4:
                                    firma_doc += "=" * (4 - len(firma_doc) % 4)

                                try:
                                    print("Procesando firma colaborador...", firma_doc)
                                    data_sign = resize_image_base64(firma_doc, 600, 600)
                                    REDUCED_SIGN = base64.b64decode(data_sign)

                                    signature_position = fitz.Rect(
                                        370 - 200, 670 - 75, 475 - 200, 705 - 75
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
                        download_name="CERTIFICADO_OCUPACIONAL_" + cedula + ".pdf",
                        mimetype="application/pdf",
                    )

                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    return render_template(
                        "dashboard/dashboard_certificado.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_certificado.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: PDF,  {e}")
                return render_template(
                    "dashboard/dashboard_certificado.html",
                    errores={},
                    form_data=form_data,
                )
        else:
            return render_template("dashboard/dashboard_certificado.html")

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
                    f"{BASE_URL}/FormDepMedico/Cargar/fichaCertOcup",
                    json=payload,
                    headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                    verify=False,
                )

                if response.status_code == 201:
                    response_data = response.json()

                    print(response_data)
                    # Diccionario de coordenadas
                    edad = response_data.get("Edad")
                    sexo = response_data.get("Sexo")
                    periodico = response_data.get("Periodico")
                    reintegro = response_data.get("Reintegro")
                    apto = response_data.get("Apto")
                    no_apto = response_data.get("No_apto")
                    apto_limitaciones = response_data.get("Apto_limitaciones")
                    fecha_emision_raw = response_data.get("Fecha_emision")
                    fecha_emision = datetime.strptime(fecha_emision_raw, "%Y-%m-%d")
                    dia = fecha_emision.day
                    mes = fecha_emision.month
                    anio = fecha_emision.year

                    print(f"MESSS: {mes}")

                    coordinates = {
                        "D8": response_data.get("Nombre", "N/A"),
                        "G2": response_data.get("Cedula", "N/A"),
                        "G4": response_data.get("NHC", "N/A"),
                        "B10": f"Edad:  {edad}",
                        "C10": f"Sexo:  {sexo}",
                        "E10": response_data.get("Cargo"),
                        "H10": response_data.get("Tiempo_cargo"),
                        "D14": str(dia),
                        "E14": str(mes),
                        "F14": str(anio),
                        "E17": response_data.get("Ingreso"),
                        "F17": f"PERIÓDICO  {periodico}",
                        "H17": f"REINTEGRO  {reintegro}",
                        "B23": f"APTO:      {apto}",
                        "D23": response_data.get("Apto_observación"),
                        "E23": f"APTO con limitaciones:  {apto_limitaciones}",
                        "H23": f"NO APTO:  {no_apto}",
                        "B27": response_data.get("Apto_detalles"),
                        "B33": response_data.get("Recomendaciones"),
                        "F43": response_data.get("Fecha_actualizacion"),
                        "C43": session["nombreColaborador"],
                    }

                    # Cargar el archivo Excel existente
                    file_path = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "static",
                        "files",
                        "CERTIFICADO_OCUPACIONAL.xlsx",
                    )

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb["CERTIFICADO OCUPACIONAL"]

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

                            tempxlsx1 = os.path.abspath(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    "..",
                                    "..",
                                    "static",
                                    "files",
                                    "CERTIFICADO_TEMP.png",
                                )
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, "wb") as f:
                                f.write(REDUCED_SIGN)
                            print("intentan insertar imagen")
                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(
                                img_colaborador, "F44"
                            )  # Ajusta la posición según sea necesario
                            print("Firma del colaborador añadida.")

                        except (base64.binascii.Error, ValueError) as e:
                            print(f"Error al procesar la firma del colaborador: {e}")

                    firma_doctor = base_firma_doc
                    if firma_doctor:
                        if firma_doctor.startswith("data:image/png;base64,"):
                            firma_doctor = firma_doctor.split(",")[1]
                        if len(firma_doctor) % 4:
                            firma_doctor += "=" * (4 - len(firma_doctor) % 4)

                        try:
                            print("Procesando firma del doctor...")
                            data_sign = resize_image_base64(
                                firma_doctor, 250, 150
                            )  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            # Guardar la firma redimensionada temporalmente
                            tempxlsx2 = os.path.join(
                                os.path.dirname(__file__),
                                "..",
                                "..",
                                "static",
                                "files",
                                "FICHA_OCUPACIONALTEMP2.png",
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx2, "wb") as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_doctor = ExcelImage(tempxlsx2)
                            ws.add_image(
                                img_doctor, "C44"
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
                        download_name=f"CERTIFICADO_OCUPACIONAL_{cedula}.xlsx",
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    print("Error en la respuesta de la API: " + response.text)
                    return render_template(
                        "dashboard/dashboard_certificado.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_certificado.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: EXCEL,  {e}")
                return render_template(
                    "dashboard/dashboard_certificado.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_certificado.html")

    def dashboard(self):
        return render_template("dashboard/dashboard_certificado.html")
