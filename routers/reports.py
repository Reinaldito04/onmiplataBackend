from fastapi import APIRouter, HTTPException
from models.Rentals import Rentals, ContractDetails,ReportData,notificacionInquilino,ReporteNotificacion,CrearInquilinoReporte,EntregaInmueble,ContratoInquilino
import os
from reports.Contrato import generar_reporte
from pydantic import ValidationError
from typing import List
from datetime import datetime,timedelta
from db.db import create_connection
from reports.Notificacionvehicular import generar_reporte as generarNotificacionVehicular
from reports.PagosContrato import ContratoInquilinoExcel
router = APIRouter()



@router.post("/report-pays")
def generarReport(contrato: ContratoInquilino):
    try:
        # Crear instancia de la clase de Excel
        contrato_excel = ContratoInquilinoExcel("contrato_inquilino.xlsx")
        
        # Configurar datos del contrato desde el body de la solicitud
        contrato_excel.set_datos_inquilino({
            "INQUILINO": contrato.INQUILINO,
            "N° CONTACTO": contrato.N_CONTACTO,
            "CORREO": contrato.CORREO,
            "INMUEBLE": contrato.INMUEBLE,
            "FECHA DE CONTRATO": contrato.FECHA_CONTRATO,
            "CANON": contrato.CANON,
            "DEPOSITO EN GARANTIA": contrato.DEPOSITO_EN_GARANTIA
        })
        contrato_excel.set_canones_mensuales(contrato.CANONES_MENSUALES)
        contrato_excel.set_total_contrato(contrato.TOTAL_CONTRATO)
        contrato_excel.set_depositos_efectuados(contrato.DEPOSITOS_EFECTUADOS)
        contrato_excel.set_total_depositado(contrato.TOTAL_DEPOSITADO)
        
        # Ruta base para guardar los reportes
        output_base_path = 'reports/output'
        
        # Generar el nombre del archivo basado en la fecha y hora actual 
        # Generar el archivo Excel en la ruta especificada
       
        nombre_archivo_output_path = contrato_excel.write_to_excel(output_path=output_base_path)
        nombre_archivo = nombre_archivo_output_path["nombre_archivo"]
        output_path = nombre_archivo_output_path["output_path"]
                
        # Devolver un mensaje de éxito con el nombre del archivo creado
        return {"message": f"Archivo '{nombre_archivo}' creado exitosamente en '{output_path}'."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")



@router.post("/inmueble-entrega")
def entrega_inmueble(inmueble : EntregaInmueble):
    try:
        template_path = 'reports/documents/EntregaInmueble.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generarNotificacionVehicular(template_path=template_path, output_base_path=output_base_path, variables=inmueble.model_dump(),tipo="Entrega Inmueble")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)
@router.post("/generate-inquilinoreporte")
def generate_inquilino(inquilino : CrearInquilinoReporte):
    try:
        template_path = 'reports/documents/DatosInquilinos.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generarNotificacionVehicular(template_path=template_path, output_base_path=output_base_path, variables=inquilino.model_dump(),tipo="Registro de Inquilino")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

@router.post("/generate-notificacionVehicular")
def generate_vehicular(vehicular : ReporteNotificacion):
    try:
        # Validar los datos recibidos antes de continuar
        

        template_path = 'reports/documents/plantillanotificacion.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generarNotificacionVehicular(template_path=template_path, output_base_path=output_base_path, variables=vehicular.model_dump(),tipo="Notificacion Vehicular")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)
@router.post("/generate-notificacionInquilino")
def generate_inquilino(notificacion: notificacionInquilino):
    try:
        # Validar los datos recibidos antes de continuar
        

        template_path = 'reports/documents/plantillaInquilino.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generar_reporte(template_path=template_path, output_base_path=output_base_path, variables=notificacion.model_dump(),tipo="Notificacion")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except ValidationError as validation_error:
        # Capturar errores de validación de Pydantic (por ejemplo, campos faltantes o incorrectos)
        raise HTTPException(status_code=422, detail=f"Error de validación de datos: {str(validation_error)}")
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/generate-contratReport")
def generate_report(report_data: ReportData):
    try:
        # Validar los datos recibidos antes de continuar
        validate_report_data(report_data)

        template_path = 'reports/documents/contratoplantilla.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generar_reporte(template_path, output_base_path, report_data.model_dump(),"reporte")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except ValidationError as validation_error:
        # Capturar errores de validación de Pydantic (por ejemplo, campos faltantes o incorrectos)
        raise HTTPException(status_code=422, detail=f"Error de validación de datos: {str(validation_error)}")
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

def validate_report_data(report_data: ReportData):
    # Validar que todos los campos obligatorios estén presentes y en el formato correcto
    if not report_data.fecha:
        raise HTTPException(status_code=422, detail="Falta la fecha en los datos del reporte")
    
    if not report_data.nombre:
        raise HTTPException(status_code=422, detail="Falta el nombre en los datos del reporte")
    
    if not report_data.inmueble:
        raise HTTPException(status_code=422, detail="Falta el inmueble en los datos del reporte")
    
    if not report_data.municipio:
        raise HTTPException(status_code=422, detail="Falta el municipio en los datos del reporte")
    
    if not report_data.motivo:
        raise HTTPException(status_code=422, detail="Falta el motivo en los datos del reporte")
    
    if not report_data.fechaInicio:
        raise HTTPException(status_code=422, detail="Falta la fecha de inicio en los datos del reporte")
    else:
        try:
            # Validar que la fecha de inicio esté en el formato correcto (YYYY-MM-DD)
            datetime.strptime(report_data.fechaInicio, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato incorrecto para la fecha de inicio. Debe ser YYYY-MM-DD")
    
    if not report_data.fechaFin:
        raise HTTPException(status_code=422, detail="Falta la fecha de fin en los datos del reporte")
    else:
        try:
            # Validar que la fecha de fin esté en el formato correcto (YYYY-MM-DD)
            datetime.strptime(report_data.fechaFin, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato incorrecto para la fecha de fin. Debe ser YYYY-MM-DD")
    
    if not report_data.duracionMeses:
        raise HTTPException(status_code=422, detail="Falta la duración en meses en los datos del reporte")
    else:
        try:
            # Validar que la duración en meses sea un número entero positivo
            duracion_meses = int(report_data.duracionMeses)
            if duracion_meses <= 0:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="La duración en meses debe ser un número entero positivo")
    
    if not report_data.monto:
        raise HTTPException(status_code=422, detail="Falta el monto en los datos del reporte")
    else:
        try:
            # Validar que el monto sea un número decimal positivo
            monto = float(report_data.monto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="El monto debe ser un número decimal positivo")
        