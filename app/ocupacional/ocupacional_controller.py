from flask import flash, redirect, render_template, request, session, url_for
from pydantic import ValidationError
from app.ocupacional.ocupacional_service import OcupacionalService
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
from datetime import date
from app.ocupacional.ocupacional_schema import OcupacionalSchema

service = OcupacionalService()

# Carpeta donde guardarás temporalmente las firmas (crear si no existe)
FIRMAS_PATH = os.path.join("static", "firmas_temp")
os.makedirs(FIRMAS_PATH, exist_ok=True)

class OcupacionalController:
    def form(self):
        fecha_actual = date.today().isoformat()  # 'YYYY-MM-DD'
        
        return render_template("forms/colaborador/registro_ocupacional.html", fecha=fecha_actual)

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
            "usuario_registro": usuario,
            "estatus": "Pendiente",
            "ci_colaborador": session.get("cedula", "No disponible"),
            "nombre_colaborador": session.get("nombreColaborador", "No disponible"),
            "edad": form_data.get("edad"),
            "sexo": form_data.get("sexo"),
            "cargo": form_data.get("cargo"),
            "tiempo_cargo": form_data.get("tiempo_cargo"),
            "antecep_clinicos": form_data.get("antecep_clinicos"),
            "antecep_quirurgicos": form_data.get("antecep_quirurgicos"),
            "act_fisica": form_data.get("act_fisica"),
            "act_fisica_obser": form_data.get("act_fisica_obser"),
            "medi_actual": form_data.get("medi_actual"),
            "medi_actual_obser": form_data.get("medi_actual_obser"),
            "alcohol": form_data.get("alcohol"),
            "alcohol_obser": form_data.get("alcohol_obser"),
            "tabaco": form_data.get("tabaco"),
            "tabaco_obser": form_data.get("tabaco_obser"),
            "otros": form_data.get("otros"),
            "otros_obser": form_data.get("otros_obser"),
            "incidente_trabajo": form_data.get("incidente_trabajo"),
            "accidente_trabajo": form_data.get("accidente_trabajo"),
            "accidente_trabajo_calif": form_data.get("accidente_trabajo_calif"),
            "accidente_trabajo_fecha": form_data.get(
                "accidente_trabajo_fecha", "0000-00-00"
            ),
            "enfermedad_prof": form_data.get("enfermedad_prof"),
            "enfermedad_prof_calif": form_data.get("enfermedad_prof_calif"),
            "enfermedad_prof_fecha": form_data.get(
                "enfermedad_prof_fecha", "0000-00-00"
            ),
            "antecf_cardio_vas": form_data.get("antecf_cardio_vas"),
            "antecf_metabotica": form_data.get("antecf_metabotica"),
            "antecf_neurologica": form_data.get("antecf_neurologica"),
            "antecf_oncologica": form_data.get("antecf_oncologica"),
            "antecf_infecciosa": form_data.get("antecf_infecciosa"),
            "antecf_hereditario": form_data.get("antecf_hereditario"),
            "antecf_observacion": form_data.get("antecf_observacion"),
            "inmuni_influenza": form_data.get("inmuni_influenza"),
            "inmuni_tetano": form_data.get("inmuni_tetano"),
            "inmuni_hepatitisB": form_data.get("inmuni_hepatitisB"),
            "inmuni_coviddosis": form_data.get("inmuni_coviddosis"),
            "firma_colaborador": form_data.get("firma_colaborador"),
            "fecha": form_data.get("fecha"),
        }

    def actualizar(self):
        """Procesa y guarda el formulario ocupacional"""
        try:
            form_data = request.form.to_dict()
            usuario = session.get("usuario", "No disponible")
            print("Datos recibidos del formulario:", form_data)
            print("FIRMA FORM:", form_data.get("firma_colaborador"))
            # Obtener la firma del formulario
            firma_formulario = form_data.get("firma_colaborador", "").strip()
            if firma_formulario:
                firma_final = firma_formulario
            else: 
                ruta_firma_guardada = session.get("firma_colaborador_path", "")
                cedula_sesion = session.get("firma_colaborador_cedula", "")
                cedula_form = form_data.get("cedula", "")

                # Verificar que la firma guardada pertenece al mismo usuario
                if ruta_firma_guardada and cedula_form == cedula_sesion and os.path.exists(ruta_firma_guardada):
                    with open(ruta_firma_guardada, "rb") as f:
                        firma_bytes = f.read()
                        firma_final = "data:image/png;base64," + base64.b64encode(firma_bytes).decode()
                else:
                    firma_final = ""


            payload = form_data.copy()
            payload.update({
                "usuario_actualizacion": usuario,
                "estatus": "Completada", 
                "tipo_ficha": "Ocupacional", 
                "firma_colaborador": firma_final
            })

            print("Firma final base64 (primeros 100 chars):", firma_final[:100])

            data_validated = OcupacionalSchema(**payload).dict()

            response = service.actualizar_formulario(data_validated)

            if response["success"]:
                flash("El formulario ha sido enviado con éxito.", "success")
                return redirect(
                    url_for("ocupacional.formulario_success", campaign="ocupacional")
                )
            else:
                flash(f'Error al enviar datos: {response["message"]}', "error")
                return render_template(
                    "forms/medico/form_ocupacional_doc.html",
                    errores={},
                    form_data=form_data,
                )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_ocupacional_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_ocupacional_doc.html",
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
            print("firma:", form_data.get("firma_colaborador", ""))
            firma_base64 = form_data.get("firma_colaborador", "")

            if firma_base64:
                    # Guardar la firma en un archivo temporal
                    timestamp = int(datetime.now().timestamp())
                    nombre_archivo = f"firma_{cedula}_{timestamp}.png"
                    ruta_archivo = os.path.join(FIRMAS_PATH, nombre_archivo)


                    with open(ruta_archivo, "wb") as f:
                        f.write(base64.b64decode(firma_base64.split(",")[-1]))
                    session['firma_colaborador_path'] = ruta_archivo
                    session['firma_colaborador_cedula'] = cedula

                    print("Firma guardada en:", ruta_archivo)
            else:
                    session['firma_colaborador_path'] = ""


            return render_template(
                "forms/medico/form_ocupacional_doc.html", errores={}, form_data=form_data
            )

        except ValidationError as e:
            print("Error de validación:", e.json())
            errores = {err["loc"][0]: err["msg"] for err in e.errors()}
            session["show_full_form"] = True
            return render_template(
                "forms/medico/form_ocupacional_doc.html",
                errores=errores,
                form_data=form_data,
                show_full_form=session.get("show_full_form", False),
            )

        except Exception as e:
            print("Error general:", str(e))
            flash(f"Ocurrió un error al procesar el formulario: {str(e)}", "error")
            return render_template(
                "forms/medico/form_ocupacional_doc.html",
                errores={},
                form_data=form_data,
            )

    def validar(self):
        excel_path = os.path.join(os.path.dirname(__file__), '..','..','static', 'files', 'CIE10.xlsx')
        df = pd.read_excel(excel_path)
        
        query = request.args.get('query', '').lower()
        if not query:
            return jsonify([])

        filtered_df = df[df['DESCRIPCION'].str.contains(query, case=False, na=False)]
        suggestions = filtered_df[['DESCRIPCION', 'COD_3']].to_dict(orient='records')

        return jsonify(suggestions)

    def listar(self, rango_fechas={}):
        return service.obtener_todas()

    def dashboard(self):
        return render_template("dashboard/dashboard_ocupacional.html")
    
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
                    'https://192.168.137.16:47096/FormDepMedico/Cargar/fichaOcupacional', 
                    json=payload,
                    headers={'AuthKey': 'jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s'},
                    verify=False
                )

                if response.status_code == 201:
                    response_data = response.json()
                    print('Respuesta de la API:\n', response_data)

                    pdf_path_input = os.path.join(os.path.dirname(__file__), '..','..','static', 'files', 'FICHA_OCUPACIONAL.pdf')
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
                            "Nombre_colaborador": (195, 133),  # Ajusta las coordenadas (x, y)
                            "Ci_colaborador": (455, 106),
                            "Edad": (150, 149),
                            "Sexo": (205, 149),
                            "Cargo": (295, 149),
                            "Tiempo_cargo": (455, 149),
                            "act_fisica": (196, 277),
                            "act_fisica_obser": (242, 278),
                            "medi_actual": (196, 290),
                            "medi_actual_obser": (242, 291),
                            "alcohol": (196, 304),
                            "alcohol_obser": (242, 304),
                            "tabaco": (196, 315),
                            "tabaco_obser": (242, 316),
                            "otros": (196, 327),
                            "otros_obser": (242, 328),

                            "incidente_trabajo": (180, 358),
                            "accidente_trabajo_calif": (180, 373),
                            "accidente_trabajo": (412, 372),
                            "accidente_trabajo_fecha": (450, 372),
                            "enfermedad_prof_calif": (180, 388),
                            "enfermedad_prof": (412, 387),
                            "enfermedad_prof_fecha": (450, 387),

                            "antecf_cardio_vas": (166, 416),
                            "antecf_metabotica": (230, 416),
                            "antecf_neurologica": (300, 416),
                            "antecf_oncologica": (374, 416),
                            "antecf_infecciosa": (444, 416),
                            "antecf_hereditario": (510, 416),

                            "fact_risg_trabajo_ruido": (206, 480),
                            "fact_risg_trabajo_polvos": (325, 480),
                            "fact_risg_trabajo_alta_respo": (483, 480),
                            "fact_risg_trabajo_iluminacion": (206, 495),
                            "fact_risg_trabajo_liquidos": (325, 495),
                            "fact_risg_trabajo_conflic_rol": (483, 495),
                            "fact_risg_trabajo_ventilacion": (206, 510),
                            "fact_risg_trabajo_virus": (325, 510),
                            "fact_risg_trabajo_sobrecarga_lab": (483, 510),
                            "fact_risg_trabajo_caidas_mismonivel": (206, 525),
                            "fact_risg_trabajo_posturas": (325, 525),
                            "fact_risg_trabajo_inestabilidad_lab": (483, 525),
                            "fact_risg_trabajo_atropellamiento_vehi": (206, 539),
                            "fact_risg_trabajo_mov_repetitivo": (325, 539),
                            "fact_risg_trabajo_rela_interp": (483, 539),
                            "fact_risg_trabajo_caidas_desnivel": (206, 551),
                            "fact_risg_trabajo_monotomia": (325, 551),

                            "sso_salud_mental": (256, 571),
                            "sso_riesgo_lab": (256, 582),
                            "sso_pausas_activas": (256, 593),

                            "inmuni_influenza": (222, 613),
                            "inmuni_tetano": (276, 613),
                            "inmuni_hepatitisB": (355, 613),
                            "inmuni_coviddosis": (452, 613),

                            "organosysis_piel_anexo": (163, 640),
                            "organosysis_genito_urinario": (163, 654),
                            "organosysis_respiratorio": (225, 640),
                            "organosysis_endocrino": (225, 654),
                            "organosysis_digestivo": (276, 640),
                            "organosysis_nervioso": (276, 654),
                            "organosysis_musculo_esqueletico": (354, 640),
                            "organosysis_cardiovascular": (354, 654),
                            "organosysis_hemolinf": (424, 640),
                            "organosysis_orgsentidos": (500, 640),
                            "organosysis_descripcion": (115, 686),
                            # Agrega más campos y sus posiciones aquí
                        }
                        
                        positions_page2 = {  
                            "examn_fis_garganta": (195, 154),      
                            "examn_fis_ojos": (195, 166),      
                            "examn_fis_oidos": (195, 178),
                            "examn_fis_nariz": (195, 190),
                            "examn_fis_boca": (195, 202),
                            "examn_fis_dentudura": (195, 215),
                            "examn_fis_corazon": (195, 238),
                            "examn_fis_pulmones": (195, 250),
                            "examn_fis_inspeccion": (195, 275),
                            "examn_fis_palpacion": (195, 287),
                            "examn_fis_percsusion": (195, 300),

                            "examn_fis_umbilical": (322, 155),      
                            "examn_fis_ingual_dere": (322, 167),      
                            "examn_fis_clural_dere": (322, 179),      
                            "examn_fis_inguinal_izquierdo": (322, 191),      
                            "examn_fis_clural_izq": (322, 203),      
                            "examn_fis_deformaciones": (322, 226),      
                            "examn_fis_movilidad": (322, 238),      
                            "examn_fis_masas_musculares": (322, 250),      
                            "examn_fis_tracto_urinario": (322, 275),      
                            "examn_fis_tracto_genital": (322, 288),      
                            "examn_fis_regio_anoperineal": (322, 300),      

                            "examn_fis_sup_izquierda": (483 , 155),      
                            "examn_fis_infer_dere": (483, 167),      
                            "examn_fis_infer_izquierda": (483, 179),      
                            "examn_fis_reflejos_tndinosos": (483, 203),          
                            "examn_fis_sencibilidad_sup": (483, 215),          
                            "examn_fis_reflejos_pupilares": (483, 226),          
                            "examn_fis_ojo_derecho": (483, 251),          
                            "examn_fis_ojo_izquierdo": (483, 264),          
                            "examn_fis_oido_derecho": (483, 287),          
                            "examn_fis_oido_izquierdo": (483, 300),          

                            "laboratorio": (180, 370),  
                            "rx": (180, 381),  
                            "audiometria": (180, 392),  
                            "optometria": (180, 403),  
                            "ekg": (180, 414),  

                            "cie10_1": (320, 445),  
                            "cie10_2": (320, 464),  
                            "cie10_3": (320, 482),  
                            "cie10_4": (320, 502),

                            "aptitud": (180, 578),  
                            "aptitud_observ": (180, 595),  
                            "aptitud_limitacion": (180, 614),  
                            "Fecha_actualizacion":  (295, 688), 
                        }

                        if page_num == 0:  # Primera página
                            for field_name, position in positions_page1.items():
                                if field_name in response_data:
                                    field_value = response_data[field_name]
                                    print(f"Campo '{field_name}' actualizado con valor: {field_value}")
                                    page.insert_text(position, str(field_value), fontsize=6)

                        elif page_num == 1:  # Segunda página
                            # Imprimir datos del segundo diccionario
                            for field_name, position in positions_page2.items():
                                if field_name in response_data:
                                    field_value = response_data[field_name]
                                    print(f"Campo '{field_name}' actualizado con valor: {field_value}")
                                    page.insert_text(position, str(field_value), fontsize=6)
                            # Imprimir la imagen de la firma en el PDF
                            firma_colaborador = response_data.get('firma_colaborador', '')
                            firma_doctor = base_firma_doc

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

                                    signature_position = fitz.Rect(370, 670, 475, 705)
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

                                    signature_position = fitz.Rect(180, 720-60, 280, 755-25)  # Ajustado 50 unidades más abajo

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
                    print("Se cierra el doc. Guardando...")            
                    # Guarda el nuevo documento PDF aplanado en un archivo temporal
                    temp_file = NamedTemporaryFile(delete=False, suffix='.pdf')
                    pdf_path_output = temp_file.name
                    temp_file.close()  # Cerrar el handle antes de usar el archivo

                    # Ahora guardar el documento
                    new_doc.save(pdf_path_output)
                    new_doc.close()

                    # Envía el archivo PDF temporal como una descarga
                    print('PDF Completado')
                    return send_file(pdf_path_output, as_attachment=True, download_name='FICHA_OCUPACIONAL_' + cedula + '.pdf', mimetype='application/pdf')


                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, 'error')
                    return render_template('dashboard/dashboard_ocupacional.html', errores={}, form_data=form_data)

            except requests.exceptions.RequestException as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: Request, {e}')
                return render_template('dashboard/dashboard_ocupacional.html', errores={}, form_data=form_data)

            except Exception as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: PDF,  {e}')
                return render_template('dashboard/dashboard_ocupacional.html', errores={}, form_data=form_data)

        return render_template('dashboard/dashboard_ocupacional.html')

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
                    'https://192.168.137.16:47096/FormDepMedico/Cargar/fichaOcupacional', 
                    json=payload,
                    headers={'AuthKey': 'jV+lYdQlv2IO0Gc1vZOeFomzl8eEt79s'},
                    verify=False
                )

                if response.status_code == 201:
                    response_data = response.json()
                    print(response_data)
                    # Diccionario de coordenadas
                    cual = "                        /Cual:"
                    accidente_trabajo = f"Calificado: {response_data.get('accidente_trabajo', 'N/A')}      Fecha:"
                    enfermedad_prof = f"Calificado: {response_data.get('enfermedad_prof', 'N/A')}      Fecha:"
                    inmuni_influenza = f"INFLUENZA:  {response_data.get('inmuni_influenza', 'N/A')}"
                    inmuni_tetano = f"TETANO:  {response_data.get('inmuni_tetano', 'N/A')}"
                    inmuni_hepatitisB = f"HEPATITIS B:  {response_data.get('inmuni_hepatitisB', 'N/A')}"
                    inmuni_coviddosis = f"COVID DOSIS #:  {response_data.get('inmuni_coviddosis', 'N/A')}"
                    
                    antecf_cardio_vas = f"Cardio-vascular:   {response_data.get('antecf_cardio_vas', 'N/A')}"
                    antecf_metabotica = f"Metabolica:   {response_data.get('antecf_metabotica', 'N/A')}"
                    antecf_neurologica = f"Neurologica:   {response_data.get('antecf_neurologica', 'N/A')}"
                    antecf_oncologica = f"Oncologica:   {response_data.get('antecf_oncologica', 'N/A')}"
                    antecf_infecciosa = f"Infecciosa:   {response_data.get('antecf_infecciosa', 'N/A')}"
                    antecf_hereditario = f"Hereditaria:   {response_data.get('antecf_hereditario', 'N/A')}"

                    organosysis_piel_anexo = f"Piel y anexo:              {response_data.get('organosysis_piel_anexo', 'N/A')}"
                    organosysis_genito_urinario = f"Genito-urinario:       {response_data.get('organosysis_genito_urinario', 'N/A')}"
                    organosysis_respiratorio = f"  Respiratorio:            {response_data.get('organosysis_respiratorio', 'N/A')}"
                    organosysis_endocrino = f"  Endocrino:              {response_data.get('organosysis_endocrino', 'N/A')}"
                    organosysis_digestivo = f"Digestivo:              {response_data.get('organosysis_digestivo', 'N/A')}"
                    organosysis_nervioso = f"Nervioso:              {response_data.get('organosysis_nervioso', 'N/A')}"
                    organosysis_musculo_esqueletico = f"Musculo-esqueletico:       {response_data.get('organosysis_musculo_esqueletico', 'N/A')}"
                    organosysis_cardiovascular = f"Cardio-Vascular:          {response_data.get('organosysis_cardiovascular', 'N/A')}"
                    organosysis_hemolinf = f"Hemolinf.:                   {response_data.get('organosysis_hemolinf', 'N/A')}"
                    organosysis_orgsentidos = f"Org. Sentidos:       {response_data.get('organosysis_orgsentidos', 'N/A')}"

                    coordinates = {
                        'G3': cedula,
                        'B9': 'Edad:  ' + response_data.get('Edad', 'N/A'),
                        'C9': 'Sexo:  ' + response_data.get('Sexo', 'N/A'),

                        'E9': response_data.get('Cargo', 'N/A'),
                        'G9': response_data.get('Tiempo_cargo', 'N/A'),
                        'C7': response_data.get('Nombre_colaborador', 'N/A'),
                        'B18': response_data.get('antecep_clinicos', 'N/A'),
                                            
                        'C24': response_data.get('act_fisica', 'N/A')+ cual,
                        'D24': response_data.get('act_fisica_obser', 'N/A'),
                        'C26': response_data.get('medi_actual', 'N/A')+ cual,
                        'D26': response_data.get('medi_actual_obser', 'N/A'),
                        'C28': response_data.get('alcohol', 'N/A')+ cual,
                        'D28': response_data.get('alcohol_obser', 'N/A'),
                        'C30': response_data.get('tabaco', 'N/A')+ cual,
                        'D30': response_data.get('tabaco_obser', 'N/A'),
                        'C32': response_data.get('otros', 'N/A')+ cual,
                        'D32': response_data.get('otros_obser', 'N/A'),

    
                        'C36': response_data.get('incidente_trabajo', 'N/A'),
                        'C38': response_data.get('accidente_trabajo_calif', 'N/A'),
                        'G38': response_data.get('accidente_trabajo_fecha', 'N/A'),
                        'C40': response_data.get('enfermedad_prof_calif', 'N/A'),
                        'F40': enfermedad_prof,
                        'F38': accidente_trabajo,
                        'G40': response_data.get('enfermedad_prof_fecha', 'N/A'),


                        'B44': antecf_cardio_vas,
                        'C44': antecf_metabotica,
                        'D44': antecf_neurologica,
                        'E44': antecf_oncologica,
                        'F44': antecf_infecciosa,
                        'G44': antecf_hereditario,
                        'B47': response_data.get('antecf_observacion', 'N/A'),

                        'C51': response_data.get('fact_risg_trabajo_ruido', 'N/A'),
                        'C52': response_data.get('fact_risg_trabajo_iluminacion', 'N/A'),
                        'C53': response_data.get('fact_risg_trabajo_ventilacion', 'N/A'),
                        'C54': response_data.get('fact_risg_trabajo_caidas_mismonivel', 'N/A'),
                        'C55': response_data.get('fact_risg_trabajo_atropellamiento_vehi', 'N/A'),
                        'C56': response_data.get('fact_risg_trabajo_caidas_desnivel', 'N/A'),
                        'E51': response_data.get('fact_risg_trabajo_polvos', 'N/A'),
                        'E52': response_data.get('fact_risg_trabajo_liquidos', 'N/A'),
                        'E53': response_data.get('fact_risg_trabajo_virus', 'N/A'),
                        'E54': response_data.get('fact_risg_trabajo_posturas', 'N/A'),
                        'E55': response_data.get('fact_risg_trabajo_mov_repetitivo', 'N/A'),
                        'E56': response_data.get('fact_risg_trabajo_monotomia', 'N/A'),
                        'G51': response_data.get('fact_risg_trabajo_alta_respo', 'N/A'),
                        'G52': response_data.get('fact_risg_trabajo_conflic_rol', 'N/A'),
                        'G53': response_data.get('fact_risg_trabajo_sobrecarga_lab', 'N/A'),
                        'G54': response_data.get('fact_risg_trabajo_inestabilidad_lab', 'N/A'),
                        'G55': response_data.get('fact_risg_trabajo_rela_interp', 'N/A'),

                        'D58': response_data.get('sso_salud_mental', 'N/A'),
                        'D59': response_data.get('sso_riesgo_lab', 'N/A'),
                        'D60': response_data.get('sso_pausas_activas', 'N/A'),

                        'C62': inmuni_influenza,
                        'D62': inmuni_tetano,
                        'E62': inmuni_hepatitisB,
                        'F62': inmuni_coviddosis,
                        
                        'B65': organosysis_piel_anexo,
                        'B66': organosysis_genito_urinario,
                        'C65': organosysis_respiratorio,
                        'C66': organosysis_endocrino,
                        'D65': organosysis_digestivo,
                        'D66': organosysis_nervioso,
                        'E65': organosysis_musculo_esqueletico,
                        'E66': organosysis_cardiovascular,
                        'F65': organosysis_hemolinf,
                        'G65': organosysis_orgsentidos,
                        

                        'B69': response_data.get('organosysis_descripcion', 'N/A'),
                        'B77': response_data.get('examn_fis_cabeza', 'N/A'),
                        'E77': response_data.get('examn_fis_extremidades', 'N/A'),
                        
                        'C82': response_data.get('examn_fis_garganta', 'N/A'),
                        'C83': response_data.get('examn_fis_ojos', 'N/A'),
                        'C84': response_data.get('examn_fis_oidos', 'N/A'),
                        'C85': response_data.get('examn_fis_nariz', 'N/A'),
                        'C86': response_data.get('examn_fis_boca', 'N/A'),
                        'C87': response_data.get('examn_fis_dentudura', 'N/A'),

                        'C89': response_data.get('examn_fis_corazon', 'N/A'),
                        'C90': response_data.get('examn_fis_pulmones', 'N/A'),

                        'C92': response_data.get('examn_fis_inspeccion', 'N/A'),
                        'C93': response_data.get('examn_fis_palpacion', 'N/A'),
                        'C94': response_data.get('examn_fis_percsusion', 'N/A'),

                        'E82': response_data.get('examn_fis_umbilical', 'N/A'),
                        'E83': response_data.get('examn_fis_ingual_dere', 'N/A'),
                        'E84': response_data.get('examn_fis_clural_dere', 'N/A'),
                        'E85': response_data.get('examn_fis_inguinal_izquierdo', 'N/A'),
                        'E86': response_data.get('examn_fis_clural_izq', 'N/A'),
                        
                        'E88': response_data.get('examn_fis_deformaciones', 'N/A'),
                        'E89': response_data.get('examn_fis_movilidad', 'N/A'),
                        'E90': response_data.get('examn_fis_masas_musculares', 'N/A'),
                        
                        'E92': response_data.get('examn_fis_tracto_urinario', 'N/A'),
                        'E93': response_data.get('examn_fis_tracto_genital', 'N/A'),
                        'E94': response_data.get('examn_fis_regio_anoperineal', 'N/A'),

                        'G82': response_data.get('examn_fis_sup_izquierda', 'N/A'),
                        'G83': response_data.get('examn_fis_infer_dere', 'N/A'),
                        'G84': response_data.get('examn_fis_infer_izquierda', 'N/A'),
                        
                        'G86': response_data.get('examn_fis_reflejos_tndinosos', 'N/A'),
                        'G87': response_data.get('examn_fis_sencibilidad_sup', 'N/A'),
                        'G88': response_data.get('examn_fis_reflejos_pupilares', 'N/A'),

                        'G90': response_data.get('examn_fis_ojo_derecho', 'N/A'),
                        'G91': response_data.get('examn_fis_ojo_izquierdo', 'N/A'),

                        'G93': response_data.get('examn_fis_oido_derecho', 'N/A'),
                        'G94': response_data.get('examn_fis_oido_izquierdo', 'N/A'),


                        'B97': response_data.get('examn_fis_descripcion', 'N/A'),
        
                        
                        'C101': response_data.get('laboratorio', 'N/A'),
                        'C102': response_data.get('rx', 'N/A'),
                        'C103': response_data.get('audiometria', 'N/A'),
                        'C104': response_data.get('optometria', 'N/A'),
                        'C105': response_data.get('ekg', 'N/A'),
                        
                        'B108': response_data.get('diagnostico_1', 'N/A'),
                        'B109': response_data.get('diagnostico_2', 'N/A'),
                        'B110': response_data.get('diagnostico_3', 'N/A'),
                        'B111': response_data.get('diagnostico_4', 'N/A'),
                        'E108': response_data.get('cie10_1', 'N/A'),
                        'E109': response_data.get('cie10_2', 'N/A'),
                        'E110': response_data.get('cie10_3', 'N/A'),
                        'E111': response_data.get('cie10_4', 'N/A'),
                        
                        'C117': response_data.get('aptitud', 'N/A'),
                        'C119': response_data.get('aptitud_observ', 'N/A'),
                        'C121': response_data.get('aptitud_limitacion', 'N/A'),
                        
                        'B124': response_data.get('recomendaciones_tto', 'N/A'),
                        
                        'F128': response_data.get('fecha', 'N/A'),
                        #'C128': response_data.get('Usuario_actualizacion', 'N/A'),

                    }
                    # Cargar el archivo Excel existente
                    file_path = os.path.join(os.path.dirname(__file__), '..','..','static', 'files', 'FICHA_OCUPACIONAL.xlsx')

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb['Sheet1']  

                    # Escribir datos en las celdas según el diccionario de coordenadas
                    for cell, value in coordinates.items():
                        ws[cell] = value

                    # Procesar y redimensionar firma del colaborador
                    firma_colaborador = response_data.get('firma_colaborador', '')
                    if firma_colaborador:
                        if firma_colaborador.startswith('data:image/png;base64,'):
                            firma_colaborador = firma_colaborador.split(',')[1]
                        if len(firma_colaborador) % 4:
                            firma_colaborador += '=' * (4 - len(firma_colaborador) % 4)

                        try:
                            print('Procesando firma del colaborador...')
                            data_sign = resize_image_base64(firma_colaborador, 250, 150)  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            tempxlsx1 = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'files', 'FICHA_OCUPACIONALTEMP.png')

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx1, 'wb') as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_colaborador = ExcelImage(tempxlsx1)
                            ws.add_image(img_colaborador, 'F130')  # Ajusta la posición según sea necesario
                            print('Firma del colaborador añadida.')

                        except (base64.binascii.Error, ValueError) as e:
                            print(f'Error al procesar la firma del colaborador: {e}')

                    # Procesar y redimensionar firma del doctor (similar al colaborador)
                    firma_doctor = base_firma_doc
                    if firma_doctor:
                        if firma_doctor.startswith('data:image/png;base64,'):
                            firma_doctor = firma_doctor.split(',')[1]
                        if len(firma_doctor) % 4:
                            firma_doctor += '=' * (4 - len(firma_doctor) % 4)

                        try:
                            print('Procesando firma del doctor...')
                            data_sign = resize_image_base64(firma_doctor, 250, 150)  # Redimensionar a 200x100
                            REDUCED_SIGN = base64.b64decode(data_sign)

                            # Guardar la firma redimensionada temporalmente
                            tempxlsx2 = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'files', 'FICHA_OCUPACIONALTEMP2.png')

                            # Guardar la firma redimensionada temporalmente
                            with open(tempxlsx2, 'wb') as f:
                                f.write(REDUCED_SIGN)

                            # Insertar la firma en el archivo Excel
                            img_doctor = ExcelImage(tempxlsx2)
                            ws.add_image(img_doctor, 'C130')  # Ajusta la posición según sea necesario
                            print('Firma del doctor añadida.')

                        except (base64.binascii.Error, ValueError) as e:
                            print(f'Error al procesar la firma del doctor: {e}')


                    # Guardar el archivo Excel modificado en un buffer temporal
                    output = BytesIO()
                    wb.save(output)
                    output.seek(0)
                        
                    # Enviar el archivo Excel como respuesta para descarga
                    return send_file(output, as_attachment=True, download_name=f'FICHA_OCUPACIONAL_{cedula}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                else:
                    print(response.status_code)
                    flash("Error en la respuesta de la API: " + response.text, 'error')
                    print("Error en la respuesta de la API: " + response.text)
                    return render_template('dashboard/dashboard_ocupacional.html', errores={}, form_data=form_data)

            except requests.exceptions.RequestException as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: Request, {e}')
                return render_template('dashboard/dashboard_ocupacional.html', errores={}, form_data=form_data)

            except Exception as e:
                flash(f'Ocurrió un error al procesar el formulario: {e}', 'error')
                print(f'Error: EXCEL,  {e}')
                return render_template('dashboard/dashboard_ocupacional.html', errores={}, form_data=form_data)

        return render_template('dashboard/dashboard_ocupacional.html')

