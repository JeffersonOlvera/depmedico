from flask import flash, redirect, render_template, request, session, url_for
from pydantic import ValidationError
from app.preocupacional.preocupacional_service import PreocupacionalService
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
from app.preocupacional.preocupacional_schema import PreocupacionalSchema


service = PreocupacionalService()


class PreocupacionalController:
    def form(self):
        form_data = {}
        errores = {}

        return render_template(
            "forms/colaborador/registro_preocupacional.html",
            errores=errores,
            form_data=form_data,
        )

    def guardar(self):
        """Procesa y guarda el formulario ocupacional"""
        try:
            print("ENVIANDO A GUARDAR EL FORMULARIO")
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")

            print("Datos recibidos del formulario:", form_data)

            # Validación con Pydantic
            form_data_converted = form_data.copy()
            # upgrade_form = Form(**form_data_converted)
            print("Formulario validado con Pydantic.")

            # Preparar payload para la API
            payload = self._preparar_payload(form_data, usuario)
            print("Payload preparado:", payload)

            # Enviar a la API
            response = service.enviar_formulario(payload)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/colaborador/registro_ocupacional.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_ocupacional.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_ocupacional.html",
                errores={},
                form_data=form_data,
            )

    def _preparar_payload(self, form_data, usuario):
        """Prepara el payload para enviar a la API"""
        return {
            "Tipo_Ficha": "Preocupacional",
            "usuario_registro": session.get("nombreColaborador", "No disponible"),
            "Sector": "Privado",
            "status": "Pendiente",
            "Nombre": session.get("nombreColaborador", ""),
            "Edad": form_data.get("Edad", ""),
            "Cedula": session.get("cedula" ""),
            "Grupo_sanguineo": form_data.get("Grupo_sanguineo", None),
            "Discapacidad": form_data.get("Discapacidad", None),
            "Porc_Discapacidad": form_data.get("Porc_Discapacidad", None),
            "Religion": form_data.get("Religion", None),
            "Puesto_Trabajo": form_data.get("Puesto_Trabajo", None),
            "Ori_Lesbiana": form_data.get("Ori_Lesbiana", None),
            "Ori_Gay": form_data.get("Ori_Gay", None),
            "Ori_Bisexual": form_data.get("Ori_Bisexual", None),
            "Ori_Hetero": form_data.get("Ori_Hetero", None),
            "Ori_Omitir": form_data.get("Ori_Omitir", None),
            "Iden_Masc": form_data.get("Iden_Masc", None),
            "Iden_Fem": form_data.get("Iden_Fem", None),
            "Iden_Transg": form_data.get("Iden_Transg", None),
            "Iden_Omitir": form_data.get("Iden_Omitir", None),
            "Antced_Clin_Quir": form_data.get("Antced_Clin_Quir", None),
            "Gin_Menarquia": form_data.get("Gin_Menarquia", None),
            "Gin_Ciclos_R": form_data.get("Gin_Ciclos_R", None),
            "Gin_Ciclos_I": form_data.get("Gin_Ciclos_I", None),
            "Gin_Fum": form_data.get("Gin_Fum", None),
            "Gin_Gestas": form_data.get("Gin_Gestas", None),
            "Gin_Partos": form_data.get("Gin_Partos", None),
            "Gin_Cesarea": form_data.get("Gin_Cesarea", None),
            "Gin_Aborto": form_data.get("Gin_Aborto", None),
            "Gin_Hijos_V": form_data.get("Gin_Hijos_V", None),
            "Gin_Hjos_M": form_data.get("Gin_Hjos_M", None),
            "Gin_Vsa": form_data.get("Gin_Vsa", None),
            "Gin_Mpf": form_data.get("Gin_Mpf", None),
            "Gin_Pap": form_data.get("Gin_Pap", None),
            "Gin_Colpos": form_data.get("Gin_Colpos", None),
            "Gin_Eco_Mama": form_data.get("Gin_Eco_Mama", None),
            "Gin_Mamografia": form_data.get("Gin_Mamografia", None),
            "Ap_Ag_Prost": form_data.get("Ap_Ag_Prost", None),
            "Ap_Eco_Prost": form_data.get("Ap_Eco_Prost", None),
            "Ap_Obsv": form_data.get("Ap_Obsv", None),
            "Act_Fisica": form_data.get("Act_Fisica", None),
            "Act_Fisica_Obsv": form_data.get("Act_Fisica_Obsv", None),
            "Medi_Actual": form_data.get("Medi_Actual", None),
            "Medi_Actual_Obsv": form_data.get("Medi_Actual_Obsv", None),
            "Alcohol": form_data.get("Alcohol", None),
            "Alcohol_Obsv": form_data.get("Alcohol_Obsv", None),
            "Tabaco": form_data.get("Tabaco", None),
            "Tabaco_Obsv": form_data.get("Tabaco_Obsv", None),
            "Otros": form_data.get("Otros", None),
            "Otros_Obsv": form_data.get("Otros_Obsv", None),
            "Empresa_1": form_data.get("Empresa_1", None),
            "Puesto_1": form_data.get("Puesto_1", None),
            "Actividad_1": form_data.get("Actividad_1", None),
            "Tiempo_1": form_data.get("Tiempo_1", None),
            "Riego_1": form_data.get("Riego_1", None),
            "Antc_Observ_1": form_data.get("Antc_Observ_1", None),
            "Empresa_2": form_data.get("Empresa_2", None),
            "Puesto_2": form_data.get("Puesto_2", None),
            "Actividad_2": form_data.get("Actividad_2", None),
            "Tiempo_2": form_data.get("Tiempo_2", None),
            "Riego_2": form_data.get("Riego_2", None),
            "Antc_Observ_2": form_data.get("Antc_Observ_2", None),
            "Empresa_3": form_data.get("Empresa_3", None),
            "Puesto_3": form_data.get("Puesto_3", None),
            "Actividad_3": form_data.get("Actividad_3", None),
            "Tiempo_3": form_data.get("Tiempo_3", None),
            "Riego_3": form_data.get("Riego_3", None),
            "Antc_Observ_3": form_data.get("Antc_Observ_3", None),
            "Empresa_4": form_data.get("Empresa_4", None),
            "Puesto_4": form_data.get("Puesto_4", None),
            "Actividad_4": form_data.get("Actividad_4", None),
            "Tiempo_4": form_data.get("Tiempo_4", None),
            "Riego_4": form_data.get("Riego_4", None),
            "Antc_Observ_4": form_data.get("Antc_Observ_4", None),
            "Accidente_Trabajo": form_data.get("Accidente_Trabajo", None),
            "Accidente_Trabajo_Calf_1": form_data.get("Accidente_Trabajo_Calf_1", None),
            "Accidente_Trabajo_Fecha": form_data.get("Accidente_Trabajo_Fecha", None),
            "Enfermedad_Prof": form_data.get("Enfermedad_Prof", None),
            "Enfermedad_Prof_Calf_1": form_data.get("Enfermedad_Prof_Calf_1", None),
            "Enfermedad_Prof_Fecha": form_data.get("Enfermedad_Prof_Fecha", None),
            "Car_Vasc": form_data.get("Car_Vasc", None),
            "Metabolica": form_data.get("Metabolica", None),
            "Neurologica": form_data.get("Neurologica", None),
            "Onco": form_data.get("Onco", None),
            "Infec": form_data.get("Infec", None),
            "Hereditaria": form_data.get("Hereditaria", None),
            "Antc_Descrip": form_data.get("Antc_Descrip", None),
            "Act_Extralaborales": form_data.get("Act_Extralaborales", None),
            "Activ_Relevante": form_data.get("Activ_Relevante", None),
            "Firma_Colaborador": form_data.get("Firma_Colaborador", None),
            "fecha": form_data.get("fecha", None),
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
                "tipo_ficha": "Preocupacional",
            }

            print("DATOS A ACTUALIZAR:", payload)
            data_validated = PreocupacionalSchema(**payload).dict()

            response = service.actualizar_formulario(data_validated)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/medico/form_preocupacional_doc.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_preocupacional_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_preocupacional_doc.html",
                errores={},
                form_data=form_data,
            )

    def cargar(self):
        print("Entra al controller de cargar")
        form_data = {}
        errores = {}

        try:
            cedula = request.form.get("cedula")
            response = service.obtener_por_ced(cedula)
            form_data = response.json()
            print(form_data)

            session["firma_colaborador"] = form_data.get("firma_colaborador", "")

            experiencias = [
                {
                    "empresa": form_data.get("Empresa_1", ""),
                    "puesto": form_data.get("Puesto_1", ""),
                    "actividad": form_data.get("Actividad_1", ""),
                    "tiempo": form_data.get("Tiempo_1", ""),
                    "riesgo": form_data.get("Riego_1", ""),
                    "observacion": form_data.get("Antc_Observ_1", ""),
                },
                {
                    "empresa": form_data.get("Empresa_2", ""),
                    "puesto": form_data.get("Puesto_2", ""),
                    "actividad": form_data.get("Actividad_2", ""),
                    "tiempo": form_data.get("Tiempo_2", ""),
                    "riesgo": form_data.get("Riego_2", ""),
                    "observacion": form_data.get("Antc_Observ_2", ""),
                },
                {
                    "empresa": form_data.get("Empresa_3", ""),
                    "puesto": form_data.get("Puesto_3", ""),
                    "actividad": form_data.get("Actividad_3", ""),
                    "tiempo": form_data.get("Tiempo_3", ""),
                    "riesgo": form_data.get("Riego_3", ""),
                    "observacion": form_data.get("Antc_Observ_3", ""),
                },
                {
                    "empresa": form_data.get("Empresa_4", ""),
                    "puesto": form_data.get("Puesto_4", ""),
                    "actividad": form_data.get("Actividad_4", ""),
                    "tiempo": form_data.get("Tiempo_4", ""),
                    "riesgo": form_data.get("Riego_4", ""),
                    "observacion": form_data.get("Antc_Observ_4", ""),
                },
            ]

            return render_template(
                "forms/medico/form_preocupacional_doc.html",
                errores={},
                form_data=form_data,
                experiencias=experiencias,
            )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_preocupacional_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_preocupacional_doc.html",
                errores={},
                form_data=form_data,
            )

    def dashboard(self):
        return render_template("dashboard/dashboard_preocupacional.html")

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
                    f"{BASE_URL}/FormDepMedico/Cargar/fichaPreocupacional",
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
                        "FICHA_PREOCUPACIONAL.pdf",
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
                            "Cedula": (448, 27),
                            "Nombre": (125, 66),
                            "Edad": (90, 87),
                            "Discapacidad": (195, 87),
                            "Porc_Discapacidad": (330, 87),
                            "Religion": (450, 87),
                            "Grupo_sanguineo": (460, 51),
                            "Puesto_Trabajo": (125, 105),
                            "Activ_Relevante": (400, 105),
                            "Ori_Lesbiana": (163, 121),
                            "Ori_Gay": (230, 121),
                            "Ori_Bisexual": (298, 121),
                            "Ori_Hetero": (356, 121),
                            "Ori_Omitir": (463, 121),
                            "Iden_Fem": (164, 137),
                            "Iden_Masc": (230, 137),
                            "Iden_Transg": (310, 137),
                            "Iden_Omitir": (464, 136),
                            "Antced_Clin_Quir": (60, 218),
                            "Gin_Menarquia": (99, 257),
                            "Gin_Ciclos_R": (156, 257),
                            "Gin_Ciclos_I": (178, 257),
                            "Gin_Fum": (225, 257),
                            "Gin_Gestas": (298, 257),
                            "Gin_Partos": (360, 257),
                            "Gin_Cesarea": (424, 257),
                            "Gin_Aborto": (475, 257),
                            "Gin_Hijos_V": (84, 271),
                            "Gin_Hjos_M": (110, 271),
                            "Gin_Vsa": (160, 271),
                            "Gin_Mpf": (225, 271),
                            "Gin_Pap": (298, 271),
                            "Gin_Colpos": (360, 271),
                            "Gin_Eco_Mama": (424, 271),
                            "Gin_Mamografia": (490, 271),
                            "Ap_Ag_Prost": (90, 302),
                            "Ap_Eco_Prost": (162, 302),
                            "Ap_Obsv": (227, 302),
                            "Act_Fisica_Obsv": (190, 323),
                            "Medi_Actual_Obsv": (190, 336),
                            "Alcohol_Obsv": (190, 348),
                            "Tabaco_Obsv": (190, 359),
                            "Otros_Obsv": (190, 370),
                            "Empresa_1": (60, 429),
                            "Empresa_2": (60, 441),
                            "Empresa_3": (60, 455),
                            "Empresa_4": (60, 468),
                            "Puesto_1": (125, 429),
                            "Puesto_2": (125, 441),
                            "Puesto_3": (125, 455),
                            "Puesto_4": (125, 468),
                            "Actividad_1": (195, 429),
                            "Actividad_2": (195, 441),
                            "Actividad_3": (195, 455),
                            "Actividad_4": (195, 468),
                            "Tiempo_1": (266, 429),
                            "Tiempo_2": (266, 441),
                            "Tiempo_3": (266, 455),
                            "Tiempo_4": (266, 468),
                            "Riego_1": (332, 429),
                            "Riego_2": (332, 441),
                            "Riego_3": (332, 455),
                            "Riego_4": (332, 468),
                            "Antc_Observ_1": (445, 429),
                            "Antc_Observ_2": (445, 441),
                            "Antc_Observ_3": (445, 455),
                            "Antc_Observ_4": (445, 468),
                            "Accidente_Trabajo_Calf_1": (127, 500),
                            "Accidente_Trabajo_Fecha": (446, 500),
                            "Enfermedad_Prof_Calf_1": (127, 519),
                            "Enfermedad_Prof_Fecha": (446, 519),
                            "Car_Vasc": (97, 554),
                            "Metabolica": (168, 554),
                            "Neurologica": (231, 554),
                            "Onco": (315, 554),
                            "Infec": (371, 554),
                            "Hereditaria": (476, 554),
                            "Antc_Descrip": (62, 587),
                            "Fact_Ruido": (155, 627),
                            "Fact_Iluminacion": (155, 642),
                            "Fact_Ventilacion": (155, 657),
                            "Fact_Caidas": (155, 672),
                            "Fact_Atrope": (155, 686),
                            "Fact_Caida_Desniv": (155, 702),
                            "Fact_Polvo": (291, 627),
                            "Fact_Liquidos": (291, 642),
                            "Fact_Virus": (291, 657),
                            "Fact_Post_Forz": (291, 672),
                            "Fact_Mov_Rep": (291, 686),
                            "Fact_Monotomia": (291, 702),
                            "Fact_Alta_Respo": (472, 627),
                            "Fact_Conflict": (472, 642),
                            "Fact_Sobrecarga": (472, 657),
                            "Fact_Inestabilidad": (472, 672),
                            "Fact_Relac_Interp": (472, 686),
                        }

                        positions_page2 = {
                            "Org_Piel": (106, 96),
                            "Org_Respiratorio": (172, 96),
                            "Org_Digestivo": (233, 96),
                            "Org_Mus_Esq": (302, 96),
                            "Org_Hemolinf": (370, 96),
                            "Org_Sent": (428, 96),
                            "Org_Gen_Uri": (481, 96),
                            "Org_Endocrino": (106, 113),
                            "Org_Nervioso": (172, 113),
                            "Org_Card_Vacular": (249, 113),
                            "Org_Descripcion": (61, 148),
                            "Sig_Pres_Art": (135, 187),
                            "Sig_Temp": (230, 187),
                            "Sig_Fc": (300, 187),
                            "Sig_Sat_Ox": (365, 187),
                            "Sig_Fr": (475, 187),
                            "Sig_Peso": (88, 201),
                            "Sig_Talla": (157, 201),
                            "Riego_8": (230, 201),
                            "Sig_Biotico": (300, 201),
                            "Sig_Atleti": (365, 201),
                            "Sig_Picn": (420, 201),
                            "Sig_Atletico": (476, 201),
                            "Examn_Fis_Garganta": (138, 261),
                            "Examn_Fis_Ojos": (138, 274),
                            "Examn_Fis_Oidos": (138, 287),
                            "Examn_Fis_Nariz": (138, 302),
                            "Examn_Fis_Boca": (138, 315),
                            "Examn_Fis_Dentudura": (138, 329),
                            "Examn_Fis_Corazon": (138, 356),
                            "Examn_Fis_Pulmones": (138, 369),
                            "Examn_Fis_Inspeccion": (138, 396),
                            "Examn_Fis_Palpacion": (138, 410),
                            "Examn_Fis_Percsusion": (138, 423),
                            "Examn_Fis_Umbilical": (291, 260),
                            "Examn_Fis_Ingual_Dere": (291, 274),
                            "Examn_Fis_Clural_Dere": (291, 287),
                            "Examn_Fis_Inguinal_Izquierdo": (291, 301),
                            "Examn_Fis_Clural_Izq": (291, 315),
                            "Examn_Fis_Deformaciones": (291, 343),
                            "Examn_Fis_Movilidad": (291, 358),
                            "Examn_Fis_Masas_Musculares": (291, 373),
                            "Examn_Fis_Tracto_Urinario": (291, 396),
                            "Examn_Fis_Tracto_Genital": (291, 410),
                            "Examn_Fis_Regio_Anoperineal": (291, 424),
                            "Examn_Fis_Sup_Izquierda": (475, 262),
                            "Examn_Fis_Infer_Dere": (475, 276),
                            "Examn_Fis_Infer_Izquierda": (475, 289),
                            "Examn_Fis_Reflejos_Tndinosos": (475, 315),
                            "Examn_Fis_Sencibilidad_Sup": (475, 330),
                            "Examn_Fis_Reflejos_Pupilares": (475, 344),
                            "Examn_Fis_Ojo_Derecho": (475, 369),
                            "Examn_Fis_Ojo_Izquierdo": (475, 384),
                            "Examn_Fis_Oido_Derecho": (475, 410),
                            "Examn_Fis_Oido_Izquierdo": (475, 424),
                            "Examn_Fis_Descripcion": (62, 464),
                            "Laboratorio": (127, 496),
                            "Rx": (127, 510),
                            "Audiometria": (127, 523),
                            "Optometria": (127, 536),
                            "Ekg": (127, 550),
                            "Diagnostico_1": (64, 597),
                            "Diagnostico_2": (64, 608),
                            "Diagnostico_3": (64, 620),
                            "Diagnostico_4": (64, 634),
                            "Cie10_1": (350, 597),
                            "Cie10_2": (350, 608),
                            "Cie10_3": (350, 620),
                            "Cie10_4": (350, 634),
                            "Apto": (92, 685),
                            "Apto_Obsv": (226, 685),
                            "Apto_Limit": (375, 685),
                            "No_Apto": (487, 685),
                            "Apt_Med_Obsv": (127, 707),
                            "Apt_Med_Limit": (127, 720),
                        }

                        positions_page3 = {}

                        # Imprimir la "X" en la posición correspondiente a 'Droga'
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
                                        page.insert_text(
                                            position,
                                            str(field_value),
                                            fontsize=8,
                                            color=(0, 0, 0),
                                        )
                                    else:
                                        print(
                                            f"El campo '{field_name}' está vacío en response_data"
                                        )

                            # Imprimir la imagen de la firma en el PDF
                            firma_colaborador = response_data.get(
                                "Firma_Colaborador", ""
                            )
                            firma_doctor = base_firma_doc

                        elif page_num == 1:
                            for field_name, position in positions_page2.items():
                                if field_name in response_data:
                                    field_value = response_data[field_name]
                                    print(
                                        f"Campo '{field_name}' actualizado con valor: {field_value}"
                                    )
                                    page.insert_text(
                                        position,
                                        str(field_value),
                                        fontsize=6,
                                        color=(0, 0, 0),
                                    )

                            act_ext = response_data.get("Act_Extralaborales", "")

                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            droga_rect = fitz.Rect(60, 36, 506, 65)

                            page.insert_textbox(
                                droga_rect,
                                act_ext,
                                fontsize=6,
                                color=(0, 0, 0),
                                align=fitz.TEXT_ALIGN_LEFT,
                                lineheight=1.6,
                            )

                        elif page_num == 2:
                            for field_name, position in positions_page3.items():
                                if field_name in response_data:
                                    field_value = response_data[field_name]
                                    print(
                                        f"Campo '{field_name}' actualizado con valor: {field_value}"
                                    )
                                    page.insert_text(
                                        position,
                                        str(field_value),
                                        fontsize=6,
                                        color=(0, 0, 0),
                                    )

                            recom = response_data.get("Recom_Tto", "")

                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            droga_rect = fitz.Rect(60, 31, 506, 65)

                            page.insert_textbox(
                                droga_rect,
                                recom,
                                fontsize=6,
                                color=(0, 0, 0),
                                align=fitz.TEXT_ALIGN_LEFT,
                                lineheight=1.6,
                            )

                            inf_gen = response_data.get("Inf_Med_Gen", "")

                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            inf_rec = fitz.Rect(60, 75, 506, 110)

                            page.insert_textbox(
                                inf_rec,
                                inf_gen,
                                fontsize=6,
                                color=(0, 0, 0),
                                align=fitz.TEXT_ALIGN_LEFT,
                                lineheight=1.6,
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
                                        180 + 200, 670 - 555, 280 + 200, 705 - 550
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

                                    # Proceso de la firma del doctor
                            if firma_doctor:
                                if firma_doctor.startswith("data:image/png;base64,"):
                                    firma_doctor = firma_doctor.split(",")[1]

                                if len(firma_doctor) % 4:
                                    firma_doctor += "=" * (4 - len(firma_doctor) % 4)

                                try:
                                    print("Procesando firma doctor...", firma_doctor)
                                    data_sign = resize_image_base64(
                                        firma_doctor, 450, 450
                                    )
                                    REDUCED_SIGN = base64.b64decode(data_sign)
                                    signature_position = fitz.Rect(
                                        370 - 250, 670 - 569, 475 - 250, 705 - 500
                                    )

                                    page.insert_image(
                                        signature_position, stream=REDUCED_SIGN
                                    )
                                    print("Firma doctor añadida.")
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
                        download_name="FICHA_PREOCUPACIONAL_" + cedula + ".pdf",
                        mimetype="application/pdf",
                    )

                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    return render_template(
                        "dashboard/dashboard_preocupacional.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_preocupacional.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: PDF,  {e}")
                return render_template(
                    "dashboard/dashboard_preocupacional.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_preocupacional.html")

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
                    f"{BASE_URL}/FormDepMedico/Cargar/fichaPreocupacional",
                    json=payload,
                    headers={"AuthKey": "jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s"},
                    verify=False,
                )

                if response.status_code == 201:

                    response_data = response.json()

                    edad = "Edad:  " + response_data.get("Edad")
                    menarquia = "Menarquia: " + response_data.get("Gin_Menarquia")
                    regular = "Ciclos: R " + response_data.get("Gin_Ciclos_R")
                    iregular = f"Ciclos: R   " + response_data.get("Gin_Ciclos_R")
                    fum = "FUM:   " + response_data.get("Gin_Fum")
                    gestas = "GESTAS:   " + response_data.get("Gin_Gestas")
                    partos = "PARTOS:   " + response_data.get("Gin_Partos")
                    cesarea = "CESAREA:   " + response_data.get("Gin_Cesarea")
                    aborto = "ABORTO:   " + response_data.get("Gin_Aborto")
                    pap = "PAP:   " + response_data.get("Gin_Pap")
                    colpos = "COLPOS:   " + response_data.get("Gin_Colpos")
                    eco_mama = "Eco Mama:   " + response_data.get("Gin_Eco_Mama")
                    mamografia = "Mamografia:   " + response_data.get("Gin_Mamografia")
                    prost = "AG Prost:   " + response_data.get("Ap_Ag_Prost")
                    eco_prost = "Eco Prost:   " + response_data.get("Ap_Eco_Prost")
                    ap_obs = "Obsv.:   " + response_data.get("Ap_Obsv")
                    accid_calf = "Calificado:  " + response_data.get(
                        "Accidente_Trabajo"
                    )
                    enf_calf = "Calificado:  " + response_data.get("Enfermedad_Prof")
                    cardi = "Car-vasc  " + response_data.get("Car_Vasc")
                    meta = "Metabolica  " + response_data.get("Metabolica")
                    neur = "Neurolog.  " + response_data.get("Neurologica")
                    onco = "Onco.  " + response_data.get("Onco")
                    infec = "Infec.  " + response_data.get("Infec")
                    here = "Hereditaria  " + response_data.get("Hereditaria")
                    piel = "Piel y anexo  " + response_data.get("Org_Piel")
                    endo = "Endocrino  " + response_data.get("Org_Endocrino")
                    resp = "Respiratorio  " + response_data.get("Org_Respiratorio")
                    nerv = "Nervioso  " + response_data.get("Org_Nervioso")
                    dig = "Digestivo  " + response_data.get("Org_Digestivo")
                    cardio = "Cardio-Vascular " + response_data.get("Org_Card_Vacular")
                    musc = "Mus-esq  " + response_data.get("Org_Mus_Esq")
                    hemo = "Hemolinf  " + response_data.get("Org_Hemolinf")
                    org_sent = "Org. Sent  " + response_data.get("Org_Sent")
                    gen_uri = "Gen-uri  " + response_data.get("Org_Gen_Uri")

                    les = "Lesbiana  " + response_data.get("Ori_Lesbiana")
                    gay = "Gay  " + response_data.get("Ori_Gay")
                    bi = "Bisexual  " + response_data.get("Ori_Bisexual")
                    hete = "Hetero  " + response_data.get("Ori_Hetero")
                    ori_om = "Omitir Informacion  " + response_data.get("Ori_Omitir")

                    fem = "Femenino  " + response_data.get("Iden_Fem")
                    masc = "Masculino  " + response_data.get("Iden_Masc")
                    trans = "Transgenero  " + response_data.get("Iden_Transg")
                    ide_om = "Omitir Informacion  " + response_data.get("Iden_Omitir")

                    apto = "APTO  " + response_data.get("Apto")
                    apto_ob = "APTO en Observacion  " + response_data.get("Apto_Obsv")
                    apto_lim = "APTO con limitaciones  " + response_data.get(
                        "Apto_Limit"
                    )
                    no_apto = "NO APTO  " + response_data.get("No_Apto")

                    presion = "Presion Arterial  " + response_data.get("Sig_Pres_Art")
                    temp = "Temp  " + response_data.get("Sig_Temp")
                    fc = "FC  " + response_data.get("Sig_Fc")
                    sat = "sat. Ox.  " + response_data.get("Sig_Sat_Ox")
                    fr = "FR  " + response_data.get("Sig_Fr")
                    peso = "Peso  " + response_data.get("Sig_Peso")
                    talla = "Talla  " + response_data.get("Sig_Talla")
                    imc = "IMC  " + response_data.get("Riego_8")
                    biotipo = "Biotipo  " + response_data.get("Sig_Biotico")
                    atleti = "Atleti.  " + response_data.get("Sig_Atleti")
                    atletico = "Picn.  " + response_data.get("Sig_Atletico")
                    picn = "Aletico  " + response_data.get("Sig_Picn")

                    coordinates = {
                        "H3": response_data.get("Cedula", "N/A"),
                        "C8": response_data.get("Nombre", "N/A"),
                        "H6": response_data.get("Grupo_sanguineo", "N/A"),
                        "H10": response_data.get("Religion", "N/A"),
                        "B10": edad,
                        "D10": response_data.get("Discapacidad", "N/A"),
                        "C12": response_data.get("Puesto_Trabajo", "N/A"),
                        "G12": response_data.get("Activ_Relevante", "N/A"),
                        "F10": response_data.get("Porc_Discapacidad", "N/A"),
                        "B25": response_data.get("Antced_Clin_Quir", "N/A"),
                        "B29": menarquia,
                        "D29": fum,
                        "E29": gestas,
                        "F29": partos,
                        "G29": cesarea,
                        "H29": aborto,
                        "E30": pap,
                        "F30": colpos,
                        "G30": eco_mama,
                        "H30": mamografia,
                        "B33": prost,
                        "C33": eco_prost,
                        "D33": ap_obs,
                        "C14": les,
                        "D14": gay,
                        "E14": bi,
                        "F14": hete,
                        "G14": ori_om,
                        "C16": fem,
                        "D16": masc,
                        "E16": trans,
                        "G16": ide_om,
                        "B130": apto,
                        "C130": apto_ob,
                        "E130": apto_lim,
                        "H130": no_apto,
                        "C35": response_data.get("Act_Fisica", "N/A"),
                        "D35": response_data.get("Act_Fisica_Obsv", "N/A"),
                        "C36": response_data.get("Medi_Actual", "N/A"),
                        "D36": response_data.get("Medi_Actual_Obsv", "N/A"),
                        "C37": response_data.get("Alcohol", "N/A"),
                        "D37": response_data.get("Alcohol_Obsv", "N/A"),
                        "C38": response_data.get("Tabaco", "N/A"),
                        "D38": response_data.get("Tabaco_Obsv", "N/A"),
                        "C39": response_data.get("Otros", "N/A"),
                        "D39": response_data.get("Otros_Obsv", "N/A"),
                        "B45": response_data.get("Empresa_1", "N/A"),
                        "C45": response_data.get("Puesto_1", "N/A"),
                        "D45": response_data.get("Actividad_1", "N/A"),
                        "E45": response_data.get("Tiempo_1", "N/A"),
                        "F45": response_data.get("Riego_1", "N/A"),
                        "H45": response_data.get("Antc_Observ_1", "N/A"),
                        "B46": response_data.get("Empresa_2", "N/A"),
                        "C46": response_data.get("Puesto_2", "N/A"),
                        "D46": response_data.get("Actividad_2", "N/A"),
                        "E46": response_data.get("Tiempo_2", "N/A"),
                        "F46": response_data.get("Riego_2", "N/A"),
                        "H46": response_data.get("Antc_Observ_2", "N/A"),
                        "B47": response_data.get("Empresa_3", "N/A"),
                        "C47": response_data.get("Puesto_3", "N/A"),
                        "D47": response_data.get("Actividad_3", "N/A"),
                        "E47": response_data.get("Tiempo_3", "N/A"),
                        "F47": response_data.get("Riego_3", "N/A"),
                        "H47": response_data.get("Antc_Observ_3", "N/A"),
                        "B48": response_data.get("Empresa_4", "N/A"),
                        "C48": response_data.get("Puesto_4", "N/A"),
                        "D48": response_data.get("Actividad_4", "N/A"),
                        "E48": response_data.get("Tiempo_4", "N/A"),
                        "F49": response_data.get("Riego_4", "N/A"),
                        "H49": response_data.get("Antc_Observ_4", "N/A"),
                        "C52": response_data.get("Accidente_Trabajo_Calf_1", "N/A"),
                        "F52": accid_calf,
                        "H52": response_data.get("Accidente_Trabajo_Fecha", "N/A"),
                        "C54": response_data.get("Enfermedad_Prof_Calf_1", "N/A"),
                        "F54": enf_calf,
                        "H54": response_data.get("Enfermedad_Prof_Fecha", "N/A"),
                        "B58": cardi,
                        "C58": meta,
                        "D58": neur,
                        "E58": onco,
                        "F58": infec,
                        "G58": here,
                        "C65": response_data.get("Fact_Ruido", "N/A"),
                        "C66": response_data.get("Fact_Iluminacion", "N/A"),
                        "C67": response_data.get("Fact_Ventilacion", "N/A"),
                        "C68": response_data.get("Fact_Caidas", "N/A"),
                        "C69": response_data.get("Fact_Atrope", "N/A"),
                        "C70": response_data.get("Fact_Caida_Desniv", "N/A"),
                        "C106": response_data.get("Examn_Fis_Inspeccion", "N/A"),
                        "C107": response_data.get("Examn_Fis_Palpacion", "N/A"),
                        "C108": response_data.get("Examn_Fis_Percsusion", "N/A"),
                        "E65": response_data.get("Fact_Polvo", "N/A"),
                        "E66": response_data.get("Fact_Liquidos", "N/A"),
                        "E67": response_data.get("Fact_Virus", "N/A"),
                        "E68": response_data.get("Fact_Post_Forz", "N/A"),
                        "E69": response_data.get("Fact_Mov_Rep", "N/A"),
                        "E70": response_data.get("Fact_Monotomia", "N/A"),
                        "H65": response_data.get("Fact_Alta_Respo", "N/A"),
                        "H66": response_data.get("Fact_Conflict", "N/A"),
                        "H67": response_data.get("Fact_Sobrecarga", "N/A"),
                        "H68": response_data.get("Fact_Inestabilidad", "N/A"),
                        "H69": response_data.get("Fact_Relac_Interp", "N/A"),
                        "B76": response_data.get("Act_Extralaborales", "N/A"),
                        "B82": piel,
                        "B83": endo,
                        "C82": resp,
                        "C83": nerv,
                        "D82": dig,
                        "D83": cardio,
                        "E82": musc,
                        "F82": hemo,
                        "G82": org_sent,
                        "H82": gen_uri,
                        "B90": presion,
                        "D90": temp,
                        "E90": fc,
                        "F90": sat,
                        "H90": fr,
                        "B91": peso,
                        "C91": talla,
                        "D91": imc,
                        "E91": biotipo,
                        "F91": atleti,
                        "G91": picn,
                        "H91": atletico,
                        "B86": response_data.get("Org_Descripcion", "N/A"),
                        "C95": response_data.get("Examn_Fis_Cabeza", "N/A"),
                        "C96": response_data.get("Examn_Fis_Garganta", "N/A"),
                        "C97": response_data.get("Examn_Fis_Ojos", "N/A"),
                        "C98": response_data.get("Examn_Fis_Oidos", "N/A"),
                        "C99": response_data.get("Examn_Fis_Nariz", "N/A"),
                        "C100": response_data.get("Examn_Fis_Boca", "N/A"),
                        "C101": response_data.get("Examn_Fis_Dentudura", "N/A"),
                        "C103": response_data.get("Examn_Fis_Corazon", "N/A"),
                        "C104": response_data.get("Examn_Fis_Pulmones", "N/A"),
                        "C106": response_data.get("Examn_Fis_Inspeccion", "N/A"),
                        "C107": response_data.get("Examn_Fis_Palpacion", "N/A"),
                        "C108": response_data.get("Examn_Fis_Percsusion", "N/A"),
                        "E94": response_data.get("Examn_Fis_Extremidades", "N/A"),
                        "E96": response_data.get("Examn_Fis_Umbilical", "N/A"),
                        "E97": response_data.get("Examn_Fis_Ingual_Dere", "N/A"),
                        "E98": response_data.get("Examn_Fis_Clural_Dere", "N/A"),
                        "E99": response_data.get("Examn_Fis_Inguinal_Izquierdo", "N/A"),
                        "E100": response_data.get("Examn_Fis_Clural_Izq", "N/A"),
                        "E102": response_data.get("Examn_Fis_Deformaciones", "N/A"),
                        "E103": response_data.get("Examn_Fis_Movilidad", "N/A"),
                        "E104": response_data.get("Examn_Fis_Masas_Musculares", "N/A"),
                        "E106": response_data.get("Examn_Fis_Tracto_Urinario", "N/A"),
                        "E107": response_data.get("Examn_Fis_Tracto_Genital", "N/A"),
                        "E108": response_data.get("Examn_Fis_Regio_Anoperineal", "N/A"),
                        "H96": response_data.get("Examn_Fis_Sup_Izquierda", "N/A"),
                        "H97": response_data.get("Examn_Fis_Infer_Dere", "N/A"),
                        "H98": response_data.get("Examn_Fis_Infer_Izquierda", "N/A"),
                        "H100": response_data.get(
                            "Examn_Fis_Reflejos_Tndinosos", "N/A"
                        ),
                        "H101": response_data.get("Examn_Fis_Sencibilidad_Sup", "N/A"),
                        "H102": response_data.get(
                            "Examn_Fis_Reflejos_Pupilares", "N/A"
                        ),
                        "H104": response_data.get("Examn_Fis_Ojo_Derecho", "N/A"),
                        "H105": response_data.get("Examn_Fis_Ojo_Izquierdo", "N/A"),
                        "H107": response_data.get("Examn_Fis_Oido_Derecho", "N/A"),
                        "H108": response_data.get("Examn_Fis_Oido_Izquierdo", "N/A"),
                        "B111": response_data.get("Examn_Fis_Descripcion", "N/A"),
                        "C114": response_data.get("Laboratorio", "N/A"),
                        "C115": response_data.get("Rx", "N/A"),
                        "C116": response_data.get("Audiometria", "N/A"),
                        "C117": response_data.get("Optometria", "N/A"),
                        "C118": response_data.get("Ekg", "N/A"),
                        "B122": response_data.get("Diagnostico_1", "N/A"),
                        "B123": response_data.get("Diagnostico_2", "N/A"),
                        "B124": response_data.get("Diagnostico_3", "N/A"),
                        "B125": response_data.get("Diagnostico_4", "N/A"),
                        "F122": response_data.get("Cie10_1", "N/A"),
                        "F123": response_data.get("Cie10_2", "N/A"),
                        "F124": response_data.get("Cie10_3", "N/A"),
                        "F125": response_data.get("Cie10_4", "N/A"),
                        "C132": response_data.get("Apt_Med_Obsv", "N/A"),
                        "C133": response_data.get("Apt_Med_Limit", "N/A"),
                        "B140": response_data.get("Recom_Tto", "N/A"),
                        "B145": response_data.get("Inf_Med_Gen", "N/A"),
                    }

                    socializacion_personal = response_data.get(
                        "Socializacion_personal", "N/A"
                    )

                    if socializacion_personal == "Si":
                        coordinates["H49"] = "X"
                    elif socializacion_personal == "No":
                        coordinates["J49"] = "X"
                    else:
                        print("No hay valor")

                    factores = response_data.get("Fact_psico_sociales", "N/A")

                    if factores == "No":
                        coordinates["I29"] = "X"
                    elif factores == "Si":
                        coordinates["I31"] = "X"
                    else:
                        print("No hay valor")

                    # Cargar el archivo Excel existente
                    file_path = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "static",
                        "files",
                        "FICHA_PREOCUPACIONAL.xlsx",
                    )

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb["pagina 1"]

                    # Escribir datos en las celdas según el diccionario de coordenadas
                    for cell, value in coordinates.items():
                        ws[cell] = value

                    # Procesar y redimensionar firma del colaborador
                    firma_colaborador = response_data.get("Firma_Colaborador", "")
                    firma_doc = base_firma_doc
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
                                "PRE_TEMP.png",
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, "wb") as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(
                                img_colaborador, "D148"
                            )  # Ajusta la posición según sea necesario
                            print("Firma del colaborador añadida.")

                        except (base64.binascii.Error, ValueError) as e:
                            print(f"Error al procesar la firma del colaborador: {e}")

                    if firma_doc:
                        if firma_doc.startswith("data:image/png;base64,"):
                            firma_doc = firma_doc.split(",")[1]
                        if len(firma_doc) % 4:
                            firma_doc += "=" * (4 - len(firma_doc) % 4)

                        try:
                            print("Procesando firma del colaborador...")
                            data_sign = resize_image_base64(
                                firma_doc, 250, 150
                            )  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            tempxlsx1 = os.path.join(
                                os.path.dirname(__file__),
                                "..",
                                "..",
                                "static",
                                "files",
                                "PRE_TEMP2.png",
                            )

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, "wb") as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(
                                img_colaborador, "G148"
                            )  # Ajusta la posición según sea necesario
                            print("Firma del colaborador añadida.")

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
                        download_name=f"FICHA_PREOCUPACIONAL_{cedula}.xlsx",
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, "error")
                    print("Error en la respuesta de la API: " + response.text)
                    return render_template(
                        "dashboard/dashboard_preocupacional.html",
                        errores={},
                        form_data=form_data,
                    )

            except requests.exceptions.RequestException as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: Request, {e}")
                return render_template(
                    "dashboard/dashboard_preocupacional.html",
                    errores={},
                    form_data=form_data,
                )

            except Exception as e:
                flash(f"Ocurrió un error al procesar el formulario: {e}", "error")
                print(f"Error: EXCEL,  {e}")
                return render_template(
                    "dashboard/dashboard_preocupacional.html",
                    errores={},
                    form_data=form_data,
                )

        return render_template("dashboard/dashboard_preocupacional.html")
