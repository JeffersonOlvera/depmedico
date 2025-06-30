from flask import flash, redirect, render_template, request, session, url_for
from pydantic import ValidationError
from app.drogas.drogas_service import DrogaService
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
from app.drogas.drogas_schema import DrogaSchema


service = DrogaService()


class DrogaController:
    def form(self):
        form_data = {}
        errores = {}

        return render_template(
            "forms/colaborador/registro_drogas.html",
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
                    url_for("droga.formulario_success")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/colaborador/registro_drogas.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/colaborador/registro_drogas.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/colaborador/registro_drogas.html",
                errores={},
                form_data=form_data,
            )

    def _preparar_payload(self, form_data, usuario):
        """Prepara el payload para enviar a la API"""
        return {
            "usuario_registro": session.get("nombreColaborador", "No disponible"),
            "tipo_ficha": "ConsumoDroga",
            "tipo_sangre": form_data.get("tipo_sangre", ""),
            "fecha_apertura_F_RPD": form_data.get("fecha_apertura_F_RPD", ""),
            "cedula": session.get("cedula", "No disponible"),
            "nombre": session.get("nombreColaborador", "No disponible"),
            "edad": form_data.get("edad", ""),
            "dimicilio": form_data.get("dimicilio", ""),
            "telefono": form_data.get("telefono", ""),
            "profesion": form_data.get("profesion", ""),
            "religion": form_data.get("religion", ""),
            "estado_civil": form_data.get("estado_civil", ""),
            "cargo": form_data.get("cargo", ""),
            "email": form_data.get("email", ""),
            "nivel_instrucción": form_data.get("nivel_instrucción", ""),
            "etnia": form_data.get("etnia", ""),
            "disca_auditiva": form_data.get("disca_auditiva", ""),
            "disca_fisica": form_data.get("disca_fisica", ""),
            "disca_intelectual": form_data.get("disca_intelectual", ""),
            "lenguaje": form_data.get("lenguaje", ""),
            "psico_social": form_data.get("psico_social", ""),
            "visual": form_data.get("visual", ""),
            "droga": form_data.get("droga", ""),
            "droga_detalles": form_data.get("droga_detalles", ""),
            "tratamiento": form_data.get("tratamiento", ""),
            "factores_psicosociales_otros": form_data.get(
                "factores_psicosociales_otros", ""
            ),
            "factores_psicosociales": form_data.get("factores_psicosociales", ""),
            "frecuencia_consumo": form_data.get("frecuencia_consumo", ""),
            "porcentaje_disca": form_data.get("porcentaje_disca", ""),
            "enfer_catastrofica": form_data.get("enfer_catastrofica", ""),
            "enfer_cron_transmi": form_data.get("enfer_cron_transmi", ""),
            "enfer_cron_notransmi": form_data.get("enfer_cron_notransmi", ""),
            "diag_presuntivo": form_data.get("diag_presuntivo", ""),
            "trabajador_sustituto": form_data.get("trabajador_sustituto", ""),
            "exam_preocupacionales": form_data.get("exam_preocupacionales", ""),
            "firma_colaborador": form_data.get("firma_colaborador", ""),
            "status": "Pendiente",
        }

    def actualizar(self):
        """Procesa y guarda el formulario ocupacional"""
        try:
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")

            payload = {**form_data, "usuario_actualizacion": usuario, "status": "Completada", "tipo_ficha": "Droga"}

            data_validated = DrogaSchema(**payload).dict()

            response = service.actualizar_formulario(data_validated)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/medico/form_drogas_doc.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_drogas_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_drogas_doc.html",
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
                "forms/medico/form_drogas_doc.html", errores={}, form_data=form_data
            )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_drogas_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_drogas_doc.html",
                errores={},
                form_data=form_data,
            )
            
    def listar(self):
        return service.obtener_todas()


    def dashboard(self):
        return render_template("dashboard/dashboard_drogas.html")
    
    def pdf(self):
        if request.method == 'POST':
            form_data = request.form.to_dict()
            cedula = form_data.get('cedula')
            session['cedula'] = cedula

            payload = {
                "cedula": cedula
            }
            print('CEDULA: ', cedula)
            try:
                # Realiza una solicitud POST a la API con la cédula
                response = requests.post(
                    'https://192.168.137.16:47096/FormDepMedico/Cargar/fichaDrogas',
                    json=payload,
                    headers={'AuthKey': 'jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s'},
                    verify=False
                )

                if response.status_code == 201:
                    response_data = response.json()
                    print('Respuesta de la API:\n', response_data)

                    print(response_data.get('Fecha_actualizacion'))
                    pdf_path_input = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'files', 'FICHA_CONSUMO.pdf')
                    doc = fitz.open(pdf_path_input)  # Abre el documento PDF existente

                    # Procesa cada página del PDF
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        widgets = page.widgets()  # Obtener los campos de formulario

                        if widgets:
                            print(f"Páginas con campos de formulario: {page_num + 1}")
                            for widget in widgets:
                                field_name = widget.field_name
                                field_value = widget.field_value  # Usar field_value para obtener el valor del campo
                                
                                print(f"Campo: {field_name}, Valor actual: {field_value}")

                                
                            # Actualiza el campo si está presente en response_data
                                if field_name in response_data:
                                    if widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                        # Marca el checkbox si el valor es True en response_data
                                        widget.field_value = True if response_data[field_name] else False

                                        widget.update()
                                        print(f"Checkbox '{field_name}' actualizado con valor: {widget.field_value}")
                            
                                    else:
                                        # Para otros campos (como texto), actualiza el valor
                                        widget.field_value = response_data[field_name]
                                        widget.update()
                                        print(f"Campo '{field_name}' actualizado con valor: {response_data[field_name]}")


                        # Establece las posiciones para cada campo a actualizar
                        positions_page1 = {
                            "Cedula": (214, 85),
                            "Tipo_sangre" : (214, 102),                   
                            "Fecha_apertura_F_RPD": (214, 118),
                            
                            "Nombre" : (214, 150),
                            "Edad": (162, 165),
                            "Dimicilio" : (162, 182),
                            "Telefono" : (162, 200),
                            "Profesion" : (162, 215),
                            "Religion" : (162, 233),
                            
                            "Estado_civil" : (380, 167),
                            "Cargo" : (380, 182),
                            "Email" : (380, 215),
                            
                            "Disca_auditiva" : (435, 358),
                            "Disca_fisica" : (435, 375),
                            "Disca_intelectual" : (435, 392),
                            "Lenguaje" : (435, 408),
                            "Psico_social" : (435, 425),
                            "Visual" : (435, 441),
                            
                            "Enfer_catastrofica" : (435, 492),
                            "Enfer_cron_transmi" : (435, 508),
                            "Enfer_cron_notransmi" : (435, 524),
                            "Diag_presuntivo" : (435, 541),
                            
                            

                        }
                                        
                        intruccion = response_data.get('Nivel_instrucción', 'N/A')
                        print(intruccion)
                        
                        if intruccion == 'basica':
                            positions_page1['intruccion'] = (204, 277)
                        elif intruccion == 'bachiller':
                            positions_page1['intruccion'] = (204, 294)
                        elif intruccion == 'tercer_nivel':
                            positions_page1['intruccion'] = (204, 311)
                        elif intruccion == 'tecnico_superior':
                            positions_page1['intruccion'] = (204, 325)
                        elif intruccion == 'tecnologo':
                            positions_page1['intruccion'] = (204, 344)
                        elif intruccion == 'licenciado':
                            positions_page1['intruccion'] = (204, 358)
                        elif intruccion == 'ingeniero':
                            positions_page1['intruccion'] = (204, 378)
                        elif intruccion == 'cuarto_nivel':
                            positions_page1['intruccion'] = (204, 394)
                        elif intruccion == 'especializacion':
                            positions_page1['intruccion'] = (204, 410)
                        elif intruccion == 'maestria':
                            positions_page1['intruccion'] = (204, 427)
                        elif intruccion == 'postgrado':
                            positions_page1['intruccion'] = (204, 443)
                        else:
                            print("Valor no valido")
                            
                            
                        porcentaje = response_data.get('Porcentaje_disca', 'N/A')
                        print(porcentaje)
                        
                        if porcentaje == '30':
                            positions_page1['porcentaje'] = (204, 490)
                        elif porcentaje == '40':
                            positions_page1['porcentaje'] = (204, 507)
                        elif porcentaje == '50':
                            positions_page1['porcentaje'] = (204, 521)
                        elif porcentaje == '60':
                            positions_page1['porcentaje'] = (204, 540)
                        elif porcentaje == '70':
                            positions_page1['porcentaje'] = (204, 557)
                        elif porcentaje == '80':
                            positions_page1['porcentaje'] = (204, 574)
                        elif porcentaje == '90':
                            positions_page1['porcentaje'] = (204, 590)
                        elif porcentaje == '100':
                            positions_page1['porcentaje'] = (204, 607)
                        else:
                            print("Valor no valido")

                        etnia = response_data.get('Etnia', 'N/A')
                        print(etnia)
                        
                        if etnia == 'mestizo':
                            positions_page1['etnia'] = (435, 277)
                        elif etnia == 'afro_ecuatoriano':
                            positions_page1['etnia'] = (435, 294)
                        elif etnia == 'blanco':
                            positions_page1['etnia'] = (435, 311)
                        elif etnia == 'otro':
                            positions_page1['etnia'] = (435, 327)
                        else:
                            print("Valor no valido")


                        etnia = response_data.get('Etnia', 'N/A')
                        print(etnia)
                        
                        if etnia == 'mestizo':
                            positions_page1['etnia'] = (435, 277)
                        elif etnia == 'afro_ecuatoriano':
                            positions_page1['etnia'] = (435, 294)
                        elif etnia == 'blanco':
                            positions_page1['etnia'] = (435, 311)
                        elif etnia == 'otro':
                            positions_page1['etnia'] = (435, 327)
                        else:
                            print("Valor no valido")
                        
                        sustituto = response_data.get('Trabajador_sustituto', 'N/A')
                        print(sustituto)
                        
                        if sustituto == 'Si':
                            positions_page1['sustituto'] = (436, 590)
                        elif sustituto == 'No':
                            positions_page1['sustituto'] = (436, 607)
                        
                        else:
                            print("Valor no valido")
                            
                                            
                        positions_page2 = {  

                        }

                        factores = response_data.get('Factores_psicosociales', 'N/A')
                        print('fACTORES:'+ factores)

                        if factores == 'no_aplica':
                            positions_page2['factores'] = (435, 472)
                        elif factores == 'agobio_tension_trabajo':
                            positions_page2['factores'] = (435, 488)
                        elif factores == 'acoso_laboral':
                            positions_page2['factores'] = (435, 507)
                        elif factores == 'cansancio_intenso':
                            positions_page2['factores'] = (435, 522)
                        elif factores == 'companeros_consumidores':
                            positions_page2['factores'] = (435, 539)
                        elif factores == 'contratos_precarios':
                            positions_page2['factores'] = (435, 556)
                        elif factores == 'curiosidad_efectos_drogas':
                            positions_page2['factores'] = (435, 572)
                        elif factores == 'dificultad_resolucion_problemas':
                            positions_page2['factores'] = (435, 588)
                        elif factores == 'niveles_tension':
                            positions_page2['factores'] = (435, 605)
                        elif factores == 'expendo_drogas_trabajo':
                            positions_page2['factores'] = (435, 620)
                        elif factores == 'familiares_consumidores':
                            positions_page2['factores'] = (435, 637)
                        elif factores == 'insatisfaccion_trabajo':
                            positions_page2['factores'] = (435, 652)
                        elif factores == 'insatisfaccion_trato_superiores':
                            positions_page2['factores'] = (435, 670)
                        elif factores == 'inseguridad_futuro_laboral':
                            positions_page2['factores'] = (435, 686)
                        elif factores == 'ausencias_hogar_laboral':
                            positions_page2['factores'] = (435, 704)
                        elif factores == 'mala_situacion_economica_familia':
                            positions_page2['factores'] = (435, 716)
                        elif factores == 'conciliacion_tareas_domesticas':
                            positions_page2['factores'] = (435, 732)
                        elif factores == 'sentimiento_poco_capacitado':
                            positions_page2['factores'] = (435, 748)


                        else:
                            print("Valor no válido")



                        
                        
                        frecuencia_consumo = response_data.get('Frecuencia_consumo', 'N/A')
                        print(frecuencia_consumo)
                        
                        if frecuencia_consumo == '5-7 dias':
                            positions_page2['frecuencia_consumo'] = (246, 310)
                        elif frecuencia_consumo == '2-4 veces':
                            positions_page2['frecuencia_consumo'] = (246, 327)
                        elif frecuencia_consumo == '2-7 veces':
                            positions_page2['frecuencia_consumo'] = (246, 344)
                        elif frecuencia_consumo == '1 vez po semana':
                            positions_page2['frecuencia_consumo'] = (246, 360)
                        elif frecuencia_consumo == '2-12 veces Año':
                            positions_page2['frecuencia_consumo'] = (246, 376)
                        elif frecuencia_consumo == '1 vez al Año':
                            positions_page2['frecuencia_consumo'] = (246, 394)
                        elif frecuencia_consumo == 'No consume':
                            positions_page2['frecuencia_consumo'] = (246, 410)
                        else:
                            print("Valor no valido")

                        tratamiento = response_data.get('Tratamiento', 'N/A')
                        print(tratamiento)
                        
                        if tratamiento == 'Si':
                            positions_page2['tratamiento'] = (435, 309)
                        elif tratamiento == 'No':
                            positions_page2['tratamiento'] = (435, 325)
                        elif tratamiento == 'No consume':
                            positions_page2['tratamiento'] = (435, 342)

                        else:
                            print("Valor no valido")


                        Droga = response_data.get('Droga', 'N/A')
                        print(Droga)
                        # Definir la posición dependiendo del valor de 'Droga'
                        if Droga == 'No consume':
                            positions_page2['Droga'] = (435, 80)
                        elif Droga == 'Alcohol':
                            positions_page2['Droga'] = (246, 80)
                        elif Droga == 'Anfetaminas':
                            positions_page2['Droga'] = (246, 96)
                        elif Droga == 'Cigarrillo':
                            positions_page2['Droga'] = (246, 113)
                        elif Droga == 'Marihuana':
                            positions_page2['Droga'] = (246, 129)
                        elif Droga == 'Base de cocaina':
                            positions_page2['Droga'] = (246, 146)
                        elif Droga == 'Heroina':
                            positions_page2['Droga'] = (246, 162)
                        elif Droga == 'Tabaco':
                            positions_page2['Droga'] = (246, 179)
                        elif Droga == 'Morfina':
                            positions_page2['Droga'] = (246, 196)
                        elif Droga == 'Hongos':
                            positions_page2['Droga'] = (246, 212)
                        elif Droga == 'Drogas de sintesis':
                            positions_page2['Droga'] = (246, 228)
                        elif Droga == 'Inhalantes':
                            positions_page2['Droga'] = (246, 245)
                        elif Droga == 'Pegamentos':
                            positions_page2['Droga'] = (246, 245+17)
                        else:
                            positions_page2['Droga'] = (435, 112)

                        positions_page3 = {  

                        }

                        factores2 = response_data.get('Factores_psicosociales', 'N/A')
                        print('fACTORES:'+ factores2)
                        
                        if factores2 == 'tareas_rutinarias':
                            positions_page3['factores2'] = (435, 44)
                        elif factores2 == 'trabajos_nocturnos':
                            positions_page3['factores2'] = (435, 64)
                        elif factores2 == 'turnos_cambiantes':
                            positions_page3['factores2'] = (435, 79)
                        
                        Examen = response_data.get('Exam_preocupacionales', 'N/A')
                        print(Examen)
                        # Definir la posición dependiendo del valor de 'Examen'
                        if Examen == 'Si':
                            positions_page3['Examen'] = (381, 146)
                        elif Examen == 'No':
                            positions_page3['Examen'] = (438, 146)
                        else:
                            positions_page3['Examen'] = (300, 148)
        
                        # Imprimir la "X" en la posición correspondiente a 'Droga'
                        if page_num == 0:  # Primera página
                            for field_name, position in positions_page1.items():
                                if field_name == 'intruccion':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'porcentaje':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'etnia':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'sustituto':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                elif field_name in response_data:
                                    field_value = response_data[field_name]
                                    if field_value:  # Asegúrate de que el valor no sea nulo o vacío
                                        print(f"Campo '{field_name}' actualizado con valor: {field_value}")
                                        page.insert_text(position, str(field_value), fontsize=10, color=(0, 0, 0))
                                    else:
                                        print(f"El campo '{field_name}' está vacío en response_data")

                            # Imprimir la imagen de la firma en el PDF
                            firma_colaborador = response_data.get('Firma_colaborador', '')
                            firma_doctor = base_firma_doc
                        
                        elif page_num == 1:
                            for field_name, position in positions_page2.items():
                                if field_name == 'Droga':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'frecuencia_consumo':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'tratamiento':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'factores':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                elif field_name in response_data:
                                    field_value = response_data[field_name]
                                    print(f"Campo '{field_name}' actualizado con valor: {field_value}")
                                    page.insert_text(position, str(field_value), fontsize=6)


                            droga_otros = response_data.get('Droga_detalles', '')

                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            droga_rect = fitz.Rect(310, 156, 480, 225)

                            page.insert_textbox(droga_rect, droga_otros, fontsize=9, color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT, lineheight=1.7 )
                            
                        elif page_num == 2:
                            for field_name, position in positions_page3.items():
                                if field_name == 'Examen':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                if field_name == 'factores2':
                                    page.insert_text(position, 'X', fontsize=10, color=(0, 0, 0))
                                elif field_name in response_data:
                                    field_value = response_data[field_name]
                                    print(f"Campo '{field_name}' actualizado con valor: {field_value}")
                                    page.insert_text(position, str(field_value), fontsize=6)
                            
                                
                            
                            detalles_factores = response_data.get('Factores_psicosociales_otros', '')

                            # Ajusta el área (rectángulo) para los detalles de apto y recomendaciones
                            rect_detalles_apto = fitz.Rect(110+2, 104, 533+2, 115)

                            page.insert_textbox(rect_detalles_apto, detalles_factores, fontsize=9, color=(0, 0, 0), align=fitz.TEXT_ALIGN_JUSTIFY)
                            
                            # Proceso de la firma del colaborador
                            if firma_colaborador:
                                if firma_colaborador.startswith('data:image/png;base64,'):
                                    firma_colaborador = firma_colaborador.split(',')[1]

                                if len(firma_colaborador) % 4:
                                    firma_colaborador += '=' * (4 - len(firma_colaborador) % 4)

                                try:
                                    print('Procesando firma colaborador...', firma_colaborador)
                                    data_sign = resize_image_base64(firma_colaborador, 600, 600)
                                    REDUCED_SIGN = base64.b64decode(data_sign)

                                    signature_position = fitz.Rect(180-30, 670-490, 280-30, 705-490)
                                    page.insert_image(signature_position, stream=REDUCED_SIGN)
                                    print('Firma colaborador añadida.')
                                except (base64.binascii.Error, ValueError) as e:
                                    flash(f'Error al decodificar la firma: {e}', 'error')
                                    print(f'Error al decodificar la firma: {e}')
                                    
                                                # Proceso de la firma del doctor
                            if firma_doctor:
                                if firma_doctor.startswith('data:image/png;base64,'):
                                    firma_doctor = firma_doctor.split(',')[1]

                                if len(firma_doctor) % 4:
                                    firma_doctor += '=' * (4 - len(firma_doctor) % 4)

                                try:
                                    print('Procesando firma doctor...', firma_doctor)
                                    data_sign = resize_image_base64(firma_doctor, 600, 600)
                                    REDUCED_SIGN = base64.b64decode(data_sign)
                                    signature_position = fitz.Rect(370-20, 670-490, 475-20, 705-475)

                                    page.insert_image(signature_position, stream=REDUCED_SIGN)
                                    print('Firma doctor añadida.')
                                except (base64.binascii.Error, ValueError) as e:
                                    flash(f'Error al decodificar la firma: {e}', 'error')
                                    print(f'Error al decodificar la firma: {e}')                           


                    # Aplanar todas las páginas
                    new_doc = fitz.open()  # Crear un nuevo documento PDF

                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # Usa una matriz para mayor calidad
                        
                        # Crea una nueva página en el nuevo documento con el mismo tamaño
                        new_page = new_doc.new_page(width=pix.width, height=pix.height)
                        
                        # Inserta la imagen de la página original en la nueva página
                        new_page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), stream=pix.tobytes())

                    doc.close()  # Cierra el documento original
                    # Guarda el nuevo documento PDF aplanado en un archivo temporal
                    temp_file = NamedTemporaryFile(delete=False, suffix='.pdf')
                    pdf_path_output = temp_file.name
                    temp_file.close()  # Cerrar el handle antes de usar el archivo

                    # Ahora guardar el documento
                    new_doc.save(pdf_path_output)
                    new_doc.close()

                    # Envía el archivo PDF temporal como una descarga
                    print('PDF Completado')
                    return send_file(pdf_path_output, as_attachment=True, download_name='FICHA_CONSUMO_' + cedula + '.pdf', mimetype='application/pdf')


                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, 'error')
                    return render_template('dashboard/dashboard_drogas.html', errores={}, form_data=form_data)

            except requests.exceptions.RequestException as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: Request, {e}')
                return render_template('dashboard/dashboard_drogas.html', errores={}, form_data=form_data)

            except Exception as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: PDF,  {e}')
                return render_template('dashboard/dashboard_drogas.html', errores={}, form_data=form_data)

        return render_template('dashboard/dashboard_drogas.html')

    def excel(self):
        if request.method == 'POST':
            print('Entra al post')
            form_data = request.form.to_dict()
            cedula = form_data.get('cedula')
            session['cedula'] = cedula
            print("datos recibidos del formulario", form_data)
            
            payload = {
                "cedula": cedula
            }

            try:
                # Realiza una solicitud POST a la API con la cédula
                response = requests.post(
                    'https://192.168.137.16:47096/FormDepMedico/Cargar/fichaDrogas', 
                    json=payload,
                    headers={'AuthKey': 'jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s'},
                    verify=False
                )       

                
                if response.status_code == 201:

                    response_data = response.json()



                    coordinates = {
                        'F6': response_data.get('Cedula', 'N/A'),
                        'F7': response_data.get('Tipo_sangre','N/A'),
                        'F8': response_data.get('Fecha_apertura_F_RPD', 'N/A'),
                        
                        'F10': response_data.get('Nombre', 'N/A'),
                        'E11': response_data.get('Edad', 'N/A'),
                        'E12': response_data.get('Dimicilio', 'N/A'),
                        'E13': response_data.get('Telefono', 'N/A'),
                        'E14': response_data.get('Profesion', 'N/A'),
                        'E15': response_data.get('Religion', 'N/A'),

                        'I11': response_data.get('Estado_civil', 'N/A'),
                        'I12': response_data.get('Cargo', 'N/A'),
                        'I14': response_data.get('Email', 'N/A'),
                        
                        'J31': response_data.get('Enfer_catastrofica', 'N/A'),
                        'J32': response_data.get('Enfer_cron_transmi', 'N/A'),
                        'J33': response_data.get('Enfer_cron_notransmi', 'N/A'),
                        'J34': response_data.get('Diag_presuntivo', 'N/A'),
                        
                        'J23': response_data.get('Disca_auditiva'),
                        'J24': response_data.get('Disca_fisica'),
                        'J25': response_data.get('Disca_intelectual'),
                        'J26': response_data.get('Lenguaje'),
                        'J27': response_data.get('Psico_social'),
                        'J28': response_data.get('Visual'),
                        
                        'H49': response_data.get('Droga_detalles'),
                        'D91': response_data.get('Factores_psicosociales_otros'),
                        
                        
    
                    }

                    instruccion = response_data.get('Nivel_instrucción', 'N/A')
                    # Definir la coordenada dependiendo del valor de 'Droga'
                    if instruccion == 'basica':
                        coordinates['F18'] = 'X'
                    elif instruccion == 'bachiller':
                        coordinates['F19'] = 'X'
                    elif instruccion == 'tercer_nivel':
                        coordinates['F20'] = 'X'
                    elif instruccion == 'tecnico_superior':
                        coordinates['F21'] = 'X'
                    elif instruccion == 'tecnologo':
                        coordinates['F22'] = 'X'
                    elif instruccion == 'licenciado':
                        coordinates['F23'] = 'X'
                    elif instruccion == 'ingeniero':
                        coordinates['F24'] = 'X'
                    elif instruccion == 'cuarto_nivel':
                        coordinates['F25'] = 'X'
                    elif instruccion == 'especializacion':
                        coordinates['F26'] = 'X'
                    elif instruccion == 'maestria':
                        coordinates['F27'] = 'X'
                    elif instruccion == 'postgrado':
                        coordinates['F28'] = 'X'

                    else:
                        print("No hay valor") 

                    factores = response_data.get('Factores_psicosociales', 'N/A')
                    # Definir la coordenada dependiendo del valor de 'Nivel_instrucción'
                    if factores == 'no_aplica':
                        coordinates['I68'] = 'X'
                    elif factores == 'agobio_tension_trabajo':
                        coordinates['I69'] = 'X'
                    elif factores == 'acoso_laboral':
                        coordinates['I70'] = 'X'
                    elif factores == 'cansancio_intenso':
                        coordinates['I71'] = 'X'
                    elif factores == 'companeros_consumidores':
                        coordinates['I72'] = 'X'
                    elif factores == 'contratos_precarios':
                        coordinates['I73'] = 'X'
                    elif factores == 'curiosidad_efectos_drogas':
                        coordinates['I74'] = 'X'
                    elif factores == 'dificultad_resolucion_problemas':
                        coordinates['I75'] = 'X'
                    elif factores == 'niveles_tension':
                        coordinates['I76'] = 'X'
                    elif factores == 'expendo_drogas_trabajo':
                        coordinates['I77'] = 'X'
                    elif factores == 'familiares_consumidores':
                        coordinates['I78'] = 'X'
                    elif factores == 'insatisfaccion_trabajo':
                        coordinates['I79'] = 'X'
                    elif factores == 'insatisfaccion_trato_superiores':
                        coordinates['I80'] = 'X'
                    elif factores == 'inseguridad_futuro_laboral':
                        coordinates['I81'] = 'X'
                    elif factores == 'ausencias_hogar_laboral':
                        coordinates['I82'] = 'X'
                    elif factores == 'mala_situacion_economica_familia':
                        coordinates['I83'] = 'X'
                    elif factores == 'conciliacion_tareas_domesticas':
                        coordinates['I84'] = 'X'
                    elif factores == 'sentimiento_poco_capacitado':
                        coordinates['I85'] = 'X'
                    elif factores == 'tareas_rutinarias':
                        coordinates['I86'] = 'X'
                    elif factores == 'trabajos_nocturnos':
                        coordinates['I87'] = 'X'
                    elif factores == 'turnos_cambiantes':
                        coordinates['I88'] = 'X'
                    else:
                        print("No hay valor")



                    etnia = response_data.get('Etnia', 'N/A')
                    if etnia == 'mestizo':
                        coordinates['J18'] = 'X'
                    elif etnia == 'afro_ecuatoriano':
                        coordinates['J19'] = 'X'
                    elif etnia == 'blanco':
                        coordinates['J20'] = 'X'
                    elif etnia == 'otro':
                        coordinates['J21'] = 'X'
                    else:
                        print("No hay valor") 

                    sustituto = response_data.get('Trabajador_sustituto', 'N/A')
                    if sustituto == 'Si':
                        coordinates['J37'] = 'X'
                    elif sustituto == 'No':
                        coordinates['J38'] = 'X'
                    else:
                        print("No hay valor") 

                    tratamiento = response_data.get('Tratamiento', 'N/A')
                    if tratamiento == 'Si':
                        coordinates['J58'] = 'X'
                    elif tratamiento == 'No':
                        coordinates['J59'] = 'X'
                    elif tratamiento == 'No consume':
                        coordinates['J60'] = 'X'
                    else:
                        print("No hay valor") 


                    droga = response_data.get('Droga', 'N/A')
                    # Definir la coordenada dependiendo del valor de 'Droga'
                    if droga == 'No Consume':
                        coordinates['J44'] = 'X'
                    elif droga == 'Alcohol':
                        coordinates['F44'] = 'X'
                    elif droga == 'Anfetaminas':
                        coordinates['F45'] = 'X'
                    elif droga == 'Cigarrillo':
                        coordinates['F46'] = 'X'
                    elif droga == 'Marihuana':
                        coordinates['F47'] = 'X'
                    elif droga == 'Base de cocaina':
                        coordinates['F48'] = 'X'
                    elif droga == 'Heroina':
                        coordinates['F49'] = 'X'
                    elif droga == 'Tabaco':
                        coordinates['F50'] = 'X'
                    elif droga == 'Morfina':
                        coordinates['F51'] = 'X'
                    elif droga == 'Hongos':
                        coordinates['F52'] = 'X'
                    elif droga == 'Drogas de sintesis':
                        coordinates['F53'] = 'X'
                    elif droga == 'Inhalantes':
                        coordinates['F54'] = 'X'
                    elif droga == 'Pegamentos':
                        coordinates['F55'] = 'X'
                    else:
                        print("No hay valor") 

                    frecuencia_consumo = response_data.get('Frecuencia_consumo', 'N/A')

                    if frecuencia_consumo == 'No consume':
                        coordinates['F64'] = 'X'
                    elif frecuencia_consumo == '5-7 dias':
                        coordinates['F58'] = 'X'
                    elif frecuencia_consumo == '2-4 veces':
                        coordinates['F59'] = 'X'
                    elif frecuencia_consumo == '2-7 veces':
                        coordinates['F60'] = 'X'
                    elif frecuencia_consumo == '1 vez por semana':
                        coordinates['F61'] = 'X'
                    elif frecuencia_consumo == '2-12 veces Año':
                        coordinates['F62'] = 'X'
                    elif frecuencia_consumo == '1 vez al Año':
                        coordinates['F63'] = 'X'
                    else:
                        print("No hay valor")
                        
                    porcentaje = response_data.get('Porcentaje_disca', 'N/A')

                    if porcentaje == '30':
                        coordinates['F31'] = 'X'
                    elif porcentaje == '40':
                        coordinates['F32'] = 'X'
                    elif porcentaje == '50':
                        coordinates['F33'] = 'X'
                    elif porcentaje == '60':
                        coordinates['F34'] = 'X'
                    elif porcentaje == '70':
                        coordinates['F35'] = 'X'
                    elif porcentaje == '80':
                        coordinates['F36'] = 'X'
                    elif porcentaje == '90':
                        coordinates['F37'] = 'X'
                    elif porcentaje == '100':
                        coordinates['F38'] = 'X'
                    else:
                        print("No hay valor")

                    socializacion_personal = response_data.get('Socializacion_personal', 'N/A')

                    if socializacion_personal == 'Si':
                        coordinates['H49'] = 'X'
                    elif socializacion_personal == 'No':
                        coordinates['J49'] = 'X'
                    else:
                        print("No hay valor")       

                    factores = response_data.get('Fact_psico_sociales', 'N/A')

                    if factores == 'No':
                        coordinates['I29'] = 'X'
                    elif factores == 'Si':
                        coordinates['I31'] = 'X'
                    else:
                        print("No hay valor") 

                    # Cargar el archivo Excel existente
                    file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'files', 'FICHA_CONSUMO.xlsx')

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb['Hoja1']  

                    # Escribir datos en las celdas según el diccionario de coordenadas
                    for cell, value in coordinates.items():
                        ws[cell] = value

                    # Procesar y redimensionar firma del colaborador
                    firma_colaborador = response_data.get('Firma_colaborador', '')
                    firma_doc = base_firma_doc
                    if firma_colaborador:
                        if firma_colaborador.startswith('data:image/png;base64,'):
                            firma_colaborador = firma_colaborador.split(',')[1]
                        if len(firma_colaborador) % 4:
                            firma_colaborador += '=' * (4 - len(firma_colaborador) % 4)

                        try:
                            print('Procesando firma del colaborador...')
                            data_sign = resize_image_base64(firma_colaborador, 250, 150)  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            tempxlsx1 = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'files', 'SEGUIMIENTO_TEMP.png')

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, 'wb') as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(img_colaborador, 'D94')  # Ajusta la posición según sea necesario
                            print('Firma del colaborador añadida.')

                        except (base64.binascii.Error, ValueError) as e:
                            print(f'Error al procesar la firma del colaborador: {e}')

                    if firma_doc:
                        if firma_doc.startswith('data:image/png;base64,'):
                            firma_doc = firma_doc.split(',')[1]
                        if len(firma_doc) % 4:
                            firma_doc += '=' * (4 - len(firma_doc) % 4)

                        try:
                            print('Procesando firma del colaborador...')
                            data_sign = resize_image_base64(firma_doc, 250, 150)  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            tempxlsx1 = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'files', 'CONSUMO_TEMP.png')

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, 'wb') as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(img_colaborador, 'H94')  # Ajusta la posición según sea necesario
                            print('Firma del colaborador añadida.')

                        except (base64.binascii.Error, ValueError) as e:
                            print(f'Error al procesar la firma del doctor: {e}')


                    # Guardar el archivo Excel modificado en un buffer temporal
                    output = BytesIO()
                    wb.save(output)
                    output.seek(0)
                        
                    # Enviar el archivo Excel como respuesta para descarga
                    return send_file(output, as_attachment=True, download_name=f'FICHA_CONSUMO_{cedula}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                
                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, 'error')
                    print("Error en la respuesta de la API: " + response.text)
                    return render_template('dashboard/dashboard_drogas.html', errores={}, form_data=form_data)

            except requests.exceptions.RequestException as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: Request, {e}')
                return render_template('dashboard/dashboard_drogas.html', errores={}, form_data=form_data)

            except Exception as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: EXCEL,  {e}')
                return render_template('dashboard/dashboard_drogas.html', errores={}, form_data=form_data)

        return render_template('dashboard/dashboard_drogas.html')

